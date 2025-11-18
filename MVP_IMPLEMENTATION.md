# MVP Implementation Plan

Implementation plan for adam-mcp MVP (8 core structured operations + lightweight discovery).

**IMPORTANT:** See **DEMO_PLAN.md** for complete demonstration strategy and rationale for operation selection.

---

## MVP Scope

**Goal:** Demonstrate two key value propositions through M10 bolt + washer creation

**Success Criteria:**
- **Creation from scratch:** M10×40 bolt using primitive operations (cylinder + fusion + fillet)
- **Intelligent editing:** Claude inspects bolt, adds threads based on discovered dimensions
- **Sketch-based workflow:** M10 washer using sketch operations (sketch + pad + pocket)
- **Context discovery:** Claude verifies washer fits bolt through dimensional inspection
- Clear error messages with recovery guidance

**Design Rationale:** Operations chosen specifically to demonstrate both primitive-based and sketch-based workflows, plus intelligent context discovery. See DEMO_PLAN.md for detailed demonstration flow and context/DECISIONS.md for architectural rationale.

**Tools:** 4 total
1. `list_objects()` - List objects in document (✅ implemented)
2. `get_object_details(names)` - Get object details (✅ implemented)
3. `list_available_operations(category)` - Discover operations by category (planned)
4. `execute_standard_operation(operation)` - Execute JSON operation with 8 MVP ops (planned)

---

## Prerequisites

**IMPORTANT: Complete structure migration before implementing MVP**

Before implementing MVP operations, migrate to the new scalable structure:
1. Follow steps in **MIGRATION_PLAN.md** to reorganize codebase
2. Verify existing tools (list_objects, get_object_details) work after migration
3. Verify imports and run pre-commit hooks

**New structure provides:**
- Clear location for each operation category
- ~100-150 LOC per file (manageable)
- Easy to find and add operations
- Modular organization ready for expansion

**Note:** Tests deliberately excluded from MVP scope. Manual validation via FreeCAD GUI prioritized for speed-to-demo.

---

## Implementation Order

### Phase 1: Operation Models (models/operations/)

**Define MVP operation Pydantic models with rich descriptions and examples (~300 LOC across 4 files)**

**Key principle:** Make auto-generated JSON schema as helpful as possible through rich docstrings and field descriptions. Include usage examples in model docstrings.

**MVP Operations (8 total):** Minimal set for M10 bolt + washer demo (see DEMO_PLAN.md)
- Primitives: Cylinder (bolt shaft/head)
- Sketches: CreateSketch, AddSketchCircle (washer profile/hole)
- Features: Pad, Pocket, Fillet, Thread (washer body/hole, rounding, bolt threads)
- Booleans: Fusion (combine bolt shaft + head)

**File locations:**
- `models/base.py` - BaseOperation (~30 LOC)
- `models/operations/primitives.py` - 1 primitive model: CreateCylinder (~25 LOC)
- `models/operations/sketches.py` - 2 sketch models: CreateSketch, AddSketchCircle (~50 LOC)
- `models/operations/features.py` - 4 feature models: CreatePad, CreatePocket, CreateFillet, CreateThread (~110 LOC)
- `models/operations/booleans.py` - 1 boolean model: CreateFusion (~20 LOC)

#### 1.1 Base Models

```python
class BaseOperation(BaseModel):
    """Base for all operations"""
    description: str = Field(description="Human-readable description")

class OperationResult(BaseModel):
    """Result from operation execution"""
    success: bool
    message: str
    affected_object: str | None = None
    error_type: str | None = None  # 'validation', 'runtime', 'geometry'
```

#### 1.2 Primitive Operations (1 model for MVP)

