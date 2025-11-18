# Architectural Decisions

Key technical choices and rationale for adam-mcp.

---

## MVP Scope

**Target:** Demonstrate two key value propositions through M10 bolt + washer creation

**Success criteria:**
- **Creation from scratch:** M10×40 bolt using primitive operations
- **Intelligent editing:** Claude inspects bolt, adds threads based on discovered dimensions
- **Sketch-based workflow:** M10 washer using sketch operations
- **Context discovery:** Claude verifies washer fits bolt through dimensional inspection
- Graceful error handling with validation + recovery

**Rationale:**
- Original brief required "minimal flow demo" (sketch → extrude → fillet)
- We chose to exceed requirements by demonstrating BOTH creation AND intelligent editing
- M10 bolt + washer shows real engineering value (ISO standards, mating parts)
- Showcases unique MCP value: Claude can **inspect, understand, and modify** designs
- Two workflows (primitive vs sketch) show flexibility without bloat
- See **DEMO_PLAN.md** for complete demonstration strategy

---

## Operation Selection: Core Workflows Over Polish Features

**Decision:** 7 operations prioritizing creation + editing workflows over polish features

**The 7 MVP operations:**
1. **CreateCylinder** - Bolt body (simple primitive)
2. **CreateSketch** - Start 2D sketches (washer profile)
3. **AddSketchCircle** - Circles in sketches (washer outer/inner)
4. **CreatePad** - Extrude sketches (washer body)
5. **CreatePocket** - Cut from solids (washer hole)
6. **CreateThread** - Add ISO threads (bolt shaft)
7. **ModifyObject** - Edit object properties (washer thickness, cylinder dimensions) ⭐ NEW

**Why these specific operations:**

### Demonstrates Three Core Workflows
- **Primitive-based creation** (bolt): Fast creation using basic shapes
- **Sketch-based creation** (washer): Precise 2D sketches → extrude/cut
- **Property modification** (editing): Inspect → Analyze → Modify properties ⭐ NEW
- Shows complete CAD workflow: create, inspect, edit

### Core Editing Capability (ModifyObject)
- **Why added:** Original 8-operation plan had NO editing capability
- All operations were create-only (additive/subtractive), not modify
- Demo claimed "intelligent editing" but only created new objects, never modified existing
- **ModifyObject enables:** Change radius, height, length, position after creation
- **Real workflow:** inspect_washer() → see 2mm thickness → modify to 4mm for heavy-duty
- **Complexity:** ~115 LOC (simpler than CreateFillet at ~150 LOC)
- **Value:** Core editing vs polish feature (fillet, fusion)

### Demonstrates Intelligent Context Discovery
- Query tools (`list_objects`, `get_object_details`) already implemented
- Demo Part 2: Claude inspects bolt, discovers M10 dimensions, adds matching threads
- Demo Part 4: Claude inspects washer, analyzes requirements, **modifies thickness** ⭐
- **Key insight:** Claude can inspect → understand → modify (like human engineer)

### Minimal but Complete
- **Additive:** CreateCylinder, CreatePad
- **Subtractive:** CreatePocket
- **Advanced:** CreateThread (ISO engineering standards)
- **Editing:** ModifyObject (change properties after creation) ⭐
- **Foundation:** CreateSketch, AddSketchCircle
- All essential workflows covered: create primitives, create sketches, edit properties

### Real Engineering Value
- ISO M10 standard parts (objective validation criteria)
- Mating parts (bolt + washer) show practical workflow
- Property modification shows iterative design (create → inspect → refine)
- Demonstrates engineering knowledge (clearances, standards, threads, material specs)

**What we removed to add ModifyObject:**
- ❌ CreateFillet - Polish feature (rounded edges). Nice but not essential for MVP
- ❌ CreateFusion - Boolean union. Not needed (single cylinder bolt simpler than shaft+head fusion)

**What we intentionally excluded from MVP:**
- ❌ CreateBox - Not needed (primitive workflow covered by CreateCylinder)
- ❌ AddSketchRectangle - Washer uses circles
- ❌ AddSketchConstraint - Parametric design (advanced, post-MVP)
- ❌ CreateChamfer - Similar to CreateFillet (polish)
- ❌ CreateCut - Boolean subtraction (CreatePocket covers cutting)
- ❌ Additional primitives (Sphere, Cone, Torus) - Not needed for demo

