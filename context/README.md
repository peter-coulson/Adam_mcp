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
3. **Pointer over duplication** - Link to code, don't reproduce (max 5-10 line examples)
4. **Scannable** - Bullet points and short sections over prose

### Maintenance

**Update when:** Major architectural change, new tool category, design constraints discovered
**Don't update for:** Individual tools, parameter tweaks, bug fixes, internal refactoring
**Health check:** Run `/context-check` to validate references, size limits, duplication, secrets

---

## Quick Reference

- **New work:** Read `DECISIONS.md` (2 min)
- **Architectural change:** Update `DECISIONS.md`
- **Standard tool:** No update needed
- **Onboarding:** `CLAUDE.md` → `context/` (5 min total)

---

**Last Updated:** 2025-11-18
