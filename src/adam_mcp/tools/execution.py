"""CAD operation execution functions (one per operation type)"""

from adam_mcp.models.operations.primitives import CreateCylinder
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
