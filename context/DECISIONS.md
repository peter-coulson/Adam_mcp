# Architectural Decisions

Key technical choices and rationale for adam-mcp.

---

## Core Architecture

### Modular Architecture

**Decision:** Extract infrastructure into focused modules when boundaries become clear. Keep `server.py` as slim entry point (~170 LOC).

**Current structure:**
- ✅ `server.py` - Entry point + tool registration only
- ✅ `constants.py` - Single source of truth for all constants
- ✅ `models.py` - Pydantic models for type-safe data
- ✅ `utils.py` - Core reusable utilities (validation, error formatting)
- ✅ `working_files.py` - Working file infrastructure (auto-save, commit/rollback)
- ✅ `freecad_env.py` - Environment setup (platform-specific)
- ✅ `tools/` - Tool implementations organized by category

**Evolution:** Started with single-file server.py (609 LOC). As boundaries became clear and LOC exceeded 500, extracted into focused modules. Each module has one clear responsibility.

**Rationale:** Extreme modularity enables easier testing, clearer organization, and better scalability as more tools are added. server.py remains simple and focused on MCP tool registration.

### Direct FreeCAD Imports

**Decision:** Import FreeCAD directly, no socket/IPC layer

**Rationale:** Simpler than reference implementation, MCP handles communication, stable API, fewer failure modes. Requires FreeCAD in Python env.

---

## Technology Choices

**FastMCP over mcp-python:** Auto-generates schemas from type hints, cleaner API, Pydantic integration, less boilerplate
**Pydantic for validation:** Declarative constraints, auto-generates JSON schema, clear errors, type safety

---

## Design Patterns

**Units in parameter names:** All params include suffix (`width_mm`, `angle_degrees`) - eliminates ambiguity, FreeCAD uses mm internally
**Tool-centric organization:** Each MCP tool self-contained (validation + execution + error handling)
**Error messages:** Explain WHAT went wrong AND HOW to fix it - actionable feedback

---

## Scope Constraints

### 3-5 Tools Only

**Decision:** Focus on sketch → extrude → fillet workflow

**Rationale:** Demonstrates MCP + FreeCAD integration, quality over quantity, 8-hour timeline

### Working File System

**Decision:** Implemented working file system with auto-save, commit/rollback

**Implementation:**
- Main file: User's actual .FCStd file (only modified on commit)
- Working file: .work copy for safe editing (auto-saved every 5 operations)
- Commit: Validates geometry before updating main file
- Rollback: Discards working changes, resets from main file

**Rationale:** Enables safe editing with crash protection, prevents corrupted geometry from being saved, supports undo workflow

---

## Quality Standards

**Constants extraction:** ALL constants in `constants.py` (single source of truth, DRY, no magic numbers)
**Type hints required:** All functions typed for schema generation and error catching. Use TYPE_CHECKING for FreeCAD imports to avoid runtime import issues.
**Modular design:** Each module has one clear responsibility. New tool categories go in `tools/` directory.

---

## FreeCAD API Constraints

**Active document pattern:** Tools check for active document, clear error if missing
**Object references:** Use explicit naming (`sketch_name` parameter) to avoid collisions

---

---

## Refactoring History

### 2025-11-18: Modular Extraction

**Trigger:** server.py exceeded 609 LOC, boundaries between concerns became clear

**Actions:**
- Extracted all constants to `constants.py` (80+ constants)
- Extracted Pydantic models to `models.py`
- Extracted utilities to `utils.py` (validation, error formatting, document helpers)
- Extracted working file infrastructure to `working_files.py` (160 LOC)
- Moved tool implementations to `tools/document.py`
- Slimmed `server.py` to ~170 LOC (just registration)

**Result:** Clear separation of concerns, easier to add new tools, better testability

---

**Last Updated:** 2025-11-18
