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

## Operation Selection: Demo-Driven Approach

**Decision:** 8 operations chosen specifically for demo requirements

**The 8 operations:**
1. **CreateCylinder** - Bolt shaft/head primitives
2. **CreateSketch** - Start 2D sketches (washer profile)
3. **AddSketchCircle** - Circles in sketches (washer outer/inner)
4. **CreatePad** - Extrude sketches (washer body)
5. **CreatePocket** - Cut from solids (washer hole)
6. **CreateFillet** - Round edges (bolt head, washer edges)
7. **CreateThread** - Add ISO threads (bolt shaft)
8. **CreateFusion** - Combine shapes (bolt shaft + head)

**Why these specific operations:**

### Demonstrates Two Workflows
- **Primitive-based** (bolt): Fast creation using basic shapes → fusion → finishing
- **Sketch-based** (washer): Precise 2D sketches → extrude/cut → finishing
- Shows MCP server handles both paradigms without complexity

### Demonstrates Intelligent Context Discovery
- Query tools (`list_objects`, `get_object_details`) already implemented
- Demo Part 2: Claude inspects bolt, discovers M10 dimensions, adds matching threads
- Demo Part 4: Claude verifies washer hole (11mm) fits bolt shaft (10mm) with clearance
- **Key insight:** This isn't just operation execution - Claude understands geometry

### Minimal but Complete
- **Additive:** CreateCylinder, CreatePad, CreateFusion
- **Subtractive:** CreatePocket
- **Finishing:** CreateFillet, CreateThread
- **Foundation:** CreateSketch, AddSketchCircle
- All essential operation types covered without redundancy

### Real Engineering Value
- ISO M10 standard parts (objective validation criteria)
- Mating parts (bolt + washer) show practical workflow
- Demonstrates engineering knowledge (clearances, standards, threads)

**What we intentionally excluded from MVP:**
- ❌ CreateBox - Not needed (primitive workflow covered by CreateCylinder)
- ❌ AddSketchRectangle - Washer uses circles
- ❌ AddSketchConstraint - Parametric design (advanced, post-MVP)
- ❌ CreateChamfer - Redundant with CreateFillet
- ❌ CreateCut - Boolean subtraction (fusion covers boolean demo)
- ❌ Additional primitives (Sphere, Cone, Torus) - Not needed

**Expansion strategy:**
- Add operations as real needs arise (not speculatively)
- Each new operation: ~50 LOC (model + handler + validation)
- Structure scales to 20-30+ operations without refactoring

**Result:**
- Original plan: 12 operations
- Demo-focused: 8 operations (33% less implementation)
- Equally compelling demo, faster validation

---

## Tool Philosophy: Structured Operations Only

**Decision:** 4 tools - structured JSON operations (NO Python fallback)

**Tools:**
1. **`list_objects()`** - Lightweight overview (names, types, dependencies)
2. **`get_object_details(names)`** - Rich context on-demand (geometry, properties)
3. **`list_available_operations(category)`** - Discover operations by category (token-efficient)
4. **`execute_standard_operation(operation)`** - Structured JSON operations with validation

**Rationale for structured operations:**
- Better pre-execution validation (Pydantic catches errors before FreeCAD execution)
- Clearer error messages ("Field 'radius' must be positive" vs FreeCAD runtime errors)
- More token-efficient (JSON more compact than Python boilerplate)
- Type-safe (all parameters validated against schemas)
- Cleaner for common operations (creating primitives, features, booleans)
- Forces proper operation design (no escape hatch to poorly-validated code)

**Rationale for NO Python fallback:**
See "Python Fallback - Explicitly Rejected" section below for detailed reasoning.

**Operation boundary:** One operation = create/modify ONE FreeCAD object. Can set multiple properties, but not create/modify multiple independent objects.

**MVP scope:** 8 core operations (sufficient for M10 bolt + washer demo). Expand incrementally based on real needs. See DEMO_PLAN.md and MVP_IMPLEMENTATION.md

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

**Decision:** Lightweight discovery tool + Rich schema descriptions

**Approach:**
1. **`list_available_operations(category)`** - Returns operation names by category (~100 tokens)
2. **Rich Pydantic descriptions** - Model docstrings with examples, Field descriptions with ranges/units
3. **Leverage MCP schema caching** - Auto-generated schema sent once at connection, not per-call

**Rationale:**
- Token efficient (100 tokens vs 3,800 for full details)
- No information duplication (details in cached schema)
- Enables categorized browsing (primitives, features, booleans, etc.)
- Always in sync (just maintains list of operation names)

**Example workflow:**
```
Claude: list_available_operations(category="features")
        → {"features": ["create_pad", "create_fillet", ...]}
Claude: *Refers to cached schema for create_fillet parameters*
Claude: execute_standard_operation({action: "create_fillet", ...})
```

**Rejected alternative:** Full discovery tool returning all parameters/examples (~3,800 tokens, duplicates schema)

---

## Implementation Status

**Implemented:**
- `list_objects()` - Query document objects (validated on engineering parts)
- `get_object_details()` - Get object details (validated on engineering parts)

**Planned:**
- `list_available_operations(category)` - Discover operations by category (~50 LOC)
- `execute_standard_operation(operation)` - Execute 8 MVP JSON operations (~400 LOC)

**Total MVP tools: 4**
**Total MVP operations: 8** (demo-focused scope, see "Operation Selection" above)

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

**Last Updated:** 2025-11-18
