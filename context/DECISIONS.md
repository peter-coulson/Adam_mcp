# Architectural Decisions

Key technical choices and rationale for adam-mcp.

---

## Core Architecture

### Modular Architecture

**Decision:** Extract infrastructure into focused modules when boundaries become clear. Keep `server.py` as slim entry point.

**Evolution:** Started with single-file server.py (609 LOC). When LOC exceeded 500 and boundaries became clear, extracted into focused modules: constants, models, utils, working_files, freecad_env, tools/. Each module has one clear responsibility.

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

**Decision:** Two-file system (main + work) with explicit commit/rollback workflow

**Rationale:** Enables safe editing with crash protection, prevents corrupted geometry from being saved, supports undo workflow, gives users control over what becomes "real"

**Details:** See context/WORKFLOW.md for complete workflow architecture

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

**Actions:** Extracted constants, models, utils, working_files, tool implementations into focused modules. Slimmed server.py to just MCP registration.

**Result:** Clear separation of concerns, easier to add new tools, better testability

---

**Last Updated:** 2025-11-18
