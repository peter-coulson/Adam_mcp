"""
Pydantic models for adam-mcp

Type-safe data models for request/response validation.
"""

from pydantic import BaseModel, Field

# ============================================================================
# Response Models
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
