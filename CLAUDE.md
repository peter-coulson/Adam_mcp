# adam-mcp

Minimal MCP server exposing CAD operations for FreeCAD through the Model Context Protocol.

## Current Scope

**Goal:** 3-5 excellent tools demonstrating sketch → extrude → fillet workflow

**Tech Stack:** Python 3.10+, FreeCAD, FastMCP, Pydantic

## Software Principles

### Universal Principles (apply to ALL code)
- **Simplicity over cleverness** - Obvious code. Refactor early
- **Extreme modularity** - Each module has one reason to change
- **DRY** - No duplicated strings, magic numbers, or logic. Use constants/config. If you copy-paste, extract it
- **Fail fast** - Validate at boundaries
- **Type safety first** - Type hints everywhere, Pydantic for constraints
- **Quality over quantity** - 3-5 excellent tools, not 12 half-baked ones

### Architecture Decisions
- **Direct API integration** - No socket layers, direct FreeCAD imports (simpler than reference implementation)
- **Tool-centric design** - Each tool is self-contained with validation + execution logic
- **Separation of concerns** - MCP tool definitions separate from FreeCAD operations
- **Single-file server** - Keep server under 500 LOC. Extract only when clear module boundaries emerge

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
- Never use `exec()` or `eval()` with user input
- Validate file paths if file operations added
- Limit parameter ranges to prevent resource exhaustion

**Constants & Configuration:**
- Extract repeated values: default tolerances, unit conversions, naming patterns
- No magic numbers in tool code
- FreeCAD API constants in dedicated section

**Tool Design:**
- Idempotent where possible (same inputs → same result)
- Document prerequisites (e.g., "requires active document")
- Return object references for use in subsequent calls
- Progressive enhancement: core demo tools first, extras later

## Quality Checklist (before marking work complete)

1. ✓ No magic numbers or duplicate strings? (extract to constants)
2. ✓ Each tool tested in demo flow (sketch → extrude → fillet)?
3. ✓ Error messages explain what went wrong + how to fix?
4. ✓ Type hints on all functions?
5. ✓ Tool docstrings clear for Claude to understand?
6. ✓ Each module has one clear purpose?
7. ✓ New validation logic extracted if used more than once?

## Documentation

**`CLAUDE.md`** - This file (project principles and standards)
**`context/`** - Strategic decisions and architecture rationale
  - `README.md` - Context system governance (size limits, content principles)
  - `DECISIONS.md` - Key architectural choices (why single-file? why FastMCP?)
