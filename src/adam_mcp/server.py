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

import os
import shutil
import tempfile
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from adam_mcp.freecad_env import setup_freecad_environment

# ============================================================================
# FreeCAD Environment Setup (MUST be first)
# ============================================================================

setup_freecad_environment()

# Now FreeCAD imports will work
import FreeCAD  # noqa: E402

# ============================================================================
# Constants
# ============================================================================

# Server metadata
SERVER_NAME = "adam-mcp"
SERVER_VERSION = "0.1.0"

# Document defaults
DEFAULT_DOCUMENT_NAME = "CAD_Design"
DEFAULT_SKETCH_NAME = "Sketch"
MAX_DOCUMENT_NAME_LENGTH = 100

# Dimension constraints (mm)
MIN_DIMENSION_MM = 0.1
MAX_DIMENSION_MM = 10000.0
MIN_FILLET_RADIUS_MM = 0.1
MAX_FILLET_RADIUS_MM = 1000.0

# Angular constraints (degrees)
MIN_ANGLE_DEGREES = -360.0
MAX_ANGLE_DEGREES = 360.0

# Working file configuration
AUTO_SAVE_INTERVAL = 5  # Save working file every N operations
WORK_FILE_SUFFIX = ".work"  # Extension for working files
VALIDATE_BEFORE_COMMIT = True  # Safety gate for commits
WORK_DIR_ENV_VAR = "ADAM_MCP_WORK_DIR"  # Environment variable for custom work directory

# Error message templates
ERROR_NO_ACTIVE_DOC = "No active FreeCAD document. Open or create a document first."
ERROR_NO_OPEN_DOC = "No document open. Use open_document() or create_document() first."
ERROR_FREECAD_API = "FreeCAD API error: {error}. {suggestion}"
ERROR_INVALID_DIMENSION = "Dimension {value} mm is outside valid range ({min_val}-{max_val} mm)"
ERROR_INVALID_OBJECT = "Object '{name}' not found in active document"
ERROR_FILE_NOT_FOUND = "File not found: {path}"
ERROR_VALIDATION_FAILED = (
    "Document validation failed. Cannot commit corrupted state. "
    "Fix errors or use rollback_working_changes() to discard changes."
)

# Success message templates
SUCCESS_DOC_CREATED = "Created document: {name}"
SUCCESS_DOC_OPENED = "Opened document: {name}"
SUCCESS_OPERATION = "Operation completed successfully"
SUCCESS_CHANGES_COMMITTED = "Changes committed to {path}"
SUCCESS_CHANGES_ROLLED_BACK = "Working changes discarded. Reset to last commit: {path}"

# ============================================================================
# Pydantic Models (Type-safe parameters)
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    status: str = Field(description="Server status")
    freecad_version: str = Field(description="FreeCAD version")
    active_document: str | None = Field(description="Name of active document, if any")
    message: str = Field(description="Human-readable status message")


class DocumentInfo(BaseModel):
    """Document information response"""

    name: str = Field(description="Document name")
    object_count: int = Field(ge=0, description="Number of objects in document")
    objects: list[str] = Field(description="List of object names")


# ============================================================================
# Global State (Working File Management)
# ============================================================================

_active_main_file_path: str | None = None
_active_work_file_path: str | None = None
_operation_counter: int = 0

# ============================================================================
# Utility Functions
# ============================================================================


def get_freecad_version() -> str:
    """
    Get FreeCAD version string

    Returns:
        Version string (e.g., "1.0.2")
    """
    version_parts = FreeCAD.Version()[:3]
    return ".".join(version_parts)


def get_active_document() -> "FreeCAD.Document":
    """
    Get active FreeCAD document

    Returns:
        Active document object

    Raises:
        RuntimeError: If no active document exists
    """
    doc = FreeCAD.ActiveDocument
    if doc is None:
        raise RuntimeError(ERROR_NO_ACTIVE_DOC)
    return doc


def format_freecad_error(error: Exception, suggestion: str = "") -> str:
    """
    Format FreeCAD API error into user-friendly message

    Args:
        error: Original exception
        suggestion: Optional suggestion for how to fix

    Returns:
        Formatted error message
    """
    if not suggestion:
        suggestion = "Check FreeCAD documentation for valid parameters."
    return ERROR_FREECAD_API.format(error=str(error), suggestion=suggestion)


def validate_dimension(value: float, param_name: str) -> None:
    """
    Validate dimension is within acceptable range

    Args:
        value: Dimension value in mm
        param_name: Parameter name for error message

    Raises:
        ValueError: If dimension is outside valid range
    """
    if not (MIN_DIMENSION_MM <= value <= MAX_DIMENSION_MM):
        raise ValueError(
            ERROR_INVALID_DIMENSION.format(
                value=value, min_val=MIN_DIMENSION_MM, max_val=MAX_DIMENSION_MM
            )
            + f" (parameter: {param_name})"
        )