**Expansion strategy:**
- Add operations as real needs arise (not speculatively)
- Each new operation: ~75 LOC (model + handler + function + tool)
- Priority additions: CreateFillet, CreateFusion, CreateBox, AddSketchLine
- Structure scales to 25-30+ operations without refactoring

**Result:**
- Original plan: 12 operations
- First reduction: 8 operations (removed CreateBox, etc.)
- Final: 7 operations (removed Fillet/Fusion, added ModifyObject)
- **Better demo:** Shows create + inspect + **edit** workflows (not just create)

---

## Tool Philosophy: Operation-Specific Tools with Flat Parameters

**Decision:** Operation-specific tools (one per operation) with flat parameters (NO Python fallback, NO nested objects)

**Tool Architecture:**
1. **`list_objects()`** - Lightweight overview (names, types, dependencies)
2. **`get_object_details(names)`** - Rich context on-demand (geometry, properties)
3. **Operation tools** - One tool per operation with flat parameters:
   - `create_cylinder_tool(name, radius, height, description, position, angle)`
   - `create_pad_tool(name, sketch, length, description, reversed)`
   - `create_fillet_tool(name, base, edges, radius, description)`
   - etc. (~17 tools for MVP, ~32 for full feature set)

**Rationale for flat, operation-specific tools:**

### MCP Integration Compatibility
- **Nested objects get stringified:** MCP/Claude Code integration treats complex nested Pydantic parameters as strings, breaking validation
- **Flat parameters work natively:** Simple types (str, float, list) pass through correctly
- **Tested and verified:** Unified tool approach failed with "not of type 'object'" errors. Flat tools work first time.

### Better Discoverability
- **Natural search:** User thinks "create cylinder" → finds `create_cylinder_tool` directly
- **Self-documenting:** Each tool name describes what it does
- **No discovery tool needed:** Tool list provides natural discovery
- **Clear intent:** `create_cylinder_tool` vs `execute_standard_operation(action="create_cylinder", ...)`

### Type Safety Maintained
- **Pydantic validation still happens:** Functions construct Pydantic models internally
- **3-layer validation preserved:** Pydantic → Semantic → Geometry (unchanged)
- **FastMCP schema generation:** Auto-generates schemas from type hints (flat params)

### Scales Well
- **32 tools for full feature set:** Manageable for Claude (regularly works with 50-100+ tools)
- **Clear naming patterns:** `create_*`, `add_*`, `modify_*` prefixes
- **One tool = one responsibility:** Each tool focused and simple

**Rationale for NO Python fallback:**
See "Python Fallback - Explicitly Rejected" section below for detailed reasoning.

**Operation boundary:** One tool = create/modify ONE FreeCAD object. Can set multiple properties, but not create/modify multiple independent objects.

**MVP scope:** 8 operation tools (sufficient for M10 bolt + washer demo). Expand incrementally based on real needs. See DEMO_PLAN.md and MVP_IMPLEMENTATION.md

---

## Sequential Operations Model

**Decision:** CAD operations are sequential single-object edits, not batch scripts

**Rationale:** Matches natural CAD workflow (dependency chain), better debugging/visibility, conversational iteration, token efficient (on-demand details).

**Example:** Create box → inspect → modify height → add fillet (iterative conversation)

---

## Core Architecture

### Modular Structure

**Modules:** server.py (MCP registration), constants.py (single source of truth), models.py (Pydantic), utils.py (validation/errors), working_files.py, freecad_env.py, tools/ (implementations)

**Rationale:** Single responsibility per module, easier testing/maintenance

### Direct FreeCAD Integration

**Decision:** Import FreeCAD directly, no socket/IPC layer

**Rationale:** Simpler than reference implementations. MCP handles communication. Fewer failure modes.

---

## Technology Choices

**FastMCP over mcp-python:** Auto-generates schemas from type hints, cleaner API, Pydantic integration

**Pydantic for validation:** Declarative constraints, auto-generates JSON schema, clear errors, type safety

---

## Working File System

**Decision:** Two-file system (main + work) with explicit commit/rollback

**Files:** Main (`design.FCStd` - stable, git-tracked) + Working (`design.FCStd.work` - experimental, auto-saved every 5 ops)

**Workflow:** open → edit → commit (validates before updating main) or rollback

**Rationale:** User control, crash/corruption safety, git-like mental model. See WORKFLOW.md

---

## Security

**Structured operations only:** No script execution, Pydantic validation before FreeCAD execution, geometry validation after execution

**No sandboxing needed:** All operations are pre-defined with type-safe parameters. No arbitrary code execution.

---

