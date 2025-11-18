"""Sketch operation models (CreateSketch, sketch geometry, constraints)"""

from typing import Literal

from pydantic import Field

from adam_mcp.constants.dimensions import (
    MAX_DIMENSION_MM,
    MAX_POLYGON_SIDES,
    MIN_DIMENSION_MM,
    MIN_POLYGON_SIDES,
)
from adam_mcp.constants.operations import MAX_DOCUMENT_NAME_LENGTH
from adam_mcp.models.base import BaseOperation


class CreateSketch(BaseOperation):
    """
    Create a 2D sketch on specified plane.

    Example:
        {
            "action": "create_sketch",
            "name": "WasherProfile",
            "plane": "XY",
            "description": "Sketch for washer outer profile"
        }

    Note: Sketches are created on standard planes (XY, XZ, YZ) at origin.
    After creation, use add_sketch_circle, add_sketch_line, etc. to add geometry.
    """

    action: Literal["create_sketch"] = Field(
        default="create_sketch",
        description="Operation type (always 'create_sketch')",
    )
    name: str = Field(
        max_length=MAX_DOCUMENT_NAME_LENGTH,
        description="Sketch name (must be unique in document)",
    )
    plane: Literal["XY", "XZ", "YZ"] = Field(
        default="XY",
        description="Plane to sketch on. XY = top view (looking down), XZ = front view, YZ = side view",
    )


class AddSketchCircle(BaseOperation):
    """
    Add circle to existing sketch.

    Example:
        {
            "action": "add_sketch_circle",
            "sketch_name": "WasherProfile",
            "center": [0, 0],
            "radius": 10,
            "description": "20mm diameter washer outer circle"
        }

    Note: Center coordinates are in the sketch's 2D coordinate system.
    Use list_objects() to find available sketch names.
    """

    action: Literal["add_sketch_circle"] = Field(
        default="add_sketch_circle",
        description="Operation type (always 'add_sketch_circle')",
    )
    sketch_name: str = Field(
        description="Name of sketch to add circle to (must exist in document)",
    )
    center: tuple[float, float] = Field(
        description="Circle center (x, y) in mm within sketch coordinate system",
    )
    radius: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description=f"Circle radius in mm (range: {MIN_DIMENSION_MM}-{MAX_DIMENSION_MM})",
    )


class AddSketchPolygon(BaseOperation):
    """
    Add regular polygon to existing sketch.

    Example:
        {
            "action": "add_sketch_polygon",
            "sketch_name": "HexSocket",
            "center": [0, 0],
            "radius": 4,
            "sides": 6,
            "description": "Hexagonal allen key socket"
        }

    Note: Center coordinates are in the sketch's 2D coordinate system.
    Radius is the circumradius (distance from center to vertex).
    Use list_objects() to find available sketch names.
    """

    action: Literal["add_sketch_polygon"] = Field(
        default="add_sketch_polygon",
        description="Operation type (always 'add_sketch_polygon')",
    )
    sketch_name: str = Field(
        description="Name of sketch to add polygon to (must exist in document)",
    )
    center: tuple[float, float] = Field(
        description="Polygon center (x, y) in mm within sketch coordinate system",
    )
    radius: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description=f"Circumradius in mm (range: {MIN_DIMENSION_MM}-{MAX_DIMENSION_MM})",
    )
    sides: int = Field(
        ge=MIN_POLYGON_SIDES,
        le=MAX_POLYGON_SIDES,
        description=f"Number of sides ({MIN_POLYGON_SIDES}-{MAX_POLYGON_SIDES}: triangle to dodecagon)",
    )


# Post-MVP: AddSketchLine, AddSketchArc, AddSketchRectangle, AddSketchConstraint
