# Structure Migration Plan

Migration from flat structure to scalable domain-organized structure.

---

## Current Structure (Before Migration)

```
src/adam_mcp/
  ├── __init__.py
  ├── server.py
  ├── constants.py
  ├── models.py
  ├── utils.py
  ├── working_files.py
  ├── freecad_env.py
  └── tools/
      ├── __init__.py
      ├── document.py
      └── cad_operations.py
```

**Current status:**
- ✅ `tools/document.py` - Document management implemented
- ✅ `tools/cad_operations.py` - Query tools (list_objects, get_object_details) implemented
- ✅ `models.py` - Base response models implemented
- ✅ `constants.py` - Basic constants defined
- ✅ `utils.py` - Basic utilities implemented

---

## Target Structure (After Migration)

```
src/adam_mcp/
  ├── core/                          # Infrastructure
  │   ├── __init__.py
  │   ├── server.py
  │   ├── freecad_env.py
  │   └── working_files.py
  ├── models/                        # Data models
  │   ├── __init__.py
  │   ├── base.py
  │   ├── responses.py
  │   └── operations/
  │       ├── __init__.py
  │       ├── primitives.py
  │       ├── sketches.py
  │       ├── features.py
  │       ├── booleans.py
  │       └── modifications.py
  ├── operations/                    # Business logic
  │   ├── __init__.py
  │   ├── dispatcher.py
  │   ├── handlers/
  │   │   ├── __init__.py
  │   │   ├── primitives.py
  │   │   ├── sketches.py
  │   │   ├── features.py
  │   │   ├── booleans.py
  │   │   └── modifications.py
  │   └── validators/
  │       ├── __init__.py
  │       ├── geometry.py
  │       └── references.py
  ├── tools/                         # MCP tools
  │   ├── __init__.py
  │   ├── document.py
  │   ├── query.py
  │   ├── discovery.py
  │   ├── execution.py
  │   └── custom_code.py
  ├── constants/                     # Configuration
  │   ├── __init__.py
  │   ├── dimensions.py
  │   ├── messages.py
  │   ├── paths.py
  │   └── operations.py
  ├── utils/                         # Utilities
  │   ├── __init__.py
  │   ├── errors.py
  │   ├── validation.py
  │   ├── paths.py
  │   └── freecad.py
  └── __init__.py

tests/
  ├── conftest.py
  ├── unit/
  │   ├── models/
  │   ├── operations/
  │   └── utils/
  └── integration/
      ├── test_real_parts.py
      └── test_workflows.py
```

---

## Migration Steps

### Phase 1: Create New Directory Structure

**Command:**
```bash
cd src/adam_mcp

# Create new directories
mkdir -p core
mkdir -p models/operations
mkdir -p operations/{handlers,validators}
mkdir -p constants
mkdir -p utils

# Tools directory already exists, just needs new files
# (tools/ already has __init__.py, document.py, cad_operations.py)

# Create test structure
cd ../../tests
mkdir -p unit/{models,operations,utils}
mkdir -p integration
```

**Create all __init__.py files:**
```bash
cd src/adam_mcp

touch core/__init__.py
touch models/__init__.py
touch models/operations/__init__.py
touch operations/__init__.py
touch operations/handlers/__init__.py
touch operations/validators/__init__.py
touch constants/__init__.py
touch utils/__init__.py

# Tests
cd ../../tests
touch unit/__init__.py
touch unit/models/__init__.py
touch unit/operations/__init__.py
touch unit/utils/__init__.py
touch integration/__init__.py
```

---

### Phase 2: Move and Split Existing Files

#### 2.1 Move Core Infrastructure

**Move without changes:**
```bash
cd src/adam_mcp

# Move server.py to core/
mv server.py core/server.py

# Move freecad_env.py to core/
mv freecad_env.py core/freecad_env.py

# Move working_files.py to core/
mv working_files.py core/working_files.py
```

**Update `core/__init__.py`:**
```python
"""Core infrastructure for adam-mcp"""

from adam_mcp.core.freecad_env import setup_freecad_environment
from adam_mcp.core.server import mcp
from adam_mcp.core.working_files import (
    create_working_file_path,
    get_working_file,
    save_working_file,
)

__all__ = [
    "setup_freecad_environment",
    "mcp",
    "create_working_file_path",
    "get_working_file",
    "save_working_file",
]
```

#### 2.2 Split models.py

**Extract base models → `models/base.py`:**
```python
"""Base models for adam-mcp operations"""

from pydantic import BaseModel, Field

class BaseOperation(BaseModel):
    """Base class for all CAD operations"""
    description: str = Field(description="Human-readable description of operation")
```