```python
class CreateCylinder(BaseOperation):
    """
    Create a cylindrical primitive.

    Example:
        {
            "action": "create_cylinder",
            "name": "Shaft",
            "radius": 5,
            "height": 40,
            "description": "M10 bolt shaft"
        }

    Note: Use angle < 360 for partial cylinder (e.g., 180 for half-cylinder)
    """
    action: Literal["create_cylinder"] = Field(
        default="create_cylinder",
        description="Operation type (always 'create_cylinder')"
    )
    name: str = Field(
        max_length=100,
        description="Object name (must be unique in document)"
    )
    radius: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description="Radius in mm (range: 0.1-10000)"
    )
    height: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description="Height in mm (range: 0.1-10000)"
    )
    position: tuple[float, float, float] = Field(
        default=(0, 0, 0),
        description="Position (x, y, z) in mm. Optional, defaults to origin."
    )
    angle: float = Field(
        default=360,
        gt=0,
        le=360,
        description="Sweep angle in degrees (0-360). Default 360 for full cylinder."
    )

# CreateSphere, CreateCone, CreateTorus, CreateBox - Post-MVP (add when needed)
```

#### 1.3 Sketch Operations (2 models for MVP)

```python
class CreateSketch(BaseOperation):
    """
    Create a 2D sketch on specified plane.

    Example:
        {
            "action": "create_sketch",
            "name": "WasherProfile",
            "plane": "XY",
            "description": "Sketch for washer outer profile"
        }
    """
    action: Literal["create_sketch"] = "create_sketch"
    name: str = Field(max_length=100, description="Sketch name (must be unique)")
    plane: Literal["XY", "XZ", "YZ"] = Field(
        default="XY",
        description="Plane to sketch on. XY = top view, XZ = front view, YZ = side view"
    )

class AddSketchCircle(BaseOperation):
    """
    Add circle to existing sketch.

    Example:
        {
            "action": "add_sketch_circle",
            "sketch_name": "WasherProfile",
            "center": [0, 0],
            "radius": 10,
            "description": "20mm diameter washer outer circle"
        }
    """
    action: Literal["add_sketch_circle"] = "add_sketch_circle"
    sketch_name: str = Field(description="Name of sketch to add circle to")
    center: tuple[float, float] = Field(description="Circle center (x, y) in mm")
    radius: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description="Circle radius in mm (range: 0.1-10000)"
    )

# AddSketchLine, AddSketchArc, AddSketchRectangle, AddSketchConstraint - Post-MVP (add when needed)
```

#### 1.4 PartDesign Operations (4 models for MVP)

