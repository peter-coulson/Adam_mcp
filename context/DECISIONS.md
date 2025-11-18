# Architectural Decisions

Key technical choices and rationale for adam-mcp.

---

## MVP Scope

**Target:** Engineering-grade machine parts (bolts, nuts, flanges, gears)

**Rationale:**
- Optimal Claude leverage (complex dimensional relationships, engineering context)
- Clear success criteria (ISO/DIN standards provide objective validation)
- Real engineering value (users need precise parts constantly)
- Token budget comfortable (3-5 parts per session, ~12-15K tokens each)

**NOT targeting:** Simple hobby parts (underutilizes Claude's intelligence, low value)

**Success criteria:**
- "Create M10×40 hex bolt" → Accurate ISO bolt
- "Create M10 hex nut" → Accurate ISO nut
- "Create 100mm flange with 4× M8 holes" → Precise flange
- Graceful error handling with validation + recovery

---

## Tool Philosophy: Generalized over Specialized

**Decision:** 3 generalized tools, not 10-20 specialized tools

**Tools:**
1. **`list_objects()`** - Lightweight overview (names, types, dependencies)
2. **`get_object_details(names)`** - Rich context on-demand (geometry, properties)
3. **`execute_cad_operation(code, description)`** - All create/update/delete operations

**Rationale:**
- Leverages Claude's core strength (writing Python code)
- Maximum flexibility (full FreeCAD API access)
- Dramatically simpler (2-3 tools vs 10-20 specialized tools)
- Less maintenance (no schema mapping for every FreeCAD type)
- Not limited by our tool imagination

**Rejected alternative:** Specialized tools (create_sketch, extrude, fillet, etc.)
- Reason: Hand-holding approach for less capable systems. Claude doesn't need guidance.

---

## Sequential Operations Model

**Decision:** CAD operations are sequential single-object edits, not batch scripts

**Rationale:**
- Matches natural CAD workflow (dependency chain: Sketch → Pad → Fillet)
- Better debugging (know exactly what failed)
- Better visibility (inspect result after each step)
- More conversational (user gives feedback between operations)
- Token efficient (fetch details on-demand, not entire design upfront)

**Pattern:**
1. User: "Create 10mm box"
2. Claude: `list_objects()` → `execute_cad_operation(create box)` → "Created"
3. User: "Make it taller"
4. Claude: `get_object_details(["Pad"])` → `execute_cad_operation(modify height)` → "Increased to 20mm"
5. User: "Add fillet to top edges"
6. Claude: `execute_cad_operation(create fillet)` → "Added 2mm fillet"

**Key insight:** FreeCAD is inherently sequential (objects depend on previous objects). Batch scripts fight this natural structure.

---

## Core Architecture

### Modular Structure

**Decision:** Extract infrastructure into focused modules. Keep `server.py` as slim entry point.

**Modules:**
- `server.py` - MCP tool registration only
- `constants.py` - All constants (single source of truth)
- `models.py` - Pydantic models for type safety
- `utils.py` - Core utilities (validation, error formatting)
- `working_files.py` - Working file infrastructure
- `freecad_env.py` - FreeCAD environment setup
- `tools/` - Tool implementations (document.py, future: cad_operations.py)

**Rationale:** Each module has one clear responsibility. Easier testing, organization, scalability.

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

**Files:**
- Main file (`design.FCStd`) - Stable, committed, git-tracked
- Working file (`design.FCStd.work`) - Experimental, auto-saved, git-ignored

**Workflow:** `open → edit (auto-save every 5 ops) → commit` (or `rollback` if needed)

**Rationale:**
- User control (explicit commit required)
- Crash safety (auto-save preserves work)
- Corruption safety (validation before commit)
- Familiar mental model (git-like: work = staged, main = committed)

**Details:** See WORKFLOW.md

---

## Security

**Sandboxed script execution:**
- Restricted namespace (FreeCAD modules only, no os/subprocess/sys)
- Time limits (10s per operation)
- Validation after execution (geometry checks)
- Explicit user intent (user wants CAD automation)

**Context:** Different from general `exec()` prohibition. This is trusted execution environment (like Jupyter notebooks) for intended CAD operations.

---

## Design Patterns

**Units in parameter names:** All params include suffix (`width_mm`, `angle_degrees`) - eliminates ambiguity

**Error messages:** Explain WHAT went wrong AND HOW to fix it
- Good: "Radius 15.0 exceeds box dimension 10.0. Maximum fillet radius is 5.0"
- Bad: "Invalid radius"

**Constants extraction:** ALL constants in `constants.py` (no magic numbers, no duplicate strings)

**Type hints required:** All functions typed. Use TYPE_CHECKING for FreeCAD imports.

---

## Token Budget

**Context window:** 200K tokens (Claude Sonnet)

**Allocation:**
- System + tools: ~10K
- Conversation history: ~20-30K
- Code + errors: ~10-20K
- CAD design context: ~50-70K max
- Safety margin: ~50K

**Design constraint:** CAD representation must stay under ~50K tokens for comfortable iterative workflow

**Part complexity tiers:**
- Simple primitives: ~2-5K tokens (underutilized)
- Machine parts: ~8-20K tokens (optimal target)
- Complex assemblies: ~30-60K tokens (post-MVP)

---

## Quality Standards

**DRY:** No duplicated strings, magic numbers, or logic. Extract to constants/config.

**Type safety:** Type hints everywhere, Pydantic for constraints

**Fail fast:** Validate at boundaries, clear error messages

**Simplicity:** Obvious code over clever code. Refactor early.

---

## FreeCAD Object Model

**Key concepts:**
- Objects have unique Names (e.g., "Sketch", "Pad001")
- Objects reference each other (e.g., `Pad.Profile = Sketch`)
- Dependency chain (Sketch → Pad → Fillet)
- Changes propagate down chain (`doc.recompute()` after modifications)

**Tool design implication:** Sequential operations match FreeCAD's dependency model naturally.

---

## Refactoring History

### 2025-11-18: Modular Extraction
- **Trigger:** server.py exceeded 609 LOC
- **Action:** Extracted into focused modules
- **Result:** Clear separation of concerns

### 2025-11-18: Tool Philosophy Shift
- **Trigger:** Questioned specialized tools approach
- **Action:** Shifted to generalized tools (3 tools vs 10-20)
- **Result:** Leverages Claude intelligence, simpler codebase

### 2025-11-18: Scope Refinement
- **Trigger:** Analyzed token budgets and use cases
- **Action:** Focused on engineering-grade machine parts
- **Result:** Clear success criteria, optimal Claude capability match

---

**Last Updated:** 2025-11-18
