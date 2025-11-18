# MVP Implementation Plan

Implementation plan for adam-mcp MVP (7 core operations via flat, operation-specific tools).

**IMPORTANT:** See **DEMO_PLAN.md** for complete demonstration strategy and rationale for operation selection.

---

## MVP Scope

**Goal:** Demonstrate three key value propositions through M10 bolt + washer creation and editing

**Success Criteria:**
- **Creation from scratch:** M10×40 bolt using primitive operations (cylinder + threads)
- **Intelligent editing:** Claude inspects washer, modifies properties based on discovered dimensions
- **Sketch-based workflow:** M10 washer using sketch operations (sketch + pad + pocket)
- **Context discovery:** Claude verifies washer fits bolt through dimensional inspection
- **Property modification:** Claude changes object properties (e.g., increase washer thickness for heavy-duty use)
- Clear error messages with recovery guidance

**Design Rationale:** Operations chosen to demonstrate creation, inspection, AND editing workflows. Prioritizes core editing capability over polish features (fillet, fusion). See DEMO_PLAN.md for detailed demonstration flow and context/DECISIONS.md for architectural rationale.

**Tools:** Operation-specific tools (flat parameters for MCP compatibility)
1. `list_objects()` - List objects in document (✅ implemented)
2. `get_object_details(names)` - Get object details (✅ implemented)
3. 7 operation tools with flat parameters (planned):
   - `create_cylinder_tool()` - Create cylindrical primitive (✅ implemented)
   - `create_sketch_tool()` - Create 2D sketch
   - `add_sketch_circle_tool()` - Add circle to sketch
   - `create_pad_tool()` - Extrude sketch into solid
   - `create_pocket_tool()` - Cut material from solid
   - `create_thread_tool()` - Add ISO metric threads
   - `modify_object_tool()` - Modify object properties (e.g., radius, height, length) ⭐ NEW

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

## Incremental Implementation Strategy

**RECOMMENDED:** Implement in 3 iterations with validation checkpoints to catch issues early.

### Iteration 1: Single Operation End-to-End (2-3 hours)
**Goal:** Prove the entire pipeline works with minimal code

**Implement:**
- CreateCylinder model only (~25 LOC)
- OperationResult model (~15 LOC)
- Cylinder handler (~40 LOC)
- Basic dispatcher (~40 LOC)
- Minimal execution tool (~30 LOC)
- Essential constants (~30 LOC)
- Register in server.py (~20 LOC)

**Total: ~200 LOC**

**Validate:**
- Create cylinder via MCP
- Open in FreeCAD GUI, verify dimensions
- Test error handling (negative radius, duplicate names)
- Confirm Pydantic validation works

**Why first:** Validates architecture decisions, discovers integration issues early, fast feedback on validation strategy.

---

### Iteration 2: Sketch Operations (1-2 hours)
**Goal:** Add sketch-based workflow for washer creation

**Implement:**
- CreateSketch, AddSketchCircle models (~50 LOC)
- Sketch handlers (~80 LOC)
- Sketch operation functions (~60 LOC)
- Tool registration (~50 LOC)
- Update dispatcher (~20 LOC)

**Total: ~260 LOC (cumulative: ~460 LOC)**

**Validate:**
- Create sketches via MCP
- Add circles to sketches via MCP
- Verify sketch geometry in FreeCAD GUI
- Test sketch-based workflow

**Why second:** Validates sketch operations, second workflow pattern after primitives.

---

### Iteration 3: Feature Operations + Editing (2-3 hours)
**Goal:** Add remaining operations including core editing capability

**Implement:**
- CreatePad, CreatePocket, CreateThread models (~75 LOC)
- ModifyObject model (~20 LOC)
- Feature handlers (~120 LOC)
- ModifyObject handler (~40 LOC - simpler than features!)
- Validators (references, basic geometry) (~80 LOC)
- Operation functions (~90 LOC)
- Tool registration (~70 LOC)
- Error message templates (~50 LOC)
- Update dispatcher (~30 LOC)

**Total: ~575 LOC (cumulative: ~1,035 LOC)**

**Validate:**
- Run complete demo flow (M10 bolt + washer)
- Test property modification (change washer thickness)
- Verify all operations work in FreeCAD GUI
- Test intelligent editing workflow (inspect → modify)
- Confirm demo success criteria met

**Why last:** Pattern is proven, this completes creation + editing capabilities.

---

**Benefits of incremental approach:**
- Fast validation after each iteration (not 8-10 hours before first test)
- Catch architecture issues early (200 LOC vs 1,000 LOC to rework)
- Clear success criteria for each iteration
- Manageable 2-3 hour chunks vs full-day marathon

---

## Implementation Order

