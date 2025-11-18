"""
Utility functions for adam-mcp

Core helper functions used across the codebase.
"""

from typing import TYPE_CHECKING, Any

from adam_mcp.constants import (
    ERROR_FREECAD_API,
    ERROR_INVALID_DIMENSION,
    ERROR_NO_ACTIVE_DOC,
    MAX_DIMENSION_MM,
    MIN_DIMENSION_MM,
)

if TYPE_CHECKING:
    import FreeCAD
else:
    # Import FreeCAD at runtime after environment setup
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


# ============================================================================
# FreeCAD Version Utilities
# ============================================================================


def get_freecad_version() -> str:
    """
    Get FreeCAD version string

    Returns:
        Version string (e.g., "1.0.2")
    """
    if FreeCAD is None:
        raise RuntimeError("FreeCAD not initialized")
    version_parts = FreeCAD.Version()[:3]
    return ".".join(version_parts)


# ============================================================================
# Document Utilities
# ============================================================================


def get_active_document() -> Any:
    """
    Get active FreeCAD document

    Returns:
        Active document object

    Raises:
        RuntimeError: If no active document exists
    """
    if FreeCAD is None:
        raise RuntimeError("FreeCAD not initialized")
    doc = FreeCAD.ActiveDocument
    if doc is None:
        raise RuntimeError(ERROR_NO_ACTIVE_DOC)
    return doc


# ============================================================================
# Error Formatting
# ============================================================================


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


# ============================================================================
# Validation Utilities
# ============================================================================


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