```python
class CreatePad(BaseOperation):
    """
    Extrude a sketch into a solid (PartDesign Pad feature).

    Example:
        {
            "action": "create_pad",
            "name": "Pad",
            "sketch": "Sketch",
            "length": 10,
            "description": "Extrude sketch 10mm"
        }

    Prerequisites: Sketch must be closed. Use list_objects() to find sketch names.
    """
    action: Literal["create_pad"] = Field(
        default="create_pad",
        description="Operation type (always 'create_pad')"
    )
    name: str = Field(
        max_length=100,
        description="Name for the pad feature"
    )
    sketch: str = Field(
        description="Name of sketch to extrude (must be closed sketch)"
    )
    length: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description="Extrusion length in mm (range: 0.1-10000)"
    )
    reversed: bool = Field(
        default=False,
        description="Extrude in opposite direction. Default: false"
    )

class CreateFillet(BaseOperation):
    """
    Round edges with specified radius.

    Example:
        {
            "action": "create_fillet",
            "name": "Fillet",
            "base": "Box",
            "edges": [0, 2, 4, 6],
            "radius": 2,
            "description": "Round top edges 2mm"
        }

    Prerequisites:
    - Use get_object_details() to identify edge indices
    - Radius must not exceed edge length (validation will check this)
    """
    action: Literal["create_fillet"] = Field(
        default="create_fillet",
        description="Operation type (always 'create_fillet')"
    )
    name: str = Field(
        max_length=100,
        description="Name for the fillet feature"
    )
    base: str = Field(
        description="Name of object to fillet"
    )
    edges: list[int] = Field(
        description="Edge indices to fillet (use get_object_details() to identify)"
    )
    radius: float = Field(
        gt=MIN_FILLET_RADIUS_MM,
        lt=MAX_FILLET_RADIUS_MM,
        description="Fillet radius in mm (range: 0.1-1000). Must not exceed edge length."
    )

class CreatePocket(BaseOperation):
    """
    Cut material from solid using sketch profile (PartDesign Pocket feature).

    Example:
        {
            "action": "create_pocket",
            "name": "Hole",
            "sketch": "HoleProfile",
            "length": 10,
            "description": "Cut through 10mm"
        }

    Prerequisites: Sketch must be closed. Use for cutting holes, slots, etc.
    """
    action: Literal["create_pocket"] = "create_pocket"
    name: str = Field(max_length=100, description="Name for the pocket feature")
    sketch: str = Field(description="Name of sketch profile to cut (must be closed)")
    length: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description="Cut depth in mm (range: 0.1-10000)"
    )
    reversed: bool = Field(
        default=False,
        description="Cut in opposite direction. Default: false"
    )

class CreateThread(BaseOperation):
    """
    Add ISO metric threads to cylindrical surface.

    Example:
        {
            "action": "create_thread",
            "name": "ThreadedBolt",
            "base": "Bolt",
            "face_index": 2,
            "thread_type": "M10",
            "length": 30,
            "description": "Add M10 threads to bolt shaft"
        }

    Prerequisites: Base object must have cylindrical surface. Use get_object_details() to identify face indices.
    """
    action: Literal["create_thread"] = "create_thread"
    name: str = Field(max_length=100, description="Name for threaded object")
    base: str = Field(description="Name of object to add threads to")
    face_index: int = Field(
        ge=0,
        description="Index of cylindrical face to thread (use get_object_details())"
    )
    thread_type: str = Field(
        description="ISO thread designation (e.g., 'M10', 'M8', 'M6')"
    )
    length: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description="Thread length in mm (range: 0.1-10000)"
    )

# CreateRevolution, CreateHole, CreateChamfer - Post-MVP (add when needed)
```

#### 1.5 Boolean Operations (1 model for MVP)

```python
class CreateFusion(BaseOperation):
    """
    Union of two shapes (boolean fusion).

    Example:
        {
            "action": "create_fusion",
            "name": "BoltBody",
            "base": "Shaft",
            "tool": "Head",
            "description": "Combine shaft and head into single bolt body"
        }

    Prerequisites: Both base and tool objects must exist. Result is a single unified shape.
    """
    action: Literal["create_fusion"] = "create_fusion"
    name: str = Field(max_length=100, description="Name for fused object")
    base: str = Field(description="First object name")
    tool: str = Field(description="Second object name to fuse with base")

# CreateCut, CreateCommon (intersection) - Post-MVP (add when needed)
```

#### 1.6 Union Type

```python
Operation = (
    CreateCylinder |
    CreateSketch | AddSketchCircle |
    CreatePad | CreatePocket | CreateFillet | CreateThread |
    CreateFusion
)
```

**Deliverable:** 8 MVP operation models with validation and rich descriptions

**Post-MVP expansions:**
- Additional primitives (Sphere, Cone, Torus)
- Additional sketch geometry (Line, Arc, Rectangle, Polygon)
- Additional features (Revolution, Hole, Draft, Loft)
- Additional booleans (Common/Intersection)
- Modifications (ModifyObject for property updates)
- Patterns (Linear, Polar, Mirror)/examples

---

### Phase 1.5: Lightweight Discovery Tool (tools/discovery.py)

**Implement minimal operation discovery (~50 LOC)**

**File location:** `tools/discovery.py`

