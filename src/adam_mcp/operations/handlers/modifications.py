"""Handlers for object modification operations"""

from typing import TYPE_CHECKING, Any

from adam_mcp.models.operations.modifications import ModifyObject
from adam_mcp.operations.validators.references import validate_object_has_property

if TYPE_CHECKING:
    import FreeCAD
else:
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


def execute_modify_object(operation: ModifyObject, doc: Any) -> str:
    """
    Execute ModifyObject operation.

    Args:
        operation: ModifyObject operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of modified object

    Raises:
        ValueError: If validation fails (object missing, invalid property, etc.)
        RuntimeError: If FreeCAD API call fails or property assignment fails
    """
    # Validate object exists and has the specified property
    is_valid, error_msg = validate_object_has_property(doc, operation.name, operation.property)
    if not is_valid:
        raise ValueError(error_msg)

    # Get object
    obj = doc.getObject(operation.name)

    # Get current value for error messages
    try:
        old_value = getattr(obj, operation.property)
    except AttributeError as e:
        # Should not happen due to validation, but handle gracefully
        raise ValueError(
            f"Cannot access property '{operation.property}' on object '{operation.name}'."
        ) from e

    # Set new value
    try:
        setattr(obj, operation.property, operation.value)
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Cannot set property '{operation.property}' to value '{operation.value}'. "
            f"Current value: {old_value}. Error: {e}"
        ) from e

    # Recompute document to apply changes
    doc.recompute()

    return operation.name


# Post-MVP: execute_modify_position, execute_modify_rotation, execute_mirror_object,
# execute_create_linear_pattern, execute_create_polar_pattern
