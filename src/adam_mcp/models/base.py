"""Base models for adam-mcp operations"""

from pydantic import BaseModel, Field


class BaseOperation(BaseModel):
    """Base class for all CAD operations"""

    description: str = Field(description="Human-readable description of operation")