# ============================================================================
# Working File Infrastructure
# ============================================================================


def get_work_file_path(main_file_path: str) -> str:
    """
    Determine working file path from main file path

    Args:
        main_file_path: Path to main .FCStd file

    Returns:
        Path to working file

    Uses environment variable ADAM_MCP_WORK_DIR if set, otherwise
    places working file in same directory as main file.
    """
    main_path = Path(main_file_path).resolve()

    # Check for custom work directory
    work_dir_str = os.environ.get(WORK_DIR_ENV_VAR)

    if work_dir_str:
        # Use ternary operator for temp directory selection
        work_dir: Path = (
            Path(tempfile.gettempdir()) / "adam_mcp_work"
            if work_dir_str == "temp"
            else Path(work_dir_str)
        )

        # Create work directory if needed
        work_dir.mkdir(parents=True, exist_ok=True)

        # Use main file's name in work directory
        work_file_name = main_path.stem + WORK_FILE_SUFFIX
        return str(work_dir / work_file_name)

    # Default: same directory as main file
    return str(main_path.parent / (main_path.name + WORK_FILE_SUFFIX))


def setup_working_file(main_file_path: str) -> str:
    """
    Setup working file from main file

    Args:
        main_file_path: Path to main .FCStd file

    Returns:
        Path to working file

    If main file exists, copies it to working file.
    If main file doesn't exist, working file will be created when document is saved.
    """
    work_file_path = get_work_file_path(main_file_path)

    # Copy main → work if main exists
    if Path(main_file_path).exists():
        shutil.copy2(main_file_path, work_file_path)

    return work_file_path


def auto_save_working_file() -> None:
    """
    Auto-save working file (called after operations)

    Saves the active document to the working file path.
    Silent fail if no active document or no working file configured.
    """
    global _active_work_file_path

    doc = FreeCAD.ActiveDocument
    if doc and _active_work_file_path:
        try:
            doc.save()
        except (RuntimeError, OSError) as e:
            # Log but don't crash - auto-save is best-effort
            print(f"Warning: Auto-save failed: {e}")


def increment_operation_counter() -> None:
    """
    Track operations and trigger auto-save

    Increments operation counter and triggers auto-save
    every AUTO_SAVE_INTERVAL operations.
    """
    global _operation_counter

    _operation_counter += 1

    if _operation_counter % AUTO_SAVE_INTERVAL == 0:
        auto_save_working_file()


def auto_save_after(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator: auto-save working file after tool execution

    Wraps a tool function to automatically increment the operation
    counter and trigger auto-save after successful execution.

    Args:
        func: Tool function to wrap

    Returns:
        Wrapped function with auto-save behavior
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        increment_operation_counter()
        return result

    return wrapper


def validate_document(doc: "FreeCAD.Document") -> bool:
    """
    Validate document is in good state before committing

    Checks for common error conditions that indicate corrupted geometry:
    - Document recomputes successfully
    - Document has objects (not empty)
    - No invalid objects or broken references
    - All shapes are geometrically valid

    Args:
        doc: FreeCAD document to validate

    Returns:
        True if document is valid, False otherwise
    """
    try:
        # Recompute should succeed
        doc.recompute()

        # Should have objects
        if len(doc.Objects) == 0:
            print("Validation: Document is empty")
            return False

        # Check each object
        for obj in doc.Objects:
            # Check object state
            if hasattr(obj, "State") and "Invalid" in str(obj.State):
                print(f"Validation: Object {obj.Name} has invalid state: {obj.State}")
                return False

            # Check shape validity
            if hasattr(obj, "Shape") and obj.Shape and not obj.Shape.isValid():
                print(f"Validation: Object {obj.Name} has invalid shape")
                return False

        return True

    except Exception as e:
        print(f"Validation error: {e}")
        return False


# ============================================================================
# FastMCP Server
# ============================================================================

mcp = FastMCP(SERVER_NAME)


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
def health_check() -> HealthCheckResponse:
    """
    Check server health and FreeCAD integration status.

    Returns health information including FreeCAD version and active document status.
    Use this to verify the server is running correctly.
    """
    try:
        version = get_freecad_version()
        active_doc = FreeCAD.ActiveDocument
        doc_name = active_doc.Name if active_doc else None

        return HealthCheckResponse(
            status="healthy",
            freecad_version=version,
            active_document=doc_name,
            message=f"Server running. FreeCAD {version} integrated successfully.",
        )
    except (AttributeError, RuntimeError, ImportError) as e:
        return HealthCheckResponse(
            status="error",
            freecad_version="unknown",
            active_document=None,
            message=f"Health check failed: {str(e)}",
        )


@mcp.tool()
def open_document(path: str = Field(description="Path to .FCStd file to open")) -> DocumentInfo:
    """
    Open existing FreeCAD document for editing.

    Creates a working copy (.work file) for safe editing. The main file is only
    modified when you call commit_changes(). All edits happen on the working file,
    which is auto-saved every 5 operations for crash protection.

    Args:
        path: Path to existing .FCStd file

    Returns:
        Information about the opened document

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If file can't be opened
    """
    global _active_main_file_path, _active_work_file_path, _operation_counter

    # Expand user path (~/)
    main_file_path = str(Path(path).expanduser().resolve())

    # Validate main file exists
    if not Path(main_file_path).exists():
        raise FileNotFoundError(ERROR_FILE_NOT_FOUND.format(path=main_file_path))

    try:
        # Setup working file (copies main → work)
        _active_main_file_path = main_file_path
        _active_work_file_path = setup_working_file(main_file_path)
        _operation_counter = 0

        # Close any existing documents
        if FreeCAD.ActiveDocument:
            FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)

        # Open working file in FreeCAD
        doc = FreeCAD.open(_active_work_file_path)

        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )

    except (RuntimeError, OSError) as e:
        raise RuntimeError(
            format_freecad_error(e, f"Ensure file is a valid FreeCAD document: {main_file_path}")
        ) from e


