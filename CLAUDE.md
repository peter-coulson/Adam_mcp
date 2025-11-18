# adam-mcp

Minimal MCP server exposing CAD operations for FreeCAD through the Model Context Protocol.

## MVP Scope

**Target:** Engineering-grade machine parts (bolts, nuts, flanges, gears)
**Success:** "Create M10×40 hex bolt" → Accurate ISO bolt in seconds
**Tech Stack:** Python 3.10+, FreeCAD, FastMCP, Pydantic

**Tool Philosophy:** 3 generalized tools (not 10-20 specialized tools)
1. `list_objects()` - Lightweight overview
2. `get_object_details(names)` - Rich context on-demand
3. `execute_cad_operation(code, description)` - All create/update/delete operations

**Workflow Model:** Sequential single-object operations (matches CAD's dependency chain)

## Codebase Structure

```
src/adam_mcp/
  ├── __init__.py           # Package metadata
  ├── server.py             # Entry point + tool registration
  ├── constants.py          # All constants (dimensions, messages, paths)
  ├── models.py             # Pydantic models for type-safe data
  ├── utils.py              # Core utilities (validation, error formatting)
  ├── working_files.py      # Working file infrastructure (auto-save, commit/rollback)
  ├── freecad_env.py        # FreeCAD environment setup
  └── tools/
      ├── __init__.py
      └── document.py       # Document management tools
      # Future: cad_operations.py (list_objects, get_object_details, execute_cad_operation)
```

**Module Responsibilities:** See context/DECISIONS.md for detailed architecture

## Software Principles

### Universal Principles (apply to ALL code)
- **Simplicity over cleverness** - Obvious code. Refactor early
- **Extreme modularity** - Each module has one reason to change
- **DRY** - No duplicated strings, magic numbers, or logic. Use constants/config. If you copy-paste, extract it
- **Fail fast** - Validate at boundaries
- **Type safety first** - Type hints everywhere, Pydantic for constraints
- **Quality over quantity** - 3-5 excellent tools, not 12 half-baked ones

### Architecture Decisions
- **Direct API integration** - No socket layers, direct FreeCAD imports
- **Generalized tools** - 3 flexible tools that leverage Claude's intelligence, not 10-20 specialized hand-holding tools
- **Sequential operations** - One focused operation at a time (matches CAD dependency chain)
- **Modular structure** - server.py is a slim entry point. Infrastructure extracted into focused modules
- **Sandboxed execution** - FreeCAD scripts run in restricted namespace (FreeCAD modules only, no os/subprocess)

### Implementation Guidance

**Type Safety:**
- Type hints on all function signatures
- Pydantic models for complex parameters with constraints (ranges, relationships)
- Let FastMCP auto-generate schemas from type hints for simple types

**Naming & Documentation:**
- Explicit parameter names with units: `width_mm`, `fillet_radius_mm`, `angle_degrees`
- Tool docstrings become MCP descriptions - make them count
- Document valid ranges in parameter descriptions
- Use CAD terminology consistently

**Error Handling:**
- Validate inputs before calling FreeCAD API
- Error messages explain what went wrong AND how to fix it
  - Good: `"Radius 15.0 exceeds box dimension 10.0. Maximum fillet radius is 5.0"`
  - Bad: `"Invalid radius"`
- Catch and translate FreeCAD exceptions to user-friendly messages

**Security:**
- Sandboxed script execution for CAD operations (restricted namespace, FreeCAD only)
- This is trusted execution environment (like Jupyter) - different from general exec() prohibition
- Time limits (10s per operation)
- Validation after execution (geometry checks)

**Constants & Configuration:**
- ALL constants live in `constants.py` - single source of truth
- No magic numbers or duplicate strings anywhere in the codebase
- Use named constants for dimensions, tolerances, messages, paths

**Tool Design:**
- Write focused, single-object operations (not batch scripts)
- Sequential workflow (inspect → operate → inspect → operate)
- Fetch details on-demand (token efficient)
- Claude writes FreeCAD Python code directly (leverages core competency)
- Tool implementations in `tools/` directory (document.py, cad_operations.py)
- FastMCP registration only in `server.py`

## Critical Workflow Rules

- **Always run pre-commit** - `uv run pre-commit run --all-files` after writing code
- **Never commit** - Commits are ALWAYS managed by the user (no exceptions)

## Quality Checklist (before marking work complete)

1. ✓ No magic numbers or duplicate strings? (ALL constants in `constants.py`)
2. ✓ Tool tested with real example (e.g., M10 bolt creation)?
3. ✓ Error messages explain what went wrong + how to fix?
4. ✓ Type hints on all functions? (mypy must pass)
5. ✓ Tool docstrings clear for Claude to understand?
6. ✓ Each module has one clear purpose?
7. ✓ Sandboxing works (restricted namespace, time limits)?
8. ✓ Validation catches geometry errors?
9. ✓ Imports use TYPE_CHECKING for FreeCAD?

## Documentation

**`CLAUDE.md`** - This file (project principles and standards)
**`context/`** - Strategic decisions and architecture rationale
  - `README.md` - Context system governance (size limits, content principles)
  - `DECISIONS.md` - Technical and architectural choices
  - `WORKFLOW.md` - User experience and workflow architecture