```python
class OperationCatalog(BaseModel):
    """Catalog of available operations by category"""
    operations_by_category: dict[str, list[str]] = Field(
        description="Operation names organized by category"
    )
    total_count: int = Field(description="Total number of operations")

def list_available_operations(
    category: Literal["all", "primitives", "sketches", "features", "booleans", "modifications"] | None = None
) -> OperationCatalog:
    """
    List available CAD operation names organized by category.

    Use this to discover which operations exist and browse by category.
    For detailed parameter information, refer to the execute_standard_operation
    tool schema which contains complete documentation for each operation type.

    Args:
        category: Filter by category, or None/"all" for complete list

    Returns:
        Operation names organized by category

    Example:
        list_available_operations(category="primitives")
        → {"primitives": ["create_box", "create_cylinder", ...]}
    """
    operations_by_category = {
        "primitives": [
            "create_box", "create_cylinder", "create_sphere",
            "create_cone", "create_torus"
        ],
        "sketches": [
            "create_sketch", "add_sketch_line", "add_sketch_circle",
            "add_sketch_arc", "add_sketch_constraint"
        ],
        "features": [
            "create_pad", "create_pocket", "create_revolution",
            "create_fillet", "create_chamfer", "create_hole", "create_thread"
        ],
        "booleans": [
            "create_fusion", "create_cut", "create_common"
        ],
        "modifications": [
            "modify_object"
        ]
    }

    if category and category != "all":
        filtered = {category: operations_by_category.get(category, [])}
        total = len(filtered.get(category, []))
        return OperationCatalog(
            operations_by_category=filtered,
            total_count=total
        )

    total = sum(len(ops) for ops in operations_by_category.values())
    return OperationCatalog(
        operations_by_category=operations_by_category,
        total_count=total
    )
```

**Benefits:**
- Token efficient: ~100 tokens per call (just operation names)
- Enables browsing by category
- Parameter details come from cached schema (no duplication)
- Always in sync (just maintains list of names)

**Deliverable:** Lightweight discovery tool (~50 LOC)

---

### Phase 2: Execution Engine (operations/)

**Implement operation execution with 3-layer validation (~450 LOC across files)**

**File locations:**
- `operations/dispatcher.py` - Operation dispatcher (~80 LOC)
- `operations/handlers/primitives.py` - Primitive handlers (~60 LOC)
- `operations/handlers/sketches.py` - Sketch handlers (~80 LOC)
- `operations/handlers/features.py` - Feature handlers (~150 LOC)
- `operations/handlers/booleans.py` - Boolean handlers (~50 LOC)
- `operations/validators/geometry.py` - Geometric validation (~100 LOC)
- `operations/validators/references.py` - Reference validation (~80 LOC)

#### 2.1 Validation Utilities (operations/validators/)

```python
def validate_object_exists(doc, name: str) -> bool:
    """Check if object exists in document"""
    return doc.getObject(name) is not None

def validate_fillet_radius(doc, base_name: str, edges: list[int], radius: float) -> tuple[bool, str]:
    """Validate fillet radius doesn't exceed edge dimensions"""
    # Get object, check each edge length vs radius
    # Return (valid, error_message)

def validate_sketch_for_pad(doc, sketch_name: str) -> tuple[bool, str]:
    """Validate sketch is closed and suitable for extrusion"""
    # Check sketch exists, is closed, has valid geometry
```

#### 2.2 Operation Handlers (operations/handlers/)

```python
def _execute_create_box(op: CreateBox, doc) -> str:
    """Execute create_box operation"""
    box = doc.addObject("Part::Box", op.name)
    box.Length = op.length
    box.Width = op.width
    box.Height = op.height
    box.Placement.Base = FreeCAD.Vector(*op.position)
    doc.recompute()
    return op.name

def _execute_create_fillet(op: CreateFillet, doc) -> str:
    """Execute create_fillet with validation"""
    # Validate base object exists
    if not validate_object_exists(doc, op.base):
        raise ValueError(f"Base object '{op.base}' not found")

    # Validate fillet radius
    valid, msg = validate_fillet_radius(doc, op.base, op.edges, op.radius)
    if not valid:
        raise ValueError(msg)

    # Execute operation
    fillet = doc.addObject("Part::Fillet", op.name)
    fillet.Base = doc.getObject(op.base)
    fillet.Edges = [(edge_idx, op.radius) for edge_idx in op.edges]
    doc.recompute()
    return op.name

# ... handlers for all 21 operations
```