## Design Patterns

**Units in names:** All params suffixed (`width_mm`, `angle_degrees`)
**Error messages:** Explain what failed + how to fix (e.g., "Radius 15.0 exceeds box 10.0. Max: 5.0")
**Constants:** ALL in `constants.py` (no magic numbers/duplicate strings)
**Type hints:** Required everywhere. Use TYPE_CHECKING for FreeCAD imports

---

## Testing Strategy - Manual Validation Only

**Decision:** No automated tests for MVP. Manual validation via FreeCAD GUI only.

**Rationale:**
- **Speed-to-demo prioritized** - Faster iteration on core functionality without test maintenance overhead
- **Visual validation sufficient** - FreeCAD GUI provides immediate visual feedback (did bolt look correct?)
- **Real-world testing more valuable** - Creating actual M10 bolt, nut, flange validates better than unit tests
- **Simpler debugging** - Open .FCStd file in FreeCAD, inspect geometry directly
- **Test complexity high** - Would need FreeCAD test fixtures, geometry comparison logic, test document management
- **Small surface area** - 4 tools total, ~12 operations for MVP - manageable to validate manually

**Validation approach:**
1. Create test parts via MCP (M10 bolt, nut, flange)
2. Open in FreeCAD GUI
3. Verify dimensions, geometry, feature tree
4. Check error handling with invalid inputs

**Post-MVP consideration:** Add tests if production use reveals brittleness. For demo/prototype, manual validation trades test time for feature velocity.

---

## Token Budget

**Context window:** 200K tokens → ~50K max for CAD design context, ~70K for conversation/code, ~50K safety margin

**Design constraint:** Machine parts (8-20K tokens optimal), complex assemblies post-MVP (30-60K)

---

## FreeCAD Object Model

**Key concepts:** Unique Names, object references (`Pad.Profile = Sketch`), dependency chain (Sketch → Pad → Fillet), propagating changes (`doc.recompute()`)

**Implication:** Sequential operations match FreeCAD's dependency model

---

## Operation Discovery Strategy

**Challenge:** How does Claude discover which operations are available and what parameters they require?

**Decision:** Natural tool list discovery (no separate discovery tool needed)

**Approach:**
1. **Tool list provides discovery** - Claude sees all available tools directly
   - `create_cylinder_tool`, `create_pad_tool`, `create_fillet_tool`, etc.
   - Clear naming pattern (`create_*`, `add_*`, `modify_*`)
   - Tool names are self-documenting
2. **Rich tool docstrings** - Each tool has clear description with examples
3. **FastMCP schema generation** - Auto-generated schemas from type hints
4. **MCP schema caching** - Schemas sent once at connection, not per-call

**Rationale:**
- **No extra tool needed:** Tool list itself is the discovery mechanism
- **More intuitive:** "I want to create a cylinder" → search tool list → find `create_cylinder_tool`
- **No token overhead:** Discovery happens at connection time (schema caching)
- **Always in sync:** Tool registration = available operations (single source of truth)
- **Better than unified tool:** No need to know `action` values or reference separate discovery

**Example workflow:**
```
Claude: *Sees create_cylinder_tool in tool list*
Claude: *Reads cached schema for parameters*
Claude: create_cylinder_tool(name="Shaft", radius=5, height=40, description="...")
```

**Rejected alternatives:**
- Separate `list_available_operations` tool - redundant with tool list
- Unified `execute_standard_operation` with discovery - breaks MCP integration (nested objects)

---

## Implementation Status

**Implemented:**
- `list_objects()` - Query document objects (validated on engineering parts)
- `get_object_details()` - Get object details (validated on engineering parts)
- `create_cylinder_tool()` - Create cylindrical primitive (validated with flat parameters)

**Planned:**
- 7 additional operation tools with flat parameters
  - `create_sketch_tool()`, `add_sketch_circle_tool()`, `create_pad_tool()`
  - `create_pocket_tool()`, `create_fillet_tool()`, `create_thread_tool()`, `create_fusion_tool()`

**Total MVP tools: 17** (9 infrastructure + 8 operations)
**Total full feature tools: 32** (9 infrastructure + ~23 operations)

---

## Python Fallback - Explicitly Rejected

**Decision:** Do NOT implement `execute_custom_code()` Python fallback tool

**Rationale:**

### 1. Suboptimal Validation
- **No pre-execution validation:** Cannot check parameters before FreeCAD executes them
- **Runtime failures only:** Errors discovered during execution, not before
- **Poor user experience:** "Part.fillet failed" vs "Radius 15mm exceeds edge length 10mm. Maximum: 5mm"

