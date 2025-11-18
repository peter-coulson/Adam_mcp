"""
adam-mcp: FreeCAD MCP Server

IMPORTANT: FreeCAD environment must be configured before importing FreeCAD modules.
This is done via setup_freecad_environment() which configures Python paths and
environment variables for FreeCAD's dynamic libraries.

Pattern:
    1. Call setup_freecad_environment() ONCE at startup
    2. Import FreeCAD modules
    3. Define and run server
"""

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from adam_mcp.freecad_env import setup_freecad_environment

# ============================================================================
# FreeCAD Environment Setup (MUST be first)
# ============================================================================

setup_freecad_environment()

# Now FreeCAD imports will work
import FreeCAD  # noqa: E402

# ============================================================================
# Constants
# ============================================================================

# Server metadata
SERVER_NAME = "adam-mcp"
SERVER_VERSION = "0.1.0"

# Document defaults
DEFAULT_DOCUMENT_NAME = "CAD_Design"
DEFAULT_SKETCH_NAME = "Sketch"
MAX_DOCUMENT_NAME_LENGTH = 100

# Dimension constraints (mm)
MIN_DIMENSION_MM = 0.1
MAX_DIMENSION_MM = 10000.0
MIN_FILLET_RADIUS_MM = 0.1
MAX_FILLET_RADIUS_MM = 1000.0

# Angular constraints (degrees)
MIN_ANGLE_DEGREES = -360.0
MAX_ANGLE_DEGREES = 360.0

# Error message templates
ERROR_NO_ACTIVE_DOC = "No active FreeCAD document. Create a document first."
ERROR_FREECAD_API = "FreeCAD API error: {error}. {suggestion}"
ERROR_INVALID_DIMENSION = "Dimension {value} mm is outside valid range ({min_val}-{max_val} mm)"
ERROR_INVALID_OBJECT = "Object '{name}' not found in active document"

# Success message templates
SUCCESS_DOC_CREATED = "Created document: {name}"
SUCCESS_OPERATION = "Operation completed successfully"

# ============================================================================
# Pydantic Models (Type-safe parameters)
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    status: str = Field(description="Server status")
    freecad_version: str = Field(description="FreeCAD version")
    active_document: str | None = Field(description="Name of active document, if any")
    message: str = Field(description="Human-readable status message")


class DocumentInfo(BaseModel):
    """Document information response"""

    name: str = Field(description="Document name")
    object_count: int = Field(ge=0, description="Number of objects in document")
    objects: list[str] = Field(description="List of object names")


# ============================================================================
# Utility Functions
# ============================================================================


def get_freecad_version() -> str:
    """
    Get FreeCAD version string

    Returns:
        Version string (e.g., "1.0.2")
    """
    version_parts = FreeCAD.Version()[:3]
    return ".".join(version_parts)


def get_active_document() -> "FreeCAD.Document":
    """
    Get active FreeCAD document

    Returns:
        Active document object

    Raises:
        RuntimeError: If no active document exists
    """
    doc = FreeCAD.ActiveDocument
    if doc is None:
        raise RuntimeError(ERROR_NO_ACTIVE_DOC)
    return doc


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


# ============================================================================
# FastMCP Server
# ============================================================================

mcp = FastMCP(SERVER_NAME)


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
def health_check() -> HealthCheckResponse:
    """
    Check server health and FreeCAD integration status.

    Returns health information including FreeCAD version and active document status.
    Use this to verify the server is running correctly.
    """
    try:
        version = get_freecad_version()
        active_doc = FreeCAD.ActiveDocument
        doc_name = active_doc.Name if active_doc else None

        return HealthCheckResponse(
            status="healthy",
            freecad_version=version,
            active_document=doc_name,
            message=f"Server running. FreeCAD {version} integrated successfully.",
        )
    except (AttributeError, RuntimeError, ImportError) as e:
        return HealthCheckResponse(
            status="error",
            freecad_version="unknown",
            active_document=None,
            message=f"Health check failed: {str(e)}",
        )


@mcp.tool()
def create_document(
    name: str = Field(
        default=DEFAULT_DOCUMENT_NAME,
        min_length=1,
        max_length=MAX_DOCUMENT_NAME_LENGTH,
        description="Document name (alphanumeric and underscores only)",
    ),
) -> DocumentInfo:
    """
    Create a new FreeCAD document.

    This document becomes the active document for subsequent operations.
    If a document with this name already exists, it will be reused.

    Args:
        name: Document name (default: "CAD_Design")

    Returns:
        Information about the created/existing document
    """
    try:
        # Check if document already exists using listDocuments()
        if name in FreeCAD.listDocuments():
            doc = FreeCAD.getDocument(name)
            FreeCAD.setActiveDocument(name)
        else:
            # Document doesn't exist, create it
            doc = FreeCAD.newDocument(name)

        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )
    except (RuntimeError, ValueError) as e:
        raise RuntimeError(
            format_freecad_error(
                e, "Ensure document name contains only alphanumeric characters and underscores."
            )
        ) from e


@mcp.tool()
def get_document_info() -> DocumentInfo:
    """
    Get information about the active document.

    Returns object count and list of objects in the current document.

    Raises:
        RuntimeError: If no active document exists
    """
    try:
        doc = get_active_document()
        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )
    except RuntimeError:
        raise
    except AttributeError as e:
        raise RuntimeError(format_freecad_error(e)) from e


# ============================================================================
# Entry Point
# ============================================================================


def main() -> None:
    """
    Main entry point for the MCP server.

    Starts the FastMCP server and runs indefinitely until terminated.
    """
    mcp.run()


if __name__ == "__main__":
    main()
