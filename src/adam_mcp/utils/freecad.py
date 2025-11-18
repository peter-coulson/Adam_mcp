"""FreeCAD utilities"""

from typing import TYPE_CHECKING, Any

from adam_mcp.constants.messages import ERROR_NO_ACTIVE_DOC

if TYPE_CHECKING:
    import FreeCAD
else:
    # Import FreeCAD at runtime after environment setup
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


def get_freecad_version() -> str:
    """
    Get FreeCAD version string

    Returns:
        Version string (e.g., "1.0.2")

    Raises:
        RuntimeError: If FreeCAD is not initialized
    """
    if FreeCAD is None:
        raise RuntimeError("FreeCAD not initialized")
    version_parts = FreeCAD.Version()[:3]
    return ".".join(version_parts)


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