@mcp.tool()
def create_document(
    path: str = Field(description="Path where new .FCStd file will be saved"),
) -> DocumentInfo:
    """
    Create new FreeCAD document and save to path.

    Creates both the main file and working file. The main file is saved with the
    initial blank state. All subsequent edits happen on the working file, which is
    auto-saved every 5 operations. Use commit_changes() to update the main file.

    Args:
        path: Path where document will be saved (e.g., ~/designs/bracket.FCStd)

    Returns:
        Information about the created document

    Raises:
        RuntimeError: If document can't be created or saved
    """
    global _active_main_file_path, _active_work_file_path, _operation_counter

    # Expand user path (~/)
    main_file_path = str(Path(path).expanduser().resolve())

    # Ensure parent directory exists
    Path(main_file_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Close any existing documents
        if FreeCAD.ActiveDocument:
            FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)

        # Create new document
        doc = FreeCAD.newDocument()

        # Save as main file (initial blank state)
        doc.saveAs(main_file_path)
        _active_main_file_path = main_file_path

        # Setup working file (copies main → work)
        _active_work_file_path = setup_working_file(main_file_path)
        doc.saveAs(_active_work_file_path)
        _operation_counter = 0

        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )

    except (RuntimeError, OSError) as e:
        raise RuntimeError(
            format_freecad_error(e, f"Ensure path is writable: {main_file_path}")
        ) from e


@mcp.tool()
def commit_changes() -> str:
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
    global _active_main_file_path, _active_work_file_path

    if not _active_main_file_path or not _active_work_file_path:
        raise RuntimeError(ERROR_NO_OPEN_DOC)

    doc = get_active_document()

    # Validate before committing (critical safety check)
    if VALIDATE_BEFORE_COMMIT and not validate_document(doc):
        raise RuntimeError(ERROR_VALIDATION_FAILED)

    try:
        # Save work file one more time
        doc.save()

        # Copy work → main (atomic commit)
        shutil.copy2(_active_work_file_path, _active_main_file_path)

        return SUCCESS_CHANGES_COMMITTED.format(path=_active_main_file_path)

    except (OSError, RuntimeError) as e:
        raise RuntimeError(
            format_freecad_error(e, "Check that main file is not open in another application.")
        ) from e


@mcp.tool()
def rollback_working_changes() -> str:
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
    global _active_main_file_path, _active_work_file_path, _operation_counter

    if not _active_main_file_path or not _active_work_file_path:
        raise RuntimeError(ERROR_NO_OPEN_DOC)

    try:
        # Close current working document
        doc = get_active_document()
        doc_name = doc.Name
        FreeCAD.closeDocument(doc_name)

        # Copy main → work (reset)
        shutil.copy2(_active_main_file_path, _active_work_file_path)

        # Reopen work file
        FreeCAD.open(_active_work_file_path)
        _operation_counter = 0

        return SUCCESS_CHANGES_ROLLED_BACK.format(path=_active_main_file_path)

    except (OSError, RuntimeError) as e:
        raise RuntimeError(format_freecad_error(e, "Failed to rollback changes.")) from e


@mcp.tool()
def get_document_info() -> DocumentInfo:
    """
    Get information about the active document.

    Returns object count and list of objects in the current document.

    Raises:
        RuntimeError: If no active document exists
    """
    try:
        doc = get_active_document()
        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )
    except RuntimeError:
        raise
    except AttributeError as e:
        raise RuntimeError(format_freecad_error(e)) from e


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
