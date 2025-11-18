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


class ProjectInfo(BaseModel):
    """Project file information"""

    name: str = Field(description="Project filename (e.g., 'bracket.FCStd')")
    path: str = Field(description="Full path to project file")
    size_bytes: int = Field(ge=0, description="File size in bytes")
    modified_time: str = Field(description="Last modified timestamp (ISO format)")
    has_working_file: bool = Field(description="Whether a .work file exists for this project")


class ProjectsList(BaseModel):
    """List of projects response"""

    directory: str = Field(description="Directory that was searched")
    projects: list[ProjectInfo] = Field(description="List of found projects")
    total_count: int = Field(ge=0, description="Total number of projects found")
