"""CAD operation execution functions (one per operation type)"""

from adam_mcp.models.operations.primitives import CreateCylinder
from adam_mcp.models.operations.sketches import AddSketchCircle, CreateSketch
from adam_mcp.models.responses import OperationResult
from adam_mcp.operations.dispatcher import Operation, execute_operation


def execute_standard_operation(operation: Operation) -> OperationResult:
    """
    Execute a standard CAD operation (internal function).

    This is a thin wrapper that calls into the operation dispatcher.
    All validation (Pydantic, semantic, and geometric) happens in the dispatcher.

    Args:
        operation: Validated operation to execute

    Returns:
        OperationResult with success status and detailed message

    Note:
        This function is for internal use. MCP tools should use the
        operation-specific functions (create_cylinder, create_pad, etc.)
        which have flat parameter lists that work better with MCP integration.
    """
    return execute_operation(operation)


# ============================================================================
# Operation-Specific Functions (MVP Iteration 1)
# ============================================================================


def create_cylinder(
    name: str,
    radius: float,
    height: float,
    description: str,
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    angle: float = 360.0,
) -> OperationResult:
    """
    Create a cylindrical primitive.

    All parameters validated before execution:
    - Pydantic validation (types, ranges)
    - Semantic validation (duplicate names)
    - Geometry validation (valid FreeCAD shape)

    Args:
        name: Unique object name (max 100 chars)
        radius: Radius in mm (range: 0.1 - 10000)
        height: Height in mm (range: 0.1 - 10000)
        description: Human-readable description of what you're creating
        position: Position (x, y, z) in mm. Defaults to origin (0, 0, 0)
        angle: Sweep angle in degrees (0-360). Defaults to 360 for full cylinder.
               Use angle < 360 for partial cylinder (e.g., 180 for half-cylinder)

    Returns:
        OperationResult with success status, message, and affected object name

    Example:
        >>> result = create_cylinder(
        ...     name="Shaft",
        ...     radius=5,
        ...     height=40,
        ...     description="M10 bolt shaft"
        ... )
        >>> print(result.success)
        True
        >>> print(result.affected_object)
        'Shaft'

    Example with partial cylinder:
        >>> result = create_cylinder(
        ...     name="HalfCylinder",
        ...     radius=8,
        ...     height=25,
        ...     angle=180,
        ...     description="Half cylinder"
        ... )
    """
    operation = CreateCylinder(
        name=name,
        radius=radius,
        height=height,
        description=description,
        position=position,
        angle=angle,
    )
    return execute_operation(operation)


# ============================================================================
# Sketch Operations (MVP Iteration 2)
# ============================================================================


def create_sketch(
    name: str,
    description: str,
    plane: str = "XY",
) -> OperationResult:
    """
    Create a 2D sketch on specified plane.

    Creates an empty sketch on the specified plane at the origin. After creating
    the sketch, use add_sketch_circle, add_sketch_line, etc. to add geometry.

    All parameters validated before execution:
    - Pydantic validation (types, ranges)
    - Semantic validation (duplicate names)
    - Geometry validation (valid FreeCAD sketch)

    Args:
        name: Unique sketch name (max 100 chars)
        description: Human-readable description of what you're sketching
        plane: Plane to sketch on. Options: "XY" (top view, looking down),
               "XZ" (front view), "YZ" (side view). Defaults to "XY".

    Returns:
        OperationResult with success status, message, and affected object name

    Example - Top view sketch:
        >>> result = create_sketch(
        ...     name="WasherProfile",
        ...     plane="XY",
        ...     description="Sketch for washer outer profile"
        ... )
        >>> print(result.success)
        True
        >>> print(result.affected_object)
        'WasherProfile'

    Example - Front view sketch:
        >>> result = create_sketch(
        ...     name="FrontProfile",
        ...     plane="XZ",
        ...     description="Front view profile"
        ... )
    """
    operation = CreateSketch(
        name=name,
        plane=plane,  # type: ignore[arg-type]
        description=description,
    )
    return execute_operation(operation)


def add_sketch_circle(
    sketch_name: str,
    center: tuple[float, float],
    radius: float,
    description: str,
) -> OperationResult:
    """
    Add circle to existing sketch.

    Adds a circle at the specified center position with the specified radius
    to an existing sketch. The sketch must exist in the active document.

    All parameters validated before execution:
    - Pydantic validation (types, ranges)
    - Semantic validation (sketch exists, is valid sketch object)
    - Geometry validation (valid circle geometry)

    Args:
        sketch_name: Name of sketch to add circle to (must exist)
        center: Circle center (x, y) in mm within sketch coordinate system
        radius: Circle radius in mm (range: 0.1 - 10000)
        description: Human-readable description of the circle

    Returns:
        OperationResult with success status, message, and affected sketch name

    Example - Center circle:
        >>> result = add_sketch_circle(
        ...     sketch_name="WasherProfile",
        ...     center=(0, 0),
        ...     radius=10,
        ...     description="20mm diameter washer outer circle"
        ... )
        >>> print(result.success)
        True

    Example - Offset circle:
        >>> result = add_sketch_circle(
        ...     sketch_name="Pattern",
        ...     center=(15, 20),
        ...     radius=5,
        ...     description="Hole at position (15, 20)"
        ... )

    Note:
        Use list_objects() to find available sketch names.
        Center coordinates are in the sketch's 2D coordinate system.
    """
    operation = AddSketchCircle(
        sketch_name=sketch_name,
        center=center,
        radius=radius,
        description=description,
    )
    return execute_operation(operation)