### 2. No Schema Benefits
- **Not introspectable:** MCP clients cannot discover what operations are possible
- **No auto-generated docs:** Structured operations provide rich schemas with examples
- **Manual documentation burden:** Must document Python API separately

### 3. Against MCP Tool Philosophy
- **MCP tools should be well-defined operations:** Clear inputs/outputs, not generic programming
- **Defeats structured approach:** Why design proper operations if there's an escape hatch?
- **Worse developer experience:** Writing Python code strings vs structured JSON

### 4. Security Complexity Without Benefit
- **Sandboxing required:** Restricted namespace, timeout limits, forbidden pattern checking
- **Complexity cost:** ~200 LOC for sandboxing that delivers inferior UX
- **For what?:** Allowing users to write worse code than our structured operations

### 5. Forces Proper Design
- **Without escape hatch:** Must design operations properly with validation
- **Better long-term:** Each new need drives proper operation design
- **Quality over convenience:** Better to have 12 excellent operations than 12 + "write any Python"

### 6. Can Add Later If Truly Needed
- **Not irreversible:** Can implement if we discover genuinely common unstructured patterns
- **Start strict:** Better to add flexibility later than remove it
- **Exhaust structured approaches first:** Force ourselves to design proper operations

**Comparison:**

| Aspect | Structured Operation | Python Fallback |
|--------|---------------------|-----------------|
| **Pre-execution validation** | ✅ Pydantic validates types/ranges | ❌ None |
| **Error messages** | ✅ "Radius exceeds edge length. Max: 5mm" | ❌ "Part.fillet failed" |
| **Schema/Discovery** | ✅ Auto-generated, introspectable | ❌ "Execute arbitrary Python" |
| **Type safety** | ✅ Full type hints, compile-time checks | ❌ Runtime failures only |
| **Documentation** | ✅ Examples in schema, rich descriptions | ❌ "See FreeCAD docs" |
| **Security** | ✅ Pydantic validation only | ❌ Needs sandboxing (~200 LOC) |
| **Token efficiency** | ✅ Compact JSON | ❌ Python boilerplate |
| **Motivates quality** | ✅ Forces proper design | ❌ Escape hatch discourages it |

**Alternative approach:** Expand structured operations incrementally
- When new capability needed → design proper operation with validation
- Get all benefits: pre-validation, clear errors, schema, type safety
- Better UX than "write Python code and hope it works"

**Reconsideration criteria:**
- After extensive production use, we discover genuinely common patterns that resist structured modeling
- BUT: Exhaust structured approaches first (parametric operations, composition patterns, etc.)
- High bar: Must demonstrate that structured approach is fundamentally insufficient

---

## Refactoring History

### 2025-11-18: Flat Tools Architecture (MCP Integration Fix)
- **Trigger:** Testing unified `execute_standard_operation_tool(operation: Operation)` failed with "not of type 'object'" validation errors. MCP/Claude Code integration stringified nested Pydantic parameters.
- **Root cause:** Complex nested parameters (Pydantic models) get stringified by MCP integration layer, breaking validation. Flat parameters (str, float, list) work natively.
- **Decision:** Refactor to operation-specific tools with flat parameters. One tool per operation (create_cylinder_tool, create_pad_tool, etc.).
- **Implementation:**
  - `tools/execution.py`: Add operation-specific functions wrapping Pydantic models (~90 LOC per operation)
  - `server.py`: Register individual tools with flat parameters (~60 LOC per operation)
  - Remove discovery tool (tool list provides natural discovery)
- **Rationale:**
  - **MCP compatibility:** Flat parameters work first time, no validation errors
  - **Better discoverability:** Tool names self-documenting (create_cylinder_tool vs execute_standard_operation)
  - **Type safety maintained:** Functions construct Pydantic models internally, 3-layer validation preserved
  - **Scales well:** 32 tools for full feature set is manageable for Claude (regularly works with 50-100+ tools)
  - **Clearer separation:** Create vs modify operations are distinct tools
- **Testing:** Validated create_cylinder_tool with all parameter variations (minimal, optional, error handling)
- **Result:** MVP: 17 tools (9 infrastructure + 8 operations). Full feature set: ~32 tools. Claude can use tools directly without workarounds.
- **Documentation:** Updated MVP_IMPLEMENTATION.md, CLAUDE.md, DECISIONS.md to reflect flat tools design