#### 2.3 Operation Dispatcher (operations/dispatcher.py)

```python
OPERATION_HANDLERS = {
    "create_box": _execute_create_box,
    "create_cylinder": _execute_create_cylinder,
    "create_sphere": _execute_create_sphere,
    "create_cone": _execute_create_cone,
    "create_torus": _execute_create_torus,
    "create_sketch": _execute_create_sketch,
    "add_sketch_constraint": _execute_add_sketch_constraint,
    "create_pad": _execute_create_pad,
    "create_pocket": _execute_create_pocket,
    "create_revolution": _execute_create_revolution,
    "create_fillet": _execute_create_fillet,
    "create_chamfer": _execute_create_chamfer,
    "create_hole": _execute_create_hole,
    "create_thread": _execute_create_thread,
    "create_fusion": _execute_create_fusion,
    "create_cut": _execute_create_cut,
    "create_common": _execute_create_common,
    "modify_object": _execute_modify_object,
}

def execute_standard_operation(operation: Operation) -> OperationResult:
    """
    Execute a standard CAD operation.

    Performs 3-layer validation:
    1. Pre-execution: Pydantic validates types/ranges (automatic)
    2. Semantic: Custom validation (object existence, geometric constraints)
    3. Post-execution: FreeCAD geometry validation
    """
    try:
        doc = get_active_document()

        # Get handler for this operation type
        handler = OPERATION_HANDLERS.get(operation.action)
        if not handler:
            return OperationResult(
                success=False,
                message=f"Unknown operation: {operation.action}",
                error_type="validation"
            )

        # Execute operation (semantic validation happens inside handler)
        affected_name = handler(operation, doc)

        # Post-execution validation
        if not validate_document(doc):
            return OperationResult(
                success=False,
                message="Operation produced invalid geometry. Rolling back.",
                error_type="geometry"
            )

        return OperationResult(
            success=True,
            message=f"Successfully created/modified {affected_name}",
            affected_object=affected_name
        )

    except ValueError as e:
        # Semantic validation errors
        return OperationResult(
            success=False,
            message=str(e),
            error_type="validation"
        )
    except Exception as e:
        # FreeCAD runtime errors
        return OperationResult(
            success=False,
            message=format_freecad_error(e, "Operation failed"),
            error_type="runtime"
        )
```

**Deliverable:** 8 MVP operations executable with 3-layer validation

---

### Phase 3: Standard Execution Tool (tools/execution.py)

**Wire up standard operation execution (~50 LOC)**

**File location:** `tools/execution.py`

```python
"""Standard CAD operation execution tool"""

from adam_mcp.models.operations import Operation
from adam_mcp.models.responses import OperationResult
from adam_mcp.operations.dispatcher import execute_operation

def execute_standard_operation(operation: Operation) -> OperationResult:
    """
    Execute a standard CAD operation.

    Thin wrapper that calls into operations/dispatcher.py
    """
    return execute_operation(operation)
```

**Deliverable:** Standard execution tool registered and callable

---

### Phase 4: Tool Registration (core/server.py)

**Register tools with FastMCP (~60 LOC)**

**File location:** `core/server.py`

```python
from adam_mcp.tools.query import (
    list_objects,
    get_object_details,
)
from adam_mcp.tools.discovery import list_available_operations
from adam_mcp.tools.execution import execute_standard_operation

@mcp.tool()
def list_available_operations_tool(
    category: Literal["all", "primitives", "sketches", "features", "booleans"] | None = None
) -> OperationCatalog:
    """
    List available CAD operation names organized by category.

    Use this to discover which operations exist. For detailed parameter
    information, refer to the execute_standard_operation tool schema.

    Operations are organized into categories:
    - primitives: Basic shapes (box, cylinder)
    - sketches: 2D sketch creation and geometry
    - features: PartDesign operations (pad, pocket, fillet, chamfer, thread)
    - booleans: Combine shapes (fusion, cut)
    """
    return list_available_operations(category)

@mcp.tool()
def execute_standard_operation_tool(operation: Operation) -> OperationResult:
    """
    Execute a standard CAD operation (create/modify one object).

    Supports 8 MVP operations for M10 bolt + washer demo (see DEMO_PLAN.md):
    - Primitives: cylinder
    - Sketches: create sketch, add circle
    - Features: pad, pocket, fillet, thread
    - Booleans: fusion

    All parameters validated before execution. One operation affects one object.
    See DEMO_PLAN.md for demonstration strategy and context/DECISIONS.md for architectural rationale.
    """
    return execute_standard_operation(operation)
```

