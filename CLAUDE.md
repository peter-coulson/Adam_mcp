# adam-mcp

Minimal MCP server exposing CAD operations for FreeCAD through the Model Context Protocol.

## MVP Scope

**Target:** Engineering-grade machine parts (pipe flanges, washers, nuts, bolts)
**Demo Success Criteria:**
- **Part 1 (Creation):** "Create 4-inch Class 150 pipe flange" → Complete ISO 7005 flange in ~2 minutes
- **Part 2 (Modification):** "Modify M3 nyloc nut properties" → Edit pre-existing complex part beyond current creation capabilities

**Why This Demo:**
- ✅ Pipe flange looks 100% complete (no threads needed - flanges use bolts)
- ✅ Nyloc nut demonstrates modification of complex parts (uses Revolution, Chamfer, Fusion operations we don't have yet)
- ✅ Both parts fully professional - no visible incompleteness
- ✅ Shows full creation workflow + modification workflow

**Tech Stack:** Python 3.10+, FreeCAD, FastMCP, Pydantic

**Tool Philosophy:** Operation-specific tools with flat parameters (MCP-compatible, no Python fallback)
1. `list_objects()` - Lightweight overview (✅ implemented)
2. `get_object_details(names)` - Rich context on-demand (✅ implemented)
3. Operation tools (one per operation, flat parameters):
   - `create_cylinder_tool()`, `create_pad_tool()`, `create_pocket_tool()`, etc.
   - Each tool has simple, flat parameters (no nested objects)
   - Natural discovery via tool list (no separate discovery tool needed)
   - ~17 tools for MVP, ~32 tools for full feature set

**Workflow Model:** Sequential single-object operations (matches CAD's dependency chain)

## Codebase Structure

**Organized by domain and layer for scalability:**

```
src/adam_mcp/
  ├── core/                          # Infrastructure (stable)
  │   ├── server.py                  # MCP server entry point + tool registration
  │   ├── freecad_env.py             # FreeCAD environment setup
  │   └── working_files.py           # Working file management (auto-save, commit/rollback)
  │
  ├── models/                        # Data models (Pydantic schemas)
  │   ├── base.py                    # BaseOperation, base models
  │   ├── responses.py               # Response models (OperationResult, DocumentInfo, etc.)
  │   └── operations/                # Operation models by category
  │       ├── primitives.py          # CreateBox, CreateCylinder, CreateSphere, etc.
  │       ├── sketches.py            # CreateSketch, SketchGeometry, etc.
  │       ├── features.py            # CreatePad, CreateFillet, CreateChamfer, etc.
  │       ├── booleans.py            # CreateFusion, CreateCut, CreateCommon
  │       └── modifications.py       # ModifyObject
  │
  ├── operations/                    # Business logic (operation implementation)
  │   ├── dispatcher.py              # Route operation.action → handler
  │   ├── handlers/                  # Handler implementations by category
  │   │   ├── primitives.py          # execute_create_box, execute_create_cylinder, etc.
  │   │   ├── sketches.py            # execute_create_sketch, etc.
  │   │   ├── features.py            # execute_create_pad, execute_create_fillet, etc.
  │   │   ├── booleans.py            # execute_create_fusion, etc.
  │   │   └── modifications.py       # execute_modify_object
  │   └── validators/                # Operation-specific validation
  │       ├── geometry.py            # Geometric validation (fillet radius, edge checks)
  │       └── references.py          # Object reference validation
  │
  ├── tools/                         # MCP tools (exposed to Claude via FastMCP)
  │   ├── document.py                # Document management (open, create, commit, rollback)
  │   ├── query.py                   # Query tools (list_objects, get_object_details) ✅
  │   ├── discovery.py               # Discovery tool (list_available_operations)
  │   └── execution.py               # Standard operation execution (execute_standard_operation)
  │
  ├── constants/                     # Configuration organized by domain
  │   ├── dimensions.py              # Dimension constraints (MIN_DIMENSION_MM, etc.)
  │   ├── messages.py                # Error/success message templates
  │   ├── paths.py                   # File paths, environment variables
  │   └── operations.py              # Operation categories, operation lists
  │
  ├── utils/                         # Helper functions
  │   ├── errors.py                  # Error formatting
  │   ├── validation.py              # General validation (validate_dimension, validate_document)
  │   ├── paths.py                   # Path utilities (resolve_project_path, etc.)
  │   └── freecad.py                 # FreeCAD utilities (get_version, get_active_document)
  │
  └── __init__.py                    # Package metadata
```

**Module Responsibilities:**
- **core/** - Infrastructure (server, FreeCAD setup, working files)
- **models/** - Pydantic schemas for requests/responses
- **operations/** - Business logic for CAD operations (handlers, validators, dispatcher)
- **tools/** - MCP tools exposed to Claude (thin layer calling operations/)
- **constants/** - All constants organized by domain
- **utils/** - General-purpose helper functions

**Design principles:**
- Each file has single responsibility
- Average file size: 50-250 LOC
- Clear separation: data (models) → logic (operations) → interface (tools)
- Manual validation via FreeCAD GUI (tests excluded for MVP speed-to-demo)

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
- **Structured operations only** - All operations use JSON with Pydantic validation (better errors, type safety, pre-execution validation)
- **No Python fallback** - Forces proper operation design. Expand structured operations incrementally as needed (see context/DECISIONS.md for rationale)
- **Operation boundary** - One operation = create/modify ONE object (can set multiple properties)
- **Sequential operations** - One focused operation at a time (matches CAD dependency chain)
- **Modular structure** - server.py is a slim entry point. Infrastructure extracted into focused modules

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
- Structured operations only (no script execution)
- Pydantic validation before FreeCAD execution (catch errors early)
- Geometry validation after execution (ensure valid shapes)
- No sandboxing needed (no arbitrary code execution)

**Constants & Configuration:**
- ALL constants live in `constants.py` - single source of truth
- No magic numbers or duplicate strings anywhere in the codebase
- Use named constants for dimensions, tolerances, messages, paths

**Tool Design:**
- **Flat, operation-specific tools** - One tool per operation (create_cylinder, create_pad, etc.)
- **Simple parameters** - All params flat (no nested objects) for MCP compatibility
- **Natural discovery** - Tool list provides discovery (no separate discovery tool)
- **Sequential workflow** - Inspect → operate → inspect → operate (one object at a time)
- **3-layer validation** - Pydantic (types/ranges) → Semantic (existence/constraints) → Geometry (valid shapes)
- **Clear separation** - Create operations vs Modify operations (separate tools)
- Tool implementations in `tools/execution.py` (one function per operation)
- FastMCP registration only in `server.py` (one @mcp.tool() per operation)
- Scales well (~17 MVP tools, ~32 full feature set)

## Critical Workflow Rules

- **Always run pre-commit** - `uv run pre-commit run --all-files` after writing code
- **Never commit** - Commits are ALWAYS managed by the user (no exceptions)

## Quality Checklist (before marking work complete)

1. ✓ No magic numbers or duplicate strings? (ALL constants in `constants/`)
2. ✓ Tool validated with real example via FreeCAD GUI (e.g., pipe flange creation)?
3. ✓ Error messages explain what went wrong + how to fix?
4. ✓ Type hints on all functions? (mypy must pass)
5. ✓ Tool docstrings clear for Claude to understand?
6. ✓ Each module has one clear purpose?
7. ✓ Pydantic validation catches parameter errors before execution?
8. ✓ Geometry validation catches invalid shapes after execution?
9. ✓ Imports use TYPE_CHECKING for FreeCAD?

## Documentation

**`CLAUDE.md`** - This file (project principles and standards)
**`context/`** - Strategic decisions and architecture rationale
  - `README.md` - Context system governance (size limits, content principles)
  - `DECISIONS.md` - Technical and architectural choices
  - `WORKFLOW.md` - User experience and workflow architecture
