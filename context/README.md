# Context System

Strategic context and architectural decisions for adam-mcp.

---

## Purpose

Document **WHY** decisions were made and **WHERE** to find implementations, not **WHAT** the code does or **HOW** it works (that's what the code itself shows).

---

## Structure

```
context/
├── README.md       # This file (entry point + governance)
└── DECISIONS.md    # Key architectural and technical choices
```

---

## What Goes Here

### ✅ Document:
- **Architectural decisions** - Why single-file server? Why FastMCP over mcp-python?
- **Design rationale** - Why direct FreeCAD imports vs socket layer?
- **Technical choices** - Why specific units (mm vs cm)? Why these specific tools?
- **Non-obvious constraints** - FreeCAD API limitations, MCP protocol considerations
- **Extension patterns** - How to add new tools without violating principles

### ❌ Don't Document:
- Tool parameter lists (see code + MCP schema)
- FreeCAD API reference (see official docs)
- Step-by-step tutorials (code is self-documenting)
- Complete function implementations (show pattern only, max 10 lines)
- Alternative approaches tried and rejected (keep only final decision + rationale)

---

## Governance (Lightweight)

**Scope:** Small project with focused scope (3-5 CAD tools)

### Size Limits

| File | Target | Hard Limit |
|------|--------|------------|
| README.md | 50 lines | 100 lines |
| DECISIONS.md | 80-120 lines | 150 lines |
| **TOTAL** | **~150 lines** | **250 lines** |

**Rationale:** Context should be scannable in <2 minutes. At 8-hour project scale, more documentation than this indicates over-documentation or content that belongs in code.

### Content Principles

1. **One source of truth** - Each decision documented once
2. **WHY over WHAT** - Explain rationale, not mechanics
3. **Pointer over duplication** - Link to code examples, don't reproduce them
4. **Scannable** - Bullet points and short sections over prose

### Code Examples

**Maximum:** 5-10 lines per example
**Purpose:** Illustrate pattern only
**Always include:** Pointer to actual file for full implementation

**Good example:**
```python
# Pattern: Units in parameter names
def create_box(width_mm: float, height_mm: float) -> str:
    """..."""

# Full implementation: src/adam_mcp/server.py:45
```

**Bad example:** 50-line complete function definition

### Maintenance

**When to update:**
- Major architectural change (e.g., splitting single-file into modules)
- New tool category added (different from sketch/extrude/fillet pattern)
- Design constraint discovered (FreeCAD API limitation)

**When NOT to update:**
- Adding individual tools following existing pattern
- Parameter tweaks
- Bug fixes
- Refactoring that doesn't change architecture

**Health check:** Run `/context-check` to validate:
- File references are valid
- Size limits respected
- No duplication across files
- No secrets in docs

---

## Usage

**Starting new work?**
Read `DECISIONS.md` (2 min read) to understand rationale.

**Making architectural change?**
Update `DECISIONS.md` with new decision + rationale.

**Adding standard tool?**
No context update needed - follow existing patterns in code.

**Onboarding collaborator?**
Point them to `CLAUDE.md` → `context/README.md` → `context/DECISIONS.md` (5 min total).

---

**Last Updated:** 2025-11-18
**Total Context Lines:** ~50 (README) + ~80 (DECISIONS) = ~130 lines
**Status:** ✅ Under target (150 lines)