**Extract response models → `models/responses.py`:**
```python
"""Response models for adam-mcp tools"""

from pydantic import BaseModel, Field

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    freecad_version: str
    active_document: str | None
    message: str

class DocumentInfo(BaseModel):
    """Document information"""
    name: str
    object_count: int
    objects: list[str]

class OperationResult(BaseModel):
    """Result from CAD operation execution"""
    success: bool
    message: str
    affected_object: str | None = None
    error_type: str | None = None

class OperationCatalog(BaseModel):
    """Catalog of available operations"""
    operations_by_category: dict[str, list[str]]
    total_count: int

# ... other response models (ObjectSummary, ObjectDetail, etc.)
```

**Create placeholder operation models:**
```bash
# These will be implemented during MVP implementation
touch models/operations/primitives.py
touch models/operations/sketches.py
touch models/operations/features.py
touch models/operations/booleans.py
touch models/operations/modifications.py
```

**Update `models/__init__.py`:**
```python
"""Data models for adam-mcp"""

from adam_mcp.models.base import BaseOperation
from adam_mcp.models.responses import (
    HealthCheckResponse,
    DocumentInfo,
    OperationResult,
    OperationCatalog,
    ObjectSummary,
    ObjectDetail,
    # ... all response models
)

# Operation models will be imported when implemented
# from adam_mcp.models.operations.primitives import CreateBox, CreateCylinder, ...

__all__ = [
    "BaseOperation",
    "HealthCheckResponse",
    "DocumentInfo",
    "OperationResult",
    "OperationCatalog",
    # ...
]
```

**Delete old models.py:**
```bash
rm models.py
```

#### 2.3 Split constants.py

**Create `constants/dimensions.py`:**
```python
"""Dimension constraints for CAD operations"""

# Dimension Constraints (mm)
MIN_DIMENSION_MM = 0.1
MAX_DIMENSION_MM = 10000.0
MIN_FILLET_RADIUS_MM = 0.1
MAX_FILLET_RADIUS_MM = 1000.0

# Angular Constraints (degrees)
MIN_ANGLE_DEGREES = -360.0
MAX_ANGLE_DEGREES = 360.0
```

**Create `constants/messages.py`:**
```python
"""Error and success message templates"""

# Error messages
ERROR_NO_ACTIVE_DOC = "No active FreeCAD document. Open or create a document first."
ERROR_NO_OPEN_DOC = "No document open. Use open_document() or create_document() first."
ERROR_FREECAD_API = "FreeCAD API error: {error}. {suggestion}"
ERROR_INVALID_DIMENSION = "Dimension {value} mm is outside valid range ({min_val}-{max_val} mm)"
ERROR_OBJECT_NOT_FOUND = "Object '{name}' not found. Use list_objects() to see available objects."
ERROR_FILLET_RADIUS_EXCEEDS = "Fillet radius {radius}mm exceeds edge length {edge_length}mm. Maximum radius: {max_radius}mm"

# Success messages
SUCCESS_DOC_CREATED = "Created document: {name}"
SUCCESS_DOC_OPENED = "Opened document: {name}"
SUCCESS_OPERATION = "Operation completed successfully"
SUCCESS_CHANGES_COMMITTED = "Changes committed to {path}"
```

**Create `constants/paths.py`:**
```python
"""File paths and environment variables"""

import os

# Default directories
DEFAULT_PROJECTS_DIR = os.environ.get(
    "ADAM_MCP_DEFAULT_DIR",
    "~/Documents/Projects/adam_mcp/dev_projects"
)

# FreeCAD paths (macOS)
MACOS_APP_PATH = "/Applications/FreeCAD.app/Contents"
MACOS_RESOURCES = f"{MACOS_APP_PATH}/Resources"
MACOS_LIB = f"{MACOS_RESOURCES}/lib"
# ... other paths

# Environment variables
ENV_VAR_FREECAD_PATH = "FREECAD_PATH"
ENV_VAR_MACOS_LIBRARY = "DYLD_LIBRARY_PATH"
# ... other env vars
```

**Create `constants/operations.py`:**
```python
"""Operation-specific constants"""

# Operation categories
OPERATION_CATEGORIES = {
    "primitives": ["create_box", "create_cylinder", "create_sphere", "create_cone", "create_torus"],
    "sketches": ["create_sketch", "add_sketch_line", "add_sketch_circle", "add_sketch_arc", "add_sketch_constraint"],
    "features": ["create_pad", "create_pocket", "create_revolution", "create_fillet", "create_chamfer", "create_hole", "create_thread"],
    "booleans": ["create_fusion", "create_cut", "create_common"],
    "modifications": ["modify_object"],
}

# Working file configuration
AUTO_SAVE_INTERVAL = 5
WORK_FILE_SUFFIX = "_work"
VALIDATE_BEFORE_COMMIT = True
```

