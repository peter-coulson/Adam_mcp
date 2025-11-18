"""Primitive operation models (Box, Cylinder, Sphere, Cone, Torus)"""

from typing import Literal

from pydantic import Field

from adam_mcp.constants.dimensions import MAX_DIMENSION_MM, MIN_DIMENSION_MM
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
    name: str = Field(max_length=100, description="Object name (must be unique in document)")
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
        default=360,
        gt=0,
        le=360,
        description="Sweep angle in degrees (0-360). Default 360 for full cylinder.",
    )
