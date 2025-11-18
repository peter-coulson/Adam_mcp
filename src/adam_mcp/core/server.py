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

from adam_mcp.constants.operations import SERVER_NAME
from adam_mcp.core.freecad_env import setup_freecad_environment
from adam_mcp.models.responses import (
    DocumentInfo,
    HealthCheckResponse,
    ObjectDetailsResponse,
    ObjectListResponse,
    OperationResult,
    ProjectsList,
)

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
from adam_mcp.tools.execution import (  # noqa: E402
    add_sketch_circle,
    create_cylinder,
    create_sketch,
)
from adam_mcp.tools.query import (  # noqa: E402
    get_object_details,
    list_objects,
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


@mcp.tool()
def list_objects_tool() -> ObjectListResponse:
    """
    List all objects in the active document.

    Returns lightweight overview with object names, types, and dependencies.
    Use this for quick inspection before operations. Token-efficient - only
    returns names and types, not full properties.

    For detailed properties of specific objects, use get_object_details_tool().

    Returns:
        List of object summaries with dependency information

    Raises:
        RuntimeError: If no active document exists
    """
    return list_objects()


@mcp.tool()
def get_object_details_tool(names: list[str]) -> ObjectDetailsResponse:
    """
    Get detailed information for specific objects.

    Fetches rich context including all properties, values, and bidirectional
    dependencies. Use this on-demand after list_objects_tool() to get details
    for specific objects of interest.

    Token-efficient pattern: list all objects (cheap) → filter what you need →
    get details for those specific objects (expensive).

    Args:
        names: List of object names to fetch details for

    Returns:
        Detailed information for found objects, plus list of not found names

    Raises:
        RuntimeError: If no active document exists
    """
    return get_object_details(names)


@mcp.tool()
def create_cylinder_tool(
    name: str,
    radius: float,
    height: float,
    description: str,
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    angle: float = 360.0,
) -> OperationResult:
    """
    Create a cylindrical primitive.

    Creates a cylinder with specified dimensions. All parameters are validated
    before execution using 3-layer validation:
    1. Pydantic validation (types, ranges)
    2. Semantic validation (duplicate names, object existence)
    3. Geometry validation (valid FreeCAD shape)

    Args:
        name: Unique object name (max 100 chars). Must not already exist in document.
        radius: Radius in mm (range: 0.1 - 10000)
        height: Height in mm (range: 0.1 - 10000)
        description: Human-readable description of what you're creating
        position: Position (x, y, z) in mm. Defaults to origin (0, 0, 0)
        angle: Sweep angle in degrees (0-360). Defaults to 360 for full cylinder.
               Use angle < 360 for partial cylinder (e.g., 180 for half-cylinder)

    Returns:
        OperationResult with success status, message, and affected object name

    Example - Basic cylinder:
        create_cylinder_tool(
            name="Shaft",
            radius=5,
            height=40,
            description="M10 bolt shaft"
        )

    Example - Half cylinder at custom position:
        create_cylinder_tool(
            name="HalfCylinder",
            radius=8,
            height=25,
            position=(10, 20, 5),
            angle=180,
            description="Half cylinder component"
        )
    """
    return create_cylinder(
        name=name,
        radius=radius,
        height=height,
        description=description,
        position=position,
        angle=angle,
    )


@mcp.tool()
def create_sketch_tool(
    name: str,
    description: str,
    plane: str = "XY",
) -> OperationResult:
    """
    Create a 2D sketch on specified plane.

    Creates an empty sketch on the specified plane at the origin. After creating
    the sketch, use add_sketch_circle_tool to add circles or other geometry.
    Sketches are the foundation for creating complex 2D profiles that can be
    extruded (pad) or used to cut material (pocket).

    All parameters are validated before execution using 3-layer validation:
    1. Pydantic validation (types, valid plane names)
    2. Semantic validation (duplicate names)
    3. Geometry validation (valid FreeCAD sketch)

    Args:
        name: Unique sketch name (max 100 chars). Must not already exist in document.
        description: Human-readable description of what you're sketching
        plane: Plane to sketch on. Options: "XY" (top view, looking down),
               "XZ" (front view), "YZ" (side view). Defaults to "XY".

    Returns:
        OperationResult with success status, message, and affected object name

    Example - Basic sketch:
        create_sketch_tool(
            name="WasherProfile",
            plane="XY",
            description="Sketch for washer outer profile"
        )

    Example - Front view sketch:
        create_sketch_tool(
            name="FrontProfile",
            plane="XZ",
            description="Front view profile for extrusion"
        )

    Workflow:
        1. Create sketch (this tool)
        2. Add geometry with add_sketch_circle_tool, add_sketch_line_tool, etc.
        3. Extrude sketch with create_pad_tool or cut with create_pocket_tool
    """
    return create_sketch(
        name=name,
        description=description,
        plane=plane,
    )


@mcp.tool()
def add_sketch_circle_tool(
    sketch_name: str,
    center: tuple[float, float],
    radius: float,
    description: str,
) -> OperationResult:
    """
    Add circle to existing sketch.

    Adds a circle at the specified center position with the specified radius
    to an existing sketch. Multiple circles can be added to the same sketch
    (e.g., for washers with outer circle and center hole).

    All parameters are validated before execution using 3-layer validation:
    1. Pydantic validation (types, ranges)
    2. Semantic validation (sketch exists, is valid sketch object)
    3. Geometry validation (valid circle geometry)

    Args:
        sketch_name: Name of sketch to add circle to (must exist in document)
        center: Circle center (x, y) in mm within sketch coordinate system.
                For circles at origin, use (0, 0).
        radius: Circle radius in mm (range: 0.1 - 10000)
        description: Human-readable description of the circle

    Returns:
        OperationResult with success status, message, and affected sketch name

    Example - Center circle:
        add_sketch_circle_tool(
            sketch_name="WasherProfile",
            center=(0, 0),
            radius=10,
            description="20mm diameter washer outer circle"
        )

    Example - Offset hole:
        add_sketch_circle_tool(
            sketch_name="Pattern",
            center=(15, 20),
            radius=5,
            description="Mounting hole at (15, 20)"
        )

    Example - Washer with hole (two circles):
        # First add outer circle
        add_sketch_circle_tool(
            sketch_name="Washer",
            center=(0, 0),
            radius=10,
            description="Washer outer diameter 20mm"
        )
        # Then add inner hole
        add_sketch_circle_tool(
            sketch_name="Washer",
            center=(0, 0),
            radius=5.5,
            description="Center hole 11mm diameter for M10 bolt"
        )

    Note:
        Use list_objects_tool() to find available sketch names.
        Center coordinates are in the sketch's 2D coordinate system.
    """
    return add_sketch_circle(
        sketch_name=sketch_name,
        center=center,
        radius=radius,
        description=description,
    )


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
