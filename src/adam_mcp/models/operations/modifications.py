"""Object modification operation models"""

from typing import Literal

from pydantic import Field

from adam_mcp.models.base import BaseOperation


class ModifyObject(BaseOperation):
    """
    Modify properties of existing object.

    Example - Change cylinder dimensions:
        {
            "action": "modify_object",
            "name": "BoltShaft",
            "property": "Radius",
            "value": 6.0,
            "description": "Increase shaft radius to 6mm"
        }

    Example - Change pad length:
        {
            "action": "modify_object",
            "name": "WasherBody",
            "property": "Length",
            "value": 4.0,
            "description": "Increase washer thickness for heavy-duty use"
        }

    Prerequisites:
        - Object must exist in document
        - Property must be valid for object type
        - Use get_object_details() to discover available properties

    Common properties by object type:
        - Cylinder: Radius, Height, Angle
        - Pad: Length, Reversed
        - Pocket: Length, Reversed
        - Sketch: (see sketch-specific operations)

    Note: Property names are FreeCAD-specific. Use get_object_details() to discover
    the exact property names available for an object.
    """

    action: Literal["modify_object"] = Field(
        default="modify_object",
        description="Operation type (always 'modify_object')",
    )
    name: str = Field(
        description="Name of object to modify (must exist in document)",
    )
    property: str = Field(
        description="Property name (e.g., 'Radius', 'Height', 'Length', 'Angle')",
    )
    value: float | str | bool | tuple[float, ...] = Field(
        description="New value for property (type depends on property)",
    )


# Post-MVP: Additional modification operations (position, rotation, mirroring, patterns)