**Update `constants/__init__.py`:**
```python
"""Constants for adam-mcp"""

from adam_mcp.constants.dimensions import *
from adam_mcp.constants.messages import *
from adam_mcp.constants.paths import *
from adam_mcp.constants.operations import *

# Re-export all constants
__all__ = [
    # Dimensions
    "MIN_DIMENSION_MM",
    "MAX_DIMENSION_MM",
    # ... all constants
]
```

**Delete old constants.py:**
```bash
rm constants.py
```

#### 2.4 Split utils.py

**Create `utils/errors.py`:**
```python
"""Error formatting utilities"""

from adam_mcp.constants.messages import ERROR_FREECAD_API

def format_freecad_error(error: Exception, suggestion: str = "") -> str:
    """Format FreeCAD API error into user-friendly message"""
    if not suggestion:
        suggestion = "Check FreeCAD documentation for valid parameters."
    return ERROR_FREECAD_API.format(error=str(error), suggestion=suggestion)
```

**Create `utils/validation.py`:**
```python
"""Validation utilities"""

from typing import Any
from adam_mcp.constants.dimensions import MIN_DIMENSION_MM, MAX_DIMENSION_MM
from adam_mcp.constants.messages import ERROR_INVALID_DIMENSION

def validate_dimension(value: float, param_name: str) -> None:
    """Validate dimension is within acceptable range"""
    if not (MIN_DIMENSION_MM <= value <= MAX_DIMENSION_MM):
        raise ValueError(
            ERROR_INVALID_DIMENSION.format(
                value=value, min_val=MIN_DIMENSION_MM, max_val=MAX_DIMENSION_MM
            ) + f" (parameter: {param_name})"
        )

def validate_document(doc: Any) -> bool:
    """Validate document is in good state before committing"""
    try:
        doc.recompute()
        if len(doc.Objects) == 0:
            return False
        # ... validation logic
        return True
    except Exception:
        return False
```

**Create `utils/paths.py`:**
```python
"""Path resolution utilities"""

from pathlib import Path
from adam_mcp.constants.paths import DEFAULT_PROJECTS_DIR

def resolve_project_path(path: str) -> str:
    """Resolve project path to absolute path"""
    path_obj = Path(path).expanduser()
    if path_obj.is_absolute():
        return str(path_obj.resolve())
    default_dir = Path(DEFAULT_PROJECTS_DIR).expanduser().resolve()
    return str(default_dir / path_obj)

def ensure_projects_directory() -> Path:
    """Ensure default projects directory exists"""
    projects_dir = Path(DEFAULT_PROJECTS_DIR).expanduser().resolve()
    projects_dir.mkdir(parents=True, exist_ok=True)
    return projects_dir
```

**Create `utils/freecad.py`:**
```python
"""FreeCAD utilities"""

from typing import TYPE_CHECKING, Any
from adam_mcp.constants.messages import ERROR_NO_ACTIVE_DOC

if TYPE_CHECKING:
    import FreeCAD
else:
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]

def get_freecad_version() -> str:
    """Get FreeCAD version string"""
    if FreeCAD is None:
        raise RuntimeError("FreeCAD not initialized")
    version_parts = FreeCAD.Version()[:3]
    return ".".join(version_parts)

def get_active_document() -> Any:
    """Get active FreeCAD document"""
    if FreeCAD is None:
        raise RuntimeError("FreeCAD not initialized")
    doc = FreeCAD.ActiveDocument
    if doc is None:
        raise RuntimeError(ERROR_NO_ACTIVE_DOC)
    return doc
```

**Update `utils/__init__.py`:**
```python
"""Utilities for adam-mcp"""

from adam_mcp.utils.errors import format_freecad_error
from adam_mcp.utils.validation import validate_dimension, validate_document
from adam_mcp.utils.paths import resolve_project_path, ensure_projects_directory
from adam_mcp.utils.freecad import get_freecad_version, get_active_document

__all__ = [
    "format_freecad_error",
    "validate_dimension",
    "validate_document",
    "resolve_project_path",
    "ensure_projects_directory",
    "get_freecad_version",
    "get_active_document",
]
```

**Delete old utils.py:**
```bash
rm utils.py
```

#### 2.5 Split tools/cad_operations.py

**Create `tools/query.py` (move existing query tools):**
```python
"""Query tools for inspecting CAD documents"""

from adam_mcp.models.responses import ObjectListResponse, ObjectDetailsResponse
from adam_mcp.utils.freecad import get_active_document
# ... move list_objects() and get_object_details() here
```

