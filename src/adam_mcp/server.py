"""
adam-mcp: FreeCAD MCP Server

IMPORTANT: FreeCAD environment must be configured before importing FreeCAD modules.
This is done via setup_freecad_environment() which configures Python paths and
environment variables for FreeCAD's dynamic libraries.

Pattern:
    1. Call setup_freecad_environment() ONCE at startup
    2. Import FreeCAD modules
    3. Define and run server
"""

from fastmcp import FastMCP

from adam_mcp.constants import SERVER_NAME
from adam_mcp.freecad_env import setup_freecad_environment
from adam_mcp.models import DocumentInfo, HealthCheckResponse, ProjectsList

# ============================================================================
# FreeCAD Environment Setup (MUST be first)
# ============================================================================

setup_freecad_environment()

# Now FreeCAD imports will work

# Import tool implementations after FreeCAD is initialized
from adam_mcp.tools.document import (  # noqa: E402
    commit_changes,
    create_document,
    get_document_info,
    health_check,
    list_projects,
    open_document,
    open_in_freecad_gui,
    rollback_working_changes,
)

# ============================================================================
# FastMCP Server
# ============================================================================

mcp = FastMCP(SERVER_NAME)


# ============================================================================
# Tool Registration
# ============================================================================


@mcp.tool()
def health_check_tool() -> HealthCheckResponse:
    """
    Check server health and FreeCAD integration status.

    Returns health information including FreeCAD version and active document status.
    Use this to verify the server is running correctly.
    """
    return health_check()


@mcp.tool()
def open_document_tool(path: str) -> DocumentInfo:
    """
    Open existing FreeCAD document for editing.

    RESUME BY DEFAULT: If you've previously edited this file, your uncommitted changes
    in the .work file are preserved and you continue where you left off. The .work file
    is only created from the main file if it doesn't exist yet.

    All edits happen on the working file (.work), which is auto-saved every 5 operations.
    The main file is ONLY modified when you call commit_changes(). Use rollback_working_changes()
    to discard uncommitted changes and reset from the main file.

    Args:
        path: Path to existing .FCStd file

    Returns:
        Information about the opened document

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If file can't be opened
    """
    return open_document(path)


@mcp.tool()
def create_document_tool(path: str) -> DocumentInfo:
    """
    Create new FreeCAD document and save to path.

    RESUME BY DEFAULT: If a .work file already exists at this path, it will be opened
    instead of creating a new document. This allows you to continue editing where you
    left off. To start fresh, use rollback_working_changes() first.

    Creates both the main file (.FCStd) and working file (.work). The main file is
    saved with the initial blank state. All subsequent edits happen on the working
    file, which is auto-saved every 5 operations. Use commit_changes() to update
    the main file.

    Args:
        path: Path where document will be saved (e.g., ~/designs/bracket.FCStd)

    Returns:
        Information about the created document

    Raises:
        RuntimeError: If document can't be created or saved
    """
    return create_document(path)


@mcp.tool()
def commit_changes_tool() -> str:
    """
    Commit working file changes to main file.

    This is the ONLY way the main file gets updated. Validates the document before
    committing to ensure geometry is not corrupted. If validation fails, commit is
    rejected and you must fix errors or use rollback_working_changes().

    Returns:
        Success message with path to main file

    Raises:
        RuntimeError: If no document open or validation fails
    """
    return commit_changes()


@mcp.tool()
def rollback_working_changes_tool() -> str:
    """
    Discard all working changes and reset from main file.

    Reloads the main file state, discarding all uncommitted work. Use this if you
    mess up and want to start over from the last commit. This is a destructive
    operation - all changes since last commit will be lost.

    Returns:
        Success message with path to main file

    Raises:
        RuntimeError: If no document open
    """
    return rollback_working_changes()


@mcp.tool()
def get_document_info_tool() -> DocumentInfo:
    """
    Get information about the active document.

    Returns object count and list of objects in the current document.

    Raises:
        RuntimeError: If no active document exists
    """
    return get_document_info()


@mcp.tool()
def open_in_freecad_gui_tool() -> str:
    """
    Open the working file in FreeCAD GUI for live preview.

    Opens the active .work file in the FreeCAD desktop application so you can see
    your changes in real-time as the MCP server modifies the file. The GUI will
    show the current state of the working file (auto-saved every 5 operations).

    To see updates, you may need to reload the document in the FreeCAD GUI (File > Reload).

    Returns:
        Success message with path to working file

    Raises:
        RuntimeError: If no document is open or FreeCAD app can't be found
    """
    return open_in_freecad_gui()


@mcp.tool()
def list_projects_tool(directory: str | None = None) -> ProjectsList:
    """
    List FreeCAD projects in a directory.

    Searches for .FCStd files and returns information about each project including
    file size, last modified time, and whether it has uncommitted changes (working file).
    Results are sorted by most recently modified first.

    Args:
        directory: Optional directory path to search. If not provided, searches the
                   default projects directory (~/freecad_projects)

    Returns:
        List of projects with metadata (name, path, size, modified time, working file status)

    Raises:
        RuntimeError: If directory doesn't exist or can't be read
    """
    return list_projects(directory)


# ============================================================================
# Entry Point
# ============================================================================


def main() -> None:
    """
    Main entry point for the MCP server.

    Starts the FastMCP server and runs indefinitely until terminated.
    """
    mcp.run()


if __name__ == "__main__":
    main()
