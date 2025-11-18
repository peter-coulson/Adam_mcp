"""
CAD operation tools for adam-mcp

Tools for inspecting and querying CAD objects in FreeCAD documents.
"""

from typing import TYPE_CHECKING

from adam_mcp.models import (
    ObjectDetail,
    ObjectDetailsResponse,
    ObjectListResponse,
    ObjectProperty,
    ObjectSummary,
)
from adam_mcp.utils import format_freecad_error, get_active_document

if TYPE_CHECKING:
    import FreeCAD
else:
    # Import FreeCAD at runtime after environment setup
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


# ============================================================================
# CAD Query Tools
# ============================================================================


def list_objects() -> ObjectListResponse:
    """
    List all objects in the active document.

    Returns lightweight overview with object names, types, and dependencies.
    Use this for quick inspection before operations. For detailed properties,
    use get_object_details().

    Returns:
        List of object summaries with dependency information

    Raises:
        RuntimeError: If no active document exists
    """
    try:
        doc = get_active_document()

        # Build object summaries
        summaries: list[ObjectSummary] = []
        for obj in doc.Objects:
            # Get objects this object depends on
            depends_on = [dep.Name for dep in obj.InList if dep in doc.Objects]

            summaries.append(
                ObjectSummary(
                    name=obj.Name,
                    type=obj.TypeId,
                    label=obj.Label,
                    depends_on=depends_on,
                )
            )

        return ObjectListResponse(count=len(summaries), objects=summaries)

    except RuntimeError:
        raise
    except (AttributeError, TypeError) as e:
        raise RuntimeError(format_freecad_error(e, "Failed to list objects")) from e


def get_object_details(names: list[str]) -> ObjectDetailsResponse:
    """
    Get detailed information for specific objects.

    Fetches rich context including all properties, values, and bidirectional
    dependencies. Use this on-demand after list_objects() to get details for
    specific objects of interest.

    Args:
        names: List of object names to fetch details for

    Returns:
        Detailed information for found objects, plus list of not found names

    Raises:
        RuntimeError: If no active document exists
    """
    try:
        doc = get_active_document()

        # Build lookup for all objects
        obj_by_name = {obj.Name: obj for obj in doc.Objects}

        details: list[ObjectDetail] = []
        not_found: list[str] = []

        for name in names:
            if name not in obj_by_name:
                not_found.append(name)
                continue

            obj = obj_by_name[name]

            # Extract all properties
            properties: list[ObjectProperty] = []
            for prop_name in obj.PropertiesList:
                try:
                    prop_value = getattr(obj, prop_name)
                    prop_type = type(prop_value).__name__

                    # Serialize value as string
                    # Special handling for FreeCAD objects (show name, not repr)
                    value_str = prop_value.Name if hasattr(prop_value, "Name") else str(prop_value)

                    properties.append(
                        ObjectProperty(name=prop_name, value=value_str, type=prop_type)
                    )
                except (AttributeError, RuntimeError):
                    # Skip properties that can't be read
                    continue

            # Get dependency information
            depends_on = [dep.Name for dep in obj.InList if dep in doc.Objects]
            depended_by = [dep.Name for dep in obj.OutList if dep in doc.Objects]

            details.append(
                ObjectDetail(
                    name=obj.Name,
                    type=obj.TypeId,
                    label=obj.Label,
                    properties=properties,
                    depends_on=depends_on,
                    depended_by=depended_by,
                )
            )

        return ObjectDetailsResponse(objects=details, not_found=not_found)

    except RuntimeError:
        raise
    except (AttributeError, TypeError) as e:
        raise RuntimeError(format_freecad_error(e, "Failed to get object details")) from e
