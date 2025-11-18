"""Handlers for sketch operations"""

import math
from typing import TYPE_CHECKING, Any

from adam_mcp.models.operations.sketches import (
    AddSketchCircle,
    AddSketchPolygon,
    CreateSketch,
)

if TYPE_CHECKING:
    import FreeCAD
else:
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


def execute_create_sketch(operation: CreateSketch, doc: Any) -> str:
    """
    Execute CreateSketch operation.

    Creates a 2D sketch on the specified plane (XY, XZ, or YZ) at the origin.
    The sketch is initially empty - use add_sketch_circle, add_sketch_line, etc.
    to add geometry to it.

    Args:
        operation: CreateSketch operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of created sketch

    Raises:
        ValueError: If sketch name already exists
        RuntimeError: If FreeCAD API call fails
    """
    # Check if object with this name already exists
    if doc.getObject(operation.name) is not None:
        raise ValueError(
            f"Object '{operation.name}' already exists. Choose a different name. "
            f"Use list_objects() to see existing objects."
        )

    # Create sketch object
    sketch = doc.addObject("Sketcher::SketchObject", operation.name)

    # Map plane names to FreeCAD placement
    # XY plane: looking down (Z-axis up)
    # XZ plane: front view (Y-axis up)
    # YZ plane: side view (X-axis up)
    plane_mappings = {
        "XY": (FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1)),  # Origin, Z-axis normal
        "XZ": (FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0)),  # Origin, Y-axis normal
        "YZ": (FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0)),  # Origin, X-axis normal
    }

    position, normal = plane_mappings[operation.plane]
    sketch.MapMode = "Deactivated"  # Deactivated mode doesn't need Support
    sketch.Placement = FreeCAD.Placement(
        position, FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), normal)
    )

    # Recompute document
    doc.recompute()

    return operation.name


def execute_add_sketch_circle(operation: AddSketchCircle, doc: Any) -> str:
    """
    Execute AddSketchCircle operation.

    Adds a circle to an existing sketch at the specified center position with
    the specified radius.

    Args:
        operation: AddSketchCircle operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of the sketch that was modified

    Raises:
        ValueError: If sketch doesn't exist or is not a Sketcher object
        RuntimeError: If FreeCAD API call fails
    """
    # Check if sketch exists
    sketch = doc.getObject(operation.sketch_name)
    if sketch is None:
        raise ValueError(
            f"Sketch '{operation.sketch_name}' not found. "
            f"Use list_objects() to see available objects."
        )

    # Verify it's a sketch object
    if not hasattr(sketch, "addGeometry"):
        raise ValueError(
            f"Object '{operation.sketch_name}' is not a sketch (type: {sketch.TypeId}). "
            f"Use create_sketch() to create a sketch first."
        )

    # Import Part module for circle geometry
    try:
        import Part
    except ImportError as e:
        raise RuntimeError("Failed to import FreeCAD Part module") from e

    # Add circle to sketch
    # FreeCAD circle: Part.Circle with center and radius
    circle = Part.Circle(
        FreeCAD.Vector(operation.center[0], operation.center[1], 0),
        FreeCAD.Vector(0, 0, 1),
        operation.radius,
    )
    sketch.addGeometry(circle, False)  # False = not construction geometry

    # Recompute document
    doc.recompute()

    return operation.sketch_name


def execute_add_sketch_polygon(operation: AddSketchPolygon, doc: Any) -> str:
    """
    Execute AddSketchPolygon operation.

    Adds a regular polygon to an existing sketch at the specified center position
    with the specified radius and number of sides. The polygon is created using
    line segments connecting calculated vertices.

    Args:
        operation: AddSketchPolygon operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of the sketch that was modified

    Raises:
        ValueError: If sketch doesn't exist or is not a Sketcher object
        RuntimeError: If FreeCAD API call fails
    """
    # Check if sketch exists
    sketch = doc.getObject(operation.sketch_name)
    if sketch is None:
        raise ValueError(
            f"Sketch '{operation.sketch_name}' not found. "
            f"Use list_objects() to see available objects."
        )

    # Verify it's a sketch object
    if not hasattr(sketch, "addGeometry"):
        raise ValueError(
            f"Object '{operation.sketch_name}' is not a sketch (type: {sketch.TypeId}). "
            f"Use create_sketch() to create a sketch first."
        )

    # Import Part module for polygon geometry
    try:
        import Part
    except ImportError as e:
        raise RuntimeError("Failed to import FreeCAD Part module") from e

    # Calculate polygon vertices
    # Start angle offset to have first vertex at top (90 degrees)
    start_angle = math.pi / 2
    vertices = []

    for i in range(operation.sides):
        angle = start_angle + (2 * math.pi * i / operation.sides)
        x = operation.center[0] + operation.radius * math.cos(angle)
        y = operation.center[1] + operation.radius * math.sin(angle)
        vertices.append(FreeCAD.Vector(x, y, 0))

    # Add line segments connecting vertices
    for i in range(operation.sides):
        start_vertex = vertices[i]
        end_vertex = vertices[(i + 1) % operation.sides]  # Wrap around to first vertex
        line = Part.LineSegment(start_vertex, end_vertex)
        sketch.addGeometry(line, False)  # False = not construction geometry

    # Recompute document
    doc.recompute()

    return operation.sketch_name
