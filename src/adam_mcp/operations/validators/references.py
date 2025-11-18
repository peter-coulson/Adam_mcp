"""Object reference validation"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import FreeCAD


def validate_object_exists(doc: "FreeCAD.Document", name: str) -> bool:
    """
    Check if object exists in document.

    Args:
        doc: FreeCAD document to search
        name: Object name to check

    Returns:
        True if object exists, False otherwise
    """
    return doc.getObject(name) is not None


def validate_sketch_exists(doc: "FreeCAD.Document", name: str) -> tuple[bool, str]:
    """
    Validate that sketch exists and is a valid Sketcher object.

    Args:
        doc: FreeCAD document to search
        name: Sketch name to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if sketch exists and is valid
        - (False, error_message) if validation fails
    """
    # Check if object exists
    obj = doc.getObject(name)
    if obj is None:
        return (
            False,
            f"Sketch '{name}' not found in document. Use list_objects() to see available sketches.",
        )

    # Check if it's a Sketcher object
    if obj.TypeId != "Sketcher::SketchObject":
        return (
            False,
            f"Object '{name}' is not a sketch (type: {obj.TypeId}). Use list_objects() to find sketches.",
        )

    return (True, "")


def validate_object_has_property(
    doc: "FreeCAD.Document", name: str, property_name: str
) -> tuple[bool, str]:
    """
    Validate that object exists and has the specified property.

    Args:
        doc: FreeCAD document to search
        name: Object name to check
        property_name: Property name to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, "") if object exists and has property
        - (False, error_message) if validation fails
    """
    # Check if object exists
    obj = doc.getObject(name)
    if obj is None:
        return (
            False,
            f"Object '{name}' not found in document. Use list_objects() to see available objects.",
        )

    # Check if property exists
    if not hasattr(obj, property_name):
        return (
            False,
            f"Object '{name}' does not have property '{property_name}'. "
            f"Use get_object_details(['{name}']) to see available properties.",
        )

    return (True, "")


# Post-MVP: validate_dependency_chain, validate_face_index, validate_edge_indices
