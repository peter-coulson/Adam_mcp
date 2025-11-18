"""Handlers for primitive operations"""

from typing import TYPE_CHECKING, Any

from adam_mcp.models.operations.primitives import CreateCylinder

if TYPE_CHECKING:
    import FreeCAD
else:
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


def execute_create_cylinder(operation: CreateCylinder, doc: Any) -> str:
    """
    Execute CreateCylinder operation.

    Args:
        operation: CreateCylinder operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of created object

    Raises:
        ValueError: If object name already exists
        RuntimeError: If FreeCAD API call fails
    """
    # Check if object with this name already exists
    if doc.getObject(operation.name) is not None:
        raise ValueError(
            f"Object '{operation.name}' already exists. Choose a different name. "
            f"Use list_objects() to see existing objects."
        )

    # Create cylinder primitive
    cylinder = doc.addObject("Part::Cylinder", operation.name)
    cylinder.Radius = operation.radius
    cylinder.Height = operation.height
    cylinder.Angle = operation.angle

    # Set position
    if operation.position != (0, 0, 0):
        cylinder.Placement.Base = FreeCAD.Vector(*operation.position)

    # Recompute document to apply changes
    doc.recompute()

    return operation.name
