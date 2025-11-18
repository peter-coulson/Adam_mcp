"""Response models for adam-mcp tools"""

from pydantic import BaseModel, Field

# ============================================================================
# Health Check & Document Management
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


# ============================================================================
# CAD Query Models
# ============================================================================


class ObjectSummary(BaseModel):
    """Lightweight object summary"""

    name: str = Field(description="Object name (e.g., 'Sketch', 'Pad001')")
    type: str = Field(
        description="FreeCAD object type (e.g., 'Part::Box', 'Sketcher::SketchObject')"
    )
    label: str = Field(description="Human-readable label")
    depends_on: list[str] = Field(
        default_factory=list, description="Names of objects this depends on"
    )


class ObjectListResponse(BaseModel):
    """Response from list_objects"""

    count: int = Field(ge=0, description="Total number of objects")
    objects: list[ObjectSummary] = Field(description="List of object summaries")


class ObjectProperty(BaseModel):
    """A single object property"""

    name: str = Field(description="Property name")
    value: str = Field(description="Property value (serialized as string)")
    type: str = Field(description="Property type (e.g., 'float', 'Vector', 'str')")


class ObjectDetail(BaseModel):
    """Detailed information about an object"""

    name: str = Field(description="Object name")
    type: str = Field(description="FreeCAD object type")
    label: str = Field(description="Human-readable label")
    properties: list[ObjectProperty] = Field(description="Object properties and values")
    depends_on: list[str] = Field(
        default_factory=list, description="Names of objects this depends on"
    )
    depended_by: list[str] = Field(
        default_factory=list, description="Names of objects that depend on this"
    )


class ObjectDetailsResponse(BaseModel):
    """Response from get_object_details"""

    objects: list[ObjectDetail] = Field(description="Detailed information for requested objects")
    not_found: list[str] = Field(
        default_factory=list, description="Names of objects that weren't found"
    )


# ============================================================================
# Operation Results
# ============================================================================


class OperationResult(BaseModel):
    """Result from CAD operation execution"""

    success: bool = Field(description="Whether the operation succeeded")
    message: str = Field(description="Human-readable message explaining the result")
    affected_object: str | None = Field(
        default=None, description="Name of the object created or modified"
    )
    error_type: str | None = Field(
        default=None, description="Error category: 'validation', 'runtime', 'geometry'"
    )


class OperationCatalog(BaseModel):
    """Catalog of available operations"""

    operations_by_category: dict[str, list[str]] = Field(
        description="Operation names organized by category"
    )
    total_count: int = Field(ge=0, description="Total number of operations")
