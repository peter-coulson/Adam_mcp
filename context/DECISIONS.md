# Architectural Decisions

Core technical choices and rationale for adam-mcp.

---

## MVP Scope & Success

**Goal:** Demonstrate sequential creation and iterative modification in a single conversation

**Success criteria:**
- **Part 1 (Creation):** Create elongated spindle shaft (5 stepped cylinders: 80mm × 40mm → 65mm × 80mm → 50mm × 100mm → 35mm × 90mm → 20mm × 70mm)
- **Part 2 (Iteration):** Mirror the spindle to create symmetrical double-sided shaft
- Show 3-layer validation + clear error messages
- Demonstrate conversational workflow (create → inspect → extend)

**Rationale:**
- Spindle demonstrates sequential primitive creation and positioning
- Mirroring shows Claude can analyze and extend existing geometry
- Pure creation workflow (no pre-existing files needed)
- Clear visual progression (stepped diameters, symmetrical result)
- Realistic mechanical component

See **OPERATIONS.md** for implementation status.

---

## Operation Selection: Workflows Over Polish

**Decision:** 8 operations prioritizing core workflows over polish features

**The 8 operations:**
1. CreateCylinder - Simple primitives
2. CreateSketch, AddSketchCircle - Sketch-based workflow
3. CreatePad, CreatePocket - Extrude and cut
4. CreateThread - ISO engineering standards
5. ModifyObject - Property editing (change dimensions post-creation)

**Why these:**
- Covers three workflows: primitive creation, sketch creation, property modification
- Removed CreateFillet (polish), CreateFusion (single-cylinder bolt simpler)
- ModifyObject demonstrates true editing (not just additive operations)
- Real engineering value: ISO standards, mating parts, iterative design

See **OPERATIONS.md** for expansion roadmap.

---

## Core Architecture

### Direct FreeCAD Integration

**Decision:** Import FreeCAD directly, no socket/IPC layer

**Rationale:** Simpler than reference implementations. MCP handles communication. Fewer failure modes.

### Modular Structure

**Organization:** server.py (MCP), tools/ (execution), operations/ (handlers), models/ (schemas), constants/ (single source of truth)

**Rationale:** Single responsibility per module, scalable to 25-30 operations.

**File sizes:** Target ~100-150 LOC per file. Achieved: ~105 LOC average across 24 files.

### Sequential Operations Model

**Decision:** One operation = create/modify ONE FreeCAD object

**Rationale:**
- Matches CAD dependency chain (Sketch → Pad → Fillet)
- Clear error attribution (know exactly what failed)
- Natural debugging (inspect after each step)
- Conversational iteration (create → inspect → modify)

---

## Technology Choices

### FastMCP over mcp-python

**Why:** Auto-generates schemas from type hints, cleaner API, Pydantic integration

### Pydantic for Validation

**Why:** Declarative constraints, auto-generates JSON schema, clear errors, type safety

**3-layer validation:**
1. Pre-execution (Pydantic): Types, ranges, required fields
2. Semantic (Custom): Object existence, geometric constraints
3. Post-execution (FreeCAD): Document recomputes, valid shapes

---

## Working File System

**Decision:** Two-file system (main + work) with explicit commit/rollback

**Files:**
- Main (`design.FCStd`) - Stable, git-tracked
- Working (`design_work.FCStd`) - Experimental, auto-saved every 5 ops

**Workflow:** open → edit → commit (validates first) or rollback

**Rationale:** User control, crash safety, git-like mental model. See **WORKFLOW.md**.

---

## Security Model

**Decision:** Structured operations only (no script execution)

**Approach:**
- All operations pre-defined with type-safe parameters
- Pydantic validation before FreeCAD execution
- Geometry validation after execution
- No arbitrary code execution → no sandboxing needed

---

## Python Fallback - Explicitly Rejected

**Decision:** NO `execute_custom_code()` tool. Structured operations only.

**Rationale:**
1. **Better validation** - Structured operations validate before execution
2. **Better errors** - "Radius 15mm exceeds edge 10mm" vs "Part.fillet failed"
3. **Better discovery** - MCP schema shows what's possible
4. **Forces quality** - Must design proper operations, not escape-hatch code
5. **Simpler security** - No sandboxing needed

**Alternative:** When you need new capability, design it properly:
- Add Pydantic model with validation
- Add handler with semantic checks
- Get all benefits: pre-validation, clear errors, schema, type safety

**If extensive use reveals needs not met:** Consider specialized workbenches (sheet metal, arch, techdraw) with proper structured operations first.

---

## Testing Strategy

**Decision:** Manual validation via FreeCAD GUI only (no automated tests for MVP)

**Rationale:**
- Speed-to-demo prioritized over test infrastructure
- Visual validation sufficient (does spindle look correct?)
- Real-world testing more valuable (create actual industrial parts)
- Small surface area (8 operations) - manageable to validate manually

**Validation approach:**
1. Create test parts via MCP (spindle shaft, mirrored geometry)
2. Open in FreeCAD GUI
3. Verify dimensions, geometry, feature tree
4. Test error handling with invalid inputs

**Post-MVP:** Add tests if production use reveals brittleness.

---

## Design Patterns

**Units in names:** All params suffixed (`width_mm`, `angle_degrees`)
**Error messages:** Explain what + how to fix
**Constants:** ALL in `constants/` (no magic numbers)
**Type hints:** Required everywhere. Use TYPE_CHECKING for FreeCAD imports

---

## Token Budget

**Context window:** 200K tokens (Claude Sonnet 4.5)

**Target:** Machine parts 8-20K tokens optimal, complex assemblies 30-60K post-MVP

**Strategy:** On-demand details (list_objects cheap, get_object_details expensive)

---

**Last Updated:** 2025-11-18
