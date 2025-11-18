"""CAD operation execution functions (one per operation type)"""

from adam_mcp.models.operations.features import CreatePad, CreatePocket, CreateThread
from adam_mcp.models.operations.modifications import ModifyObject
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


# ============================================================================
# Feature Operations (MVP Iteration 3)
# ============================================================================


def create_pad(
    name: str,
    sketch: str,
    length: float,
    description: str,
    reversed: bool = False,
) -> OperationResult:
    """
    Extrude a sketch into a solid (PartDesign Pad feature).

    Takes a 2D sketch and extrudes it perpendicular to the sketch plane to create
    a 3D solid. The sketch must be closed (complete profile).

    All parameters validated before execution:
    - Pydantic validation (types, ranges)
    - Semantic validation (sketch exists, is closed, suitable for extrusion)
    - Geometry validation (valid 3D solid created)

    Args:
        name: Unique name for the pad feature (max 100 chars)
        sketch: Name of sketch to extrude (must be closed sketch)
        length: Extrusion length in mm (range: 0.1 - 10000)
        description: Human-readable description of what you're creating
        reversed: Extrude in opposite direction. Defaults to False.

    Returns:
        OperationResult with success status, message, and affected object name

    Example - Create washer body:
        >>> result = create_pad(
        ...     name="WasherBody",
        ...     sketch="WasherProfile",
        ...     length=3,
        ...     description="Extrude washer profile 3mm"
        ... )
        >>> print(result.success)
        True
        >>> print(result.affected_object)
        'WasherBody'

    Example - Reverse extrusion:
        >>> result = create_pad(
        ...     name="ExtrudedProfile",
        ...     sketch="Profile",
        ...     length=10,
        ...     reversed=True,
        ...     description="Extrude downward"
        ... )

    Note:
        Use list_objects() to find available sketch names.
        Use get_object_details() to verify sketch is closed before extruding.
    """
    operation = CreatePad(
        name=name,
        sketch=sketch,
        length=length,
        description=description,
        reversed=reversed,
    )
    return execute_operation(operation)


def create_pocket(
    name: str,
    sketch: str,
    length: float,
    description: str,
    reversed: bool = False,
) -> OperationResult:
    """
    Cut material from solid using sketch profile (PartDesign Pocket feature).

    Takes a 2D sketch profile and removes material from an existing solid by
    cutting into it. Commonly used for creating holes, slots, and pockets.

    All parameters validated before execution:
    - Pydantic validation (types, ranges)
    - Semantic validation (sketch exists, is closed)
    - Geometry validation (valid cut operation)

    Args:
        name: Unique name for the pocket feature (max 100 chars)
        sketch: Name of sketch profile to cut (must be closed sketch)
        length: Cut depth in mm (range: 0.1 - 10000)
        description: Human-readable description of what you're creating
        reversed: Cut in opposite direction. Defaults to False.

    Returns:
        OperationResult with success status, message, and affected object name

    Example - Create washer hole:
        >>> result = create_pocket(
        ...     name="WasherHole",
        ...     sketch="HoleProfile",
        ...     length=3,
        ...     description="Cut through washer center"
        ... )
        >>> print(result.success)
        True
        >>> print(result.affected_object)
        'WasherHole'

    Example - Reverse cut:
        >>> result = create_pocket(
        ...     name="Slot",
        ...     sketch="SlotProfile",
        ...     length=5,
        ...     reversed=True,
        ...     description="Cut slot in opposite direction"
        ... )

    Note:
        Use list_objects() to find available sketch names.
        A base solid must exist before creating a pocket (e.g., from Pad).
    """
    operation = CreatePocket(
        name=name,
        sketch=sketch,
        length=length,
        description=description,
        reversed=reversed,
    )
    return execute_operation(operation)


def create_thread(
    name: str,
    base: str,
    thread_type: str,
    length: float,
    description: str,
) -> OperationResult:
    """
    Add ISO metric threads to cylindrical surface.

    Creates a cosmetic thread representation on a cylindrical object. The base
    object geometry is preserved with thread metadata added.

    All parameters validated before execution:
    - Pydantic validation (types, ranges, thread format)
    - Semantic validation (base object exists, thread type is valid)
    - Geometry validation (valid threaded object created)

    Args:
        name: Unique name for threaded object (max 100 chars)
        base: Name of cylindrical object to add threads to (must exist)
        thread_type: ISO thread designation (e.g., 'M10', 'M8', 'M6')
        length: Thread length in mm (range: 0.1 - 10000)
        description: Human-readable description of what you're creating

    Returns:
        OperationResult with success status, message, and affected object name

    Supported thread types:
        M3, M4, M5, M6, M8, M10, M12, M14, M16, M20, M24, M30

    Example - Add M10 threads to bolt:
        >>> result = create_thread(
        ...     name="ThreadedBolt",
        ...     base="BoltShaft",
        ...     thread_type="M10",
        ...     length=30,
        ...     description="Add M10 threads to bolt shaft"
        ... )
        >>> print(result.success)
        True
        >>> print(result.affected_object)
        'ThreadedBolt'

    Example - M6 threads:
        >>> result = create_thread(
        ...     name="ThreadedRod",
        ...     base="Rod",
        ...     thread_type="M6",
        ...     length=50,
        ...     description="M6 threaded rod"
        ... )

    Note:
        This creates cosmetic threads (visual representation). For engineering
        analysis, use nominal diameter without actual thread geometry.
        Use list_objects() to find available base objects.
    """
    operation = CreateThread(
        name=name,
        base=base,
        thread_type=thread_type,
        length=length,
        description=description,
    )
    return execute_operation(operation)


# ============================================================================
# Modification Operations (MVP Iteration 3)
# ============================================================================


def modify_object(
    name: str,
    property: str,
    value: float | str | bool | tuple[float, ...],
    description: str,
) -> OperationResult:
    """
    Modify properties of existing object.

    Changes a property value on an existing object. Use get_object_details() to
    discover available properties for an object.

    All parameters validated before execution:
    - Pydantic validation (types)
    - Semantic validation (object exists, property exists, value is valid type)
    - Geometry validation (valid geometry after modification)

    Args:
        name: Name of object to modify (must exist)
        property: Property name (e.g., 'Radius', 'Height', 'Length', 'Angle')
        value: New value for property (type depends on property)
        description: Human-readable description of the change

    Returns:
        OperationResult with success status, message, and affected object name

    Common properties by object type:
        - Cylinder: Radius, Height, Angle
        - Pad: Length, Reversed
        - Pocket: Length, Reversed
        - Sketch: (see sketch-specific operations)

    Example - Change cylinder radius:
        >>> result = modify_object(
        ...     name="BoltShaft",
        ...     property="Radius",
        ...     value=6.0,
        ...     description="Increase shaft radius to 6mm"
        ... )
        >>> print(result.success)
        True
        >>> print(result.affected_object)
        'BoltShaft'

    Example - Change pad length:
        >>> result = modify_object(
        ...     name="WasherBody",
        ...     property="Length",
        ...     value=4.0,
        ...     description="Increase washer thickness for heavy-duty use"
        ... )

    Example - Change boolean property:
        >>> result = modify_object(
        ...     name="ExtrudedFeature",
        ...     property="Reversed",
        ...     value=True,
        ...     description="Reverse extrusion direction"
        ... )

    Note:
        Property names are FreeCAD-specific. Use get_object_details([name])
        to discover the exact property names and current values for an object.
    """
    operation = ModifyObject(
        name=name,
        property=property,
        value=value,
        description=description,
    )
    return execute_operation(operation)
