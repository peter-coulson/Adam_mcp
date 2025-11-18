"""PartDesign feature operation models (Pad, Pocket, Thread)"""

from typing import Literal

from pydantic import Field

from adam_mcp.constants.dimensions import MAX_DIMENSION_MM, MIN_DIMENSION_MM
from adam_mcp.models.base import BaseOperation


class CreatePad(BaseOperation):
    """
    Extrude a sketch into a solid (PartDesign Pad feature).

    Example:
        {
            "action": "create_pad",
            "name": "WasherBody",
            "sketch": "WasherProfile",
            "length": 3,
            "description": "Extrude washer profile 3mm"
        }

    Prerequisites:
        - Sketch must be closed (complete profile)
        - Use list_objects() to find available sketch names

    Note: Pad creates a 3D solid by extruding a 2D sketch perpendicular to the sketch plane.
    """

    action: Literal["create_pad"] = Field(
        default="create_pad",
        description="Operation type (always 'create_pad')",
    )
    name: str = Field(
        max_length=100,
        description="Name for the pad feature (must be unique in document)",
    )
    sketch: str = Field(
        description="Name of sketch to extrude (must be closed sketch)",
    )
    length: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description=f"Extrusion length in mm (range: {MIN_DIMENSION_MM}-{MAX_DIMENSION_MM})",
    )
    reversed: bool = Field(
        default=False,
        description="Extrude in opposite direction. Default: false",
    )


class CreatePocket(BaseOperation):
    """
    Cut material from solid using sketch profile (PartDesign Pocket feature).

    Example:
        {
            "action": "create_pocket",
            "name": "WasherHole",
            "sketch": "HoleProfile",
            "length": 3,
            "description": "Cut through washer center"
        }

    Prerequisites:
        - Sketch must be closed (complete profile)
        - Base solid must exist (e.g., from Pad)
        - Use for cutting holes, slots, pockets

    Note: Pocket removes material by cutting into a solid using a sketch profile.
    """

    action: Literal["create_pocket"] = Field(
        default="create_pocket",
        description="Operation type (always 'create_pocket')",
    )
    name: str = Field(
        max_length=100,
        description="Name for the pocket feature (must be unique in document)",
    )
    sketch: str = Field(
        description="Name of sketch profile to cut (must be closed sketch)",
    )
    length: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description=f"Cut depth in mm (range: {MIN_DIMENSION_MM}-{MAX_DIMENSION_MM})",
    )
    reversed: bool = Field(
        default=False,
        description="Cut in opposite direction. Default: false",
    )


class CreateThread(BaseOperation):
    """
    Add ISO metric threads to cylindrical surface.

    Example:
        {
            "action": "create_thread",
            "name": "ThreadedBolt",
            "base": "BoltShaft",
            "thread_type": "M10",
            "length": 30,
            "description": "Add M10 threads to bolt shaft"
        }

    Prerequisites:
        - Base object must be cylindrical (e.g., cylinder primitive)
        - Use get_object_details() to verify base object exists

    Supported thread types: M3, M4, M5, M6, M8, M10, M12, M14, M16, M20, M24, M30

    Note: This creates cosmetic threads (visual representation). For engineering
    analysis, use nominal diameter without threads.
    """

    action: Literal["create_thread"] = Field(
        default="create_thread",
        description="Operation type (always 'create_thread')",
    )
    name: str = Field(
        max_length=100,
        description="Name for threaded object (must be unique in document)",
    )
    base: str = Field(
        description="Name of cylindrical object to add threads to",
    )
    thread_type: str = Field(
        description="ISO thread designation (e.g., 'M10', 'M8', 'M6')",
        pattern=r"^M\d+$",
    )
    length: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description=f"Thread length in mm (range: {MIN_DIMENSION_MM}-{MAX_DIMENSION_MM})",
    )


# Post-MVP: CreateRevolution, CreateHole, CreateFillet, CreateChamfer, CreateDraft, CreateLoft
