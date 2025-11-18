"""Validation utilities"""

from typing import Any

from adam_mcp.constants.dimensions import MAX_DIMENSION_MM, MIN_DIMENSION_MM
from adam_mcp.constants.messages import ERROR_INVALID_DIMENSION


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


def validate_document(doc: Any) -> bool:
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