### 2025-11-18: Demo-Driven Scope Refinement (12 → 8 operations)
- **Trigger:** Reviewing operation list against demo requirements. Asked: "What's the minimal set for a compelling demo?"
- **Analysis:** Original plan had 12 operations including CreateBox, AddSketchConstraint, CreateChamfer, CreateCut. Analyzed which operations are essential for M10 bolt + washer demo.
- **Decision:** Reduce to 8 operations focused on demo requirements
- **Rationale:** Demo needs to showcase BOTH creation and intelligent editing. Bolt + washer demonstrates two workflows (primitive vs sketch), context discovery (inspection), and real engineering value (ISO standards, mating parts). Removed redundant operations (Chamfer ≈ Fillet, Cut not needed with Pocket, Box not needed with Cylinder, Constraint advanced feature).
- **Result:** 8 operations (33% reduction), clearer demo narrative, faster implementation (~1985 LOC vs ~2250 LOC). Operations: CreateCylinder, CreateSketch, AddSketchCircle, CreatePad, CreatePocket, CreateFillet, CreateThread, CreateFusion. See DEMO_PLAN.md for complete strategy.

### 2025-11-18: Python Fallback - Explicitly Rejected
- **Trigger:** During MVP planning review, questioned whether Python fallback adds value
- **Analysis:** Compared validation quality, error messages, schema benefits, security complexity, and philosophy
- **Decision:** Remove Python fallback entirely from MVP and roadmap
- **Rationale:** Forces proper operation design. Structured operations provide better validation, errors, and UX. Security complexity not worth inferior experience. Can add later if truly needed.
- **Result:** 4 tools (not 5), ~12 MVP operations, cleaner architecture. See detailed reasoning above.

### 2025-11-18: MVP Scope Reduction
- **Trigger:** Reviewing MVP_IMPLEMENTATION.md - 21 operations seemed excessive for success criteria
- **Analysis:** M10 bolt, nut, flange only require ~12 operations. 21 is over-specified.
- **Decision:** Reduce MVP to 12 core operations, expand incrementally
- **Rationale:** Faster validation of architecture, learn what's actually needed, ~40% less implementation
- **Result:** MVP delivers success criteria in ~2250 LOC vs ~3860 LOC. Post-MVP expansion driven by real needs.

### 2025-11-18: Execution Strategy - Structured Operations Only
- **Trigger:** Planning operation execution tool. Analyzed Python exec() vs structured JSON approaches
- **Analysis:** Compared validation, safety, token efficiency, flexibility, error quality across real examples
- **Initial decision:** Hybrid approach - structured JSON (90%) + Python fallback (10%)
- **Revised decision:** Structured operations only (100%), no Python fallback
- **Rationale:** Engineering parts use well-defined operations. JSON provides better validation/errors. Python fallback is suboptimal for validation and against MCP tool philosophy.
- **Result:** 4 execution tools (query + discovery + execute). MVP: 12 core operations.

### 2025-11-18: Operation Discovery Strategy
- **Trigger:** Analyzing how Claude discovers available operations. Concerned about token cost of full discovery tool.
- **Analysis:** Compared full discovery tool (~3,800 tokens) vs minimal discovery (~100 tokens) vs schema-only (0 tokens). Considered MCP schema caching behavior.
- **Decision:** Lightweight discovery tool + rich Pydantic descriptions
- **Rationale:** MCP caches schema at connection (sent once). Discovery tool provides categorization without duplicating schema details. Rich docstrings/Field descriptions make auto-generated schema helpful.
- **Result:** 4 total tools. Discovery adds ~100 tokens per call, enables browsing by category. No information duplication.

### 2025-11-18: Codebase Structure Reorganization
- **Trigger:** Concern that flat structure won't scale for MVP (~2250 LOC) and post-MVP expansion (~4000-5000 LOC)
- **Analysis:** Current structure would result in 2 files with 500-1000+ LOC each (models.py, tools/cad_operations.py). Difficult to navigate, unclear where to add operations, no separation of concerns.
- **Decision:** Reorganize by domain and layer - core/, models/, operations/, tools/, constants/, utils/
- **Rationale:** Average file size 50-250 LOC (manageable), clear patterns for adding operations, test structure mirrors source, scales to full feature set without refactoring.
- **Result:** ~27 files organized by responsibility. See MIGRATION_PLAN.md for migration steps. CLAUDE.md updated with new structure.

---

**Last Updated:** 2025-11-18 (flat tools architecture)