**Deliverable:** 4 tools registered and callable via MCP

---

### Phase 5: Constants & Error Messages (constants/)

**Add operation-specific constants (~100 LOC across multiple files)**

**File locations:**
- `constants/dimensions.py` - Dimension constraints
- `constants/messages.py` - Error/success messages
- `constants/operations.py` - Operation categories and lists

```python
# Operation constraints
MIN_EDGE_COUNT = 1
MAX_EDGE_COUNT = 1000
MIN_SKETCH_POINTS = 2
MAX_SKETCH_POINTS = 10000

# Error messages
ERROR_OBJECT_NOT_FOUND = "Object '{name}' not found. Use list_objects() to see available objects."
ERROR_FILLET_RADIUS_EXCEEDS = "Fillet radius {radius}mm exceeds edge length {edge_length}mm. Maximum radius: {max_radius}mm"
ERROR_SKETCH_NOT_CLOSED = "Sketch '{name}' is not closed. Pad/Pocket require closed sketches."
ERROR_INVALID_EDGE_INDEX = "Edge index {index} not found on object '{name}'. Object has {count} edges."

# Success messages
SUCCESS_OPERATION_STANDARD = "Created {object_name} ({operation_type})"
SUCCESS_OPERATION_CUSTOM = "Successfully executed custom operation: {description}"
```

**Deliverable:** All constants and messages extracted

---

## Quality Checklist

Before marking MVP complete:

- [ ] 8 MVP operation models defined with Pydantic validation
- [ ] 8 MVP operation handlers implemented with 3-layer validation
- [ ] 4 tools registered with FastMCP
- [ ] All constants extracted to constants/ (organized by domain)
- [ ] Pre-commit passes (mypy, ruff, formatting)
- [ ] Error messages explain what + how to fix
- [ ] Can create M10 bolt from scratch (primitive workflow)
- [ ] Claude can inspect bolt and add threads (intelligent editing)
- [ ] Can create M10 washer (sketch workflow)
- [ ] Claude can verify washer fits bolt (context discovery)
- [ ] Demo script validated (see DEMO_PLAN.md)
- [ ] Documentation updated (DEMO_PLAN.md, context/DECISIONS.md)

---

## Estimated LOC by Module

**MVP (8 operations):**

| Module | Files | Est. LOC | Notes |
|--------|-------|----------|-------|
| **models/** | 6 | ~235 | 8 operation models with rich descriptions |
| **operations/** | 6 | ~450 | Handlers, validators, dispatcher (reduced scope) |
| **tools/** | 4 | ~350 | Tool implementations (query, discovery, execution, document) |
| **constants/** | 4 | ~200 | Organized constants |
| **core/** | 3 | ~450 | Infrastructure (server, freecad, working_files) |
| **utils/** | 4 | ~300 | Utilities |
| **Total** | **27** | **~1985** | Average ~74 LOC/file |

**Rationale for reduced scope:**
- Focus on demo requirements (M10 bolt + washer)
- Validates both primitive-based and sketch-based workflows
- Demonstrates intelligent context discovery
- Faster implementation, cleaner validation
- See DEMO_PLAN.md for demonstration strategy

**Post-MVP expansions (incremental):**
- Each new operation: ~50 LOC (model + handler + validation)
- Structure scales well - add to existing files
- Estimated final: ~4000-5000 LOC for comprehensive CAD coverage

---

**Last Updated:** 2025-11-18
