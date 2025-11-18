# Architectural Decisions

Key technical choices and rationale for adam-mcp.

---

## Core Architecture

### Single-File Server (< 500 LOC)

**Decision:** Keep server in `src/adam_mcp/server.py`

**Rationale:** 3-5 tools = ~300-450 LOC, easier to understand/debug/deploy. Split when >500 LOC or clear module boundaries emerge.

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

### No File I/O (Initially)

**Decision:** In-memory operations, manual save via FreeCAD GUI

**Rationale:** Simpler security, focus on CAD operations, can add export later if needed

---

## Quality Standards

**Constants extraction:** All repeated values at top of `server.py` (DRY, no magic numbers)
**Type hints required:** All functions typed for schema generation and error catching

---

## FreeCAD API Constraints

**Active document pattern:** Tools check for active document, clear error if missing
**Object references:** Use explicit naming (`sketch_name` parameter) to avoid collisions

---

**Last Updated:** 2025-11-18