**Create placeholder files for future implementation:**
```bash
touch tools/discovery.py      # list_available_operations
touch tools/execution.py       # execute_standard_operation
touch tools/custom_code.py     # execute_custom_code
```

**Keep `tools/document.py` as-is** (already properly scoped)

**Update `tools/__init__.py`:**
```python
"""MCP tools for adam-mcp"""

from adam_mcp.tools.document import (
    open_document,
    create_document,
    commit_changes,
    rollback_working_changes,
    # ...
)
from adam_mcp.tools.query import (
    list_objects,
    get_object_details,
)

# Will add when implemented:
# from adam_mcp.tools.discovery import list_available_operations
# from adam_mcp.tools.execution import execute_standard_operation
# from adam_mcp.tools.custom_code import execute_custom_code

__all__ = [
    "open_document",
    "create_document",
    "list_objects",
    "get_object_details",
    # ...
]
```

**Delete old tools/cad_operations.py:**
```bash
rm tools/cad_operations.py
```

---

### Phase 3: Update Imports

Update all import statements throughout the codebase:

**Old imports:**
```python
from adam_mcp.models import ObjectSummary
from adam_mcp.constants import MIN_DIMENSION_MM
from adam_mcp.utils import validate_dimension
```

**New imports:**
```python
from adam_mcp.models.responses import ObjectSummary
from adam_mcp.constants.dimensions import MIN_DIMENSION_MM
from adam_mcp.utils.validation import validate_dimension
```

**Files to update:**
- `core/server.py` - Update tool imports
- `core/working_files.py` - Update constant imports
- `tools/document.py` - Update imports from utils/constants
- `tools/query.py` - Update imports from models/utils
- All test files

---

### Phase 4: Update Documentation

**Update CLAUDE.md:**
- Replace "Codebase Structure" section with new structure
- Update module responsibilities

**Update MVP_IMPLEMENTATION.md:**
- Update file paths in all phases
- Reflect new organization

**Update context/DECISIONS.md:**
- Add refactoring history entry for structure migration

---

### Phase 5: Create Placeholder Files for MVP Implementation

**Create stub files with TODOs:**

```python
# models/operations/primitives.py
"""Primitive operation models (Box, Cylinder, Sphere, Cone, Torus)"""

from adam_mcp.models.base import BaseOperation
# TODO: Implement CreateBox, CreateCylinder, etc.

# operations/handlers/primitives.py
"""Handlers for primitive operations"""

# TODO: Implement _execute_create_box, _execute_create_cylinder, etc.

# operations/validators/geometry.py
"""Geometric validation for CAD operations"""

# TODO: Implement validate_fillet_radius, validate_edge_indices, etc.
```

---

### Phase 6: Run Tests and Verify

**Run existing tests:**
```bash
uv run pytest tests/ -v
```

**Verify imports work:**
```bash
uv run python -c "from adam_mcp.models.responses import ObjectSummary; print('✓ Imports working')"
uv run python -c "from adam_mcp.tools.query import list_objects; print('✓ Tools working')"
```

**Run pre-commit:**
```bash
uv run pre-commit run --all-files
```

---

## Migration Checklist

- [ ] Phase 1: Create new directory structure
- [ ] Phase 1: Create all __init__.py files
- [ ] Phase 2.1: Move core files (server, freecad_env, working_files)
- [ ] Phase 2.2: Split models.py into models/{base,responses,operations/}
- [ ] Phase 2.3: Split constants.py into constants/{dimensions,messages,paths,operations}
- [ ] Phase 2.4: Split utils.py into utils/{errors,validation,paths,freecad}
- [ ] Phase 2.5: Split tools/cad_operations.py into tools/{query,discovery,execution,custom_code}
- [ ] Phase 3: Update all imports in existing files
- [ ] Phase 4: Update documentation (CLAUDE.md, MVP_IMPLEMENTATION.md, DECISIONS.md)
- [ ] Phase 5: Create placeholder files for MVP implementation
- [ ] Phase 6: Run tests and verify everything works
- [ ] Phase 6: Run pre-commit hooks
- [ ] Delete old files (models.py, constants.py, utils.py, tools/cad_operations.py)

---

## Post-Migration Benefits

**Before migration:**
- 8 files total
- 2 files with 500-1000+ LOC each
- Unclear where to add new operations

**After migration:**
- 36+ files (more granular)
- Average file size: ~100-150 LOC
- Clear patterns for adding operations
- Easy to navigate and maintain
- Test structure mirrors source structure

---

**Estimated migration time:** 2-3 hours (mostly careful import updates and testing)

**Last Updated:** 2025-11-18