### Phase 1: Operation Models (models/operations/)

**Define MVP operation Pydantic models with rich descriptions and examples (~230 LOC across 4 files)**

**Key principle:** Make auto-generated JSON schema as helpful as possible through rich docstrings and field descriptions. Include usage examples in model docstrings.

**MVP Operations (7 total):** Minimal set for M10 bolt + washer demo with editing (see DEMO_PLAN.md)
- Primitives: CreateCylinder (bolt body)
- Sketches: CreateSketch, AddSketchCircle (washer profile/hole)
- Features: CreatePad, CreatePocket, CreateThread (washer body/hole, bolt threads)
- Modifications: ModifyObject (edit object properties - e.g., change dimensions)

**Removed from original plan:** CreateFillet (polish), CreateFusion (not needed - single cylinder bolt)
**Why:** Prioritize core editing capability over polish features. ModifyObject demonstrates true property modification.

**File locations:**
- `models/base.py` - BaseOperation (~30 LOC) ✅
- `models/operations/primitives.py` - 1 primitive: CreateCylinder (~25 LOC) ✅
- `models/operations/sketches.py` - 2 sketch models: CreateSketch, AddSketchCircle (~50 LOC)
- `models/operations/features.py` - 3 feature models: CreatePad, CreatePocket, CreateThread (~80 LOC)
- `models/operations/modifications.py` - 1 modification model: ModifyObject (~20 LOC)

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

#### 1.6 Modifications (1 model for MVP)

```python
class ModifyObject(BaseOperation):
    """
    Modify properties of existing object.

    Example - Change cylinder dimensions:
        {
            "action": "modify_object",
            "name": "Shaft",
            "property": "Radius",
            "value": 6.0,
            "description": "Increase shaft radius to 6mm"
        }

    Example - Change pad length:
        {
            "action": "modify_object",
            "name": "Washer",
            "property": "Length",
            "value": 4.0,
            "description": "Increase washer thickness for heavy-duty use"
        }

    Note: Property names are FreeCAD-specific. Use get_object_details() to discover available properties.
    """
    action: Literal["modify_object"] = "modify_object"
    name: str = Field(description="Name of object to modify")
    property: str = Field(description="Property name (e.g., 'Radius', 'Height', 'Length')")
    value: float | str | tuple[float, ...] = Field(
        description="New value for property"
    )
```

#### 1.7 Union Type

```python
Operation = (
    CreateCylinder |
    CreateSketch | AddSketchCircle |
    CreatePad | CreatePocket | CreateThread |
    ModifyObject
)
```

**Deliverable:** 7 MVP operation models with validation and rich descriptions

**Post-MVP expansions:**
- Additional primitives (Sphere, Cone, Torus, Box)
- Additional sketch geometry (Line, Arc, Rectangle, Polygon, Constraint)
- Additional features (Revolution, Hole, Draft, Loft, Fillet, Chamfer)
- Booleans (Fusion, Cut, Common/Intersection)
- Advanced modifications (position, rotation, mirroring)
- Patterns (Linear, Polar, Mirror)

---

**Note on Discovery:** No separate discovery tool needed. Tool list provides natural discovery - Claude can see all available operation tools (create_cylinder_tool, create_pad_tool, etc.) directly in the tool list.

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

### Phase 3: Operation Execution Functions (tools/execution.py)

**Create operation-specific functions with flat parameters (~90 LOC per iteration)**

**File location:** `tools/execution.py`

**Design Decision:** Use **flat, operation-specific tools** instead of a unified tool with complex parameters. This solves MCP integration issues where nested Pydantic models get stringified, and makes tools more discoverable and easier to use.

**Pattern:**
```python
"""CAD operation execution functions (one per operation type)"""

from adam_mcp.models.operations.primitives import CreateCylinder
from adam_mcp.models.responses import OperationResult
from adam_mcp.operations.dispatcher import execute_operation

def create_cylinder(
    name: str,
    radius: float,
    height: float,
    description: str,
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    angle: float = 360.0,
) -> OperationResult:
    """
    Create a cylindrical primitive.

    All parameters are flat and simple (no nested objects).
    Function constructs Pydantic model internally and calls dispatcher.
    """
    operation = CreateCylinder(
        name=name,
        radius=radius,
        height=height,
        description=description,
        position=position,
        angle=angle,
    )
    return execute_operation(operation)
```

**Benefits:**
- Simple, flat parameters (work with MCP integration)
- Each operation is self-documenting
- Natural discoverability (search "create cylinder" → finds tool)
- Type-safe (Pydantic validation still happens internally)
- Scales well (~23 tools for full feature set)

**Deliverable:** One function per operation with flat parameters

---

### Phase 4: Tool Registration (core/server.py)

