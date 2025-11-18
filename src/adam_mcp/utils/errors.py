"""Error formatting utilities"""

from adam_mcp.constants.messages import ERROR_FREECAD_API


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
