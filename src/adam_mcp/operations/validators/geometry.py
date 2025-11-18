"""Geometric validation for CAD operations"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import FreeCAD


def validate_sketch_for_pad(doc: "FreeCAD.Document", sketch_name: str) -> tuple[bool, str]:
    """
    Validate that sketch is suitable for Pad operation.

    Checks:
    - Sketch exists and is a Sketcher object
    - Sketch has geometry
    - Sketch profile is closed (required for extrusion)

    Args:
        doc: FreeCAD document containing sketch
        sketch_name: Name of sketch to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if sketch is valid for pad
        - (False, error_message) if validation fails
    """
    # Check if object exists
    sketch = doc.getObject(sketch_name)
    if sketch is None:
        return (
            False,
            f"Sketch '{sketch_name}' not found. Use list_objects() to see available sketches.",
        )

    # Check if it's a sketch
    if sketch.TypeId != "Sketcher::SketchObject":
        return (
            False,
            f"Object '{sketch_name}' is not a sketch (type: {sketch.TypeId}). "
            "Pad requires a Sketcher object.",
        )

    # Check if sketch has geometry
    if not hasattr(sketch, "Geometry") or len(sketch.Geometry) == 0:
        return (
            False,
            f"Sketch '{sketch_name}' has no geometry. Add circles, lines, etc. before creating pad.",
        )

    # Check if sketch has a closed profile
    # Note: FreeCAD's Shape property provides the actual geometry
    if not hasattr(sketch, "Shape") or sketch.Shape.isNull():
        return (
            False,
            f"Sketch '{sketch_name}' has invalid geometry. Check sketch constraints and geometry.",
        )

    # Check if sketch has wires (closed profiles)
    if not sketch.Shape.Wires:
        return (
            False,
            f"Sketch '{sketch_name}' has no closed profiles. "
            "Pad requires at least one closed profile (e.g., circle, closed polyline).",
        )

    return (True, "")


def validate_sketch_for_pocket(doc: "FreeCAD.Document", sketch_name: str) -> tuple[bool, str]:
    """
    Validate that sketch is suitable for Pocket operation.

    Same requirements as Pad - sketch must be closed and have geometry.

    Args:
        doc: FreeCAD document containing sketch
        sketch_name: Name of sketch to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if sketch is valid for pocket
        - (False, error_message) if validation fails
    """
    # Pocket has same requirements as Pad
    return validate_sketch_for_pad(doc, sketch_name)


def validate_thread_type(thread_type: str) -> tuple[bool, str]:
    """
    Validate ISO metric thread designation.

    Args:
        thread_type: Thread designation (e.g., "M10", "M8")

    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if thread type is valid
        - (False, error_message) if validation fails
    """
    # Standard ISO metric thread sizes
    valid_threads = {
        "M3",
        "M4",
        "M5",
        "M6",
        "M8",
        "M10",
        "M12",
        "M14",
        "M16",
        "M20",
        "M24",
        "M30",
    }

    if thread_type not in valid_threads:
        return (
            False,
            f"Thread type '{thread_type}' not supported. "
            f"Supported types: {', '.join(sorted(valid_threads))}",
        )

    return (True, "")


# Post-MVP: validate_fillet_radius, validate_edge_indices, validate_chamfer_distance
