# Architectural Decisions

Key technical choices and rationale for adam-mcp.

---

## Core Architecture

### Single-File Server (< 500 LOC)

**Decision:** Keep server in single file `src/adam_mcp/server.py`

**Rationale:**
- Project scope: 3-5 tools only
- MCP server boilerplate + FastMCP is ~50 LOC
- Each tool: ~50-80 LOC (validation + execution)
- Total: ~300-450 LOC fits comfortably in single file
- Easier to understand, debug, and deploy
- Extract to modules only when clear boundaries emerge

**When to split:**
- File exceeds 500 LOC
- Clear module boundaries emerge (e.g., validation library reused >3 times)
- FreeCAD operations become complex enough to warrant separate module

### Direct FreeCAD Imports

**Decision:** Import FreeCAD directly, no socket/IPC layer

**Rationale:**
- Simpler than reference implementation (freecad-mcp-server uses sockets)
- MCP protocol handles client-server communication
- No need for additional abstraction layer
- FreeCAD Python API is stable and well-documented
- Reduces moving parts and failure modes

**Trade-off accepted:** Requires FreeCAD installed in Python environment

---

## Technology Choices

### FastMCP over mcp-python

**Decision:** Use FastMCP framework

**Rationale:**
- Auto-generates MCP schemas from type hints
- Cleaner tool registration API
- Better error handling defaults
- Pydantic integration for validation
- Less boilerplate than raw mcp-python

**See:** `pyproject.toml` for dependency

### Pydantic for Validation

**Decision:** Use Pydantic models for complex parameter validation

**Rationale:**
- Constraints (ranges, relationships) declaratively defined
- Auto-generates JSON schema for MCP
- Clear validation errors
- Type safety

**Pattern:**
```python
from pydantic import BaseModel, Field

class BoxParams(BaseModel):
    width_mm: float = Field(gt=0, le=10000)
    # Full: src/adam_mcp/server.py:XX
```

---

## Design Patterns

### Units in Parameter Names

**Decision:** All parameters include unit suffix (`_mm`, `_degrees`)

**Rationale:**
- Eliminates ambiguity (10mm or 10cm?)
- Self-documenting
- Prevents conversion errors
- FreeCAD API uses mm internally

**Examples:** `width_mm`, `fillet_radius_mm`, `angle_degrees`

### Tool-Centric Organization

**Decision:** Each MCP tool is self-contained (validation + execution)

**Rationale:**
- Clear boundaries
- Easy to test individual tools
- Follows MCP protocol design (tools are units of capability)
- Single Responsibility Principle at tool level

**Structure per tool:**
1. Pydantic model (if complex params)
2. Validation logic
3. FreeCAD API calls
4. Error handling
5. Return value

### Error Message Pattern

**Decision:** Error messages explain WHAT went wrong AND HOW to fix it

**Good:** `"Radius 15.0 exceeds box dimension 10.0. Maximum fillet radius is 5.0"`
**Bad:** `"Invalid radius"`

**Rationale:**
- Claude (and users) need actionable feedback
- Reduces trial-and-error
- Better debugging experience

---

## Scope Constraints

### 3-5 Tools Only

**Decision:** Focus on excellent sketch → extrude → fillet workflow

**Rationale:**
- Demonstrates MCP + FreeCAD integration
- Quality over quantity principle
- 8-hour project timeline
- Easy to expand later if valuable

**Current tools:**
1. Create sketch (planned)
2. Add geometry to sketch (planned)
3. Extrude sketch (planned)
4. Apply fillet (planned)
5. Export document (maybe)

### No File I/O (Initially)

**Decision:** Operations in-memory, manual save via FreeCAD GUI

**Rationale:**
- Simpler security model (no path validation)
- Reduces attack surface
- Focus on CAD operations, not file management
- Can add export tool later if needed

**Future:** Add controlled export if workflow requires it

---

## Quality Standards

### Constants Extraction

**Decision:** All repeated values in constants section

**Rationale:**
- DRY principle
- Easy to tune defaults
- No magic numbers in tool code

**Location:** Top of `src/adam_mcp/server.py`

**Examples:**
```python
# Constants
DEFAULT_SKETCH_NAME = "Sketch"
MAX_DIMENSION_MM = 10000.0
MIN_FILLET_RADIUS_MM = 0.1
```

### Type Hints Required

**Decision:** All function signatures have type hints

**Rationale:**
- FastMCP uses types to generate schemas
- Catches errors at write-time
- Self-documenting
- Better IDE support

**Enforced by:** `/code-check` command

---

## FreeCAD API Constraints

### Document Management

**Observation:** FreeCAD uses active document pattern

**Implication:**
- Tools check for active document
- Clear error if no document exists
- Alternative: Auto-create document on first tool use

**Decision:** TBD during implementation (document in code)

### Object References

**Observation:** FreeCAD objects referenced by name or internal ID

**Implication:**
- Tools return object names for subsequent operations
- Name collisions possible
- Auto-generated names may be non-intuitive

**Decision:** Use explicit naming where possible (`sketch_name` parameter)

---

## Future Considerations

**Not implementing now, but documented for future:**

### Multi-Document Support
If users need multiple documents, add document handle to tool parameters

### File Operations
If export needed, add single export tool with path validation

### Advanced Constraints
Sketch constraints (parallel, perpendicular, etc.) - separate tool or part of add_geometry?

### Undo Support
FreeCAD has undo stack - expose via MCP?

---

**Note:** This is a living document. Update when architectural decisions are made, not for every code change.

**Last Updated:** 2025-11-18
**Lines:** ~140 (under 150 limit ✓)