**Register operation-specific tools with FastMCP (~60 LOC per operation)**

**File location:** `core/server.py`

**Pattern:** One MCP tool per operation, each with flat parameters that map directly to function parameters.

```python
from adam_mcp.tools.execution import (
    create_cylinder,
    create_sketch,
    add_sketch_circle,
    create_pad,
    create_pocket,
    create_fillet,
    create_thread,
    create_fusion,
)

@mcp.tool()
def create_cylinder_tool(
    name: str,
    radius: float,
    height: float,
    description: str,
    position: tuple[float, float, float] = (0.0, 0.0, 0.0),
    angle: float = 360.0,
) -> OperationResult:
    """
    Create a cylindrical primitive.

    Args:
        name: Unique object name (max 100 chars)
        radius: Radius in mm (range: 0.1 - 10000)
        height: Height in mm (range: 0.1 - 10000)
        description: Human-readable description
        position: Position (x, y, z) in mm. Defaults to origin.
        angle: Sweep angle 0-360 degrees. Defaults to 360 (full cylinder).

    Example:
        create_cylinder_tool(
            name="Shaft",
            radius=5,
            height=40,
            description="M10 bolt shaft"
        )
    """
    return create_cylinder(name, radius, height, description, position, angle)

# Register tools for all 8 MVP operations following the same pattern
# - create_sketch_tool
# - add_sketch_circle_tool
# - create_pad_tool
# - create_pocket_tool
# - create_fillet_tool
# - create_thread_tool
# - create_fusion_tool
```

**Why this approach:**
- **Works with MCP integration**: Flat parameters don't get stringified
- **Discoverable**: Each operation is a named tool
- **Self-documenting**: Tool name + docstring is clear
- **Type-safe**: FastMCP generates schemas from type hints
- **Scalable**: ~23 tools for full feature set (manageable)

**Discovery tool removed:** Not needed - tool list serves as natural discovery

**Deliverable:** 8 MVP operation tools + 9 infrastructure tools = 17 total tools

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

- [x] 7 MVP operation models defined with Pydantic validation (1/7 complete)
- [ ] 7 MVP operation handlers implemented with 3-layer validation (1/7 complete)
- [ ] 7 operation-specific tools registered with FastMCP (flat parameters) (1/7 complete)
- [x] All constants extracted to constants/ (organized by domain)
- [x] Pre-commit passes (mypy, ruff, formatting)
- [x] Error messages explain what + how to fix
- [ ] Claude can create M10 bolt from scratch via MCP tools (primitive workflow)
- [ ] Claude can inspect bolt and add threads (intelligent editing)
- [ ] Claude can create M10 washer via MCP tools (sketch workflow)
- [ ] Claude can modify washer properties after inspection (core editing workflow) ⭐
- [ ] Claude can verify washer fits bolt (context discovery)
- [ ] Demo flow validated (see DEMO_PLAN.md)
- [x] Documentation updated (MVP_IMPLEMENTATION.md reflects 7 operations with editing)

---

## Estimated LOC by Module

**MVP (7 operations via flat tools, includes editing):**

| Module | Files | Est. LOC | Notes |
|--------|-------|----------|-------|
| **models/** | 5 | ~205 | 7 operation models with rich descriptions |
| **operations/** | 6 | ~400 | Handlers, validators, dispatcher |
| **tools/** | 2 | ~615 | execution.py (~515 LOC for 7 ops), query.py (~100 LOC) |
| **constants/** | 4 | ~200 | Organized constants |
| **core/** | 3 | ~800 | server.py (~550 LOC), freecad_env.py (~100 LOC), working_files.py (~150 LOC) |
| **utils/** | 4 | ~300 | Utilities |
| **Total** | **24** | **~2520** | Average ~105 LOC/file |

**Rationale for operation selection:**
- Focus on core workflows: creation + inspection + **editing**
- Removed CreateFillet (polish), CreateFusion (not needed with single-cylinder bolt)
- Added ModifyObject (core editing capability - change properties after creation)
- Still demonstrates both primitive-based and sketch-based workflows
- **Key improvement:** True editing workflow (inspect → modify) vs just additive operations
- See DEMO_PLAN.md for demonstration strategy

**Post-MVP expansions (incremental):**
- Each new operation: ~75 LOC (model + handler + function + tool registration)
- Flat tools scale well - clear naming patterns (create_*, modify_*)
- Priority additions: CreateFillet, CreateFusion, CreateBox, AddSketchLine, CreateChamfer
- Estimated final: ~4000-5000 LOC for comprehensive CAD coverage (~25-30 operations)
- Natural tool discovery (no separate discovery tool needed)

---

**Last Updated:** 2025-11-18
