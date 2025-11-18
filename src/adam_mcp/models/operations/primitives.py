"""Primitive operation models (Box, Cylinder, Sphere, Cone, Torus)"""

from typing import Literal

from pydantic import Field

from adam_mcp.constants.dimensions import MAX_ANGLE_DEGREES, MAX_DIMENSION_MM, MIN_DIMENSION_MM
from adam_mcp.constants.operations import MAX_DOCUMENT_NAME_LENGTH
from adam_mcp.models.base import BaseOperation


class CreateCylinder(BaseOperation):
    """
    Create a cylindrical primitive.

    Example:
        {
            "action": "create_cylinder",
            "name": "Shaft",
            "radius": 5,
            "height": 40,
            "description": "M10 bolt shaft"
        }

    Note: Use angle < 360 for partial cylinder (e.g., 180 for half-cylinder)
    """

    action: Literal["create_cylinder"] = Field(
        default="create_cylinder",
        description="Operation type (always 'create_cylinder')",
    )
    name: str = Field(
        max_length=MAX_DOCUMENT_NAME_LENGTH, description="Object name (must be unique in document)"
    )
    radius: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description=f"Radius in mm (range: {MIN_DIMENSION_MM}-{MAX_DIMENSION_MM})",
    )
    height: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description=f"Height in mm (range: {MIN_DIMENSION_MM}-{MAX_DIMENSION_MM})",
    )
    position: tuple[float, float, float] = Field(
        default=(0, 0, 0),
        description="Position (x, y, z) in mm. Optional, defaults to origin.",
    )
    angle: float = Field(
        default=MAX_ANGLE_DEGREES,
        gt=0,
        le=MAX_ANGLE_DEGREES,
        description=f"Sweep angle in degrees (0-{MAX_ANGLE_DEGREES}). Default {MAX_ANGLE_DEGREES} for full cylinder.",
    )
