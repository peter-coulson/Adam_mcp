# Context System

Strategic context and architectural decisions for adam-mcp.

---

## Purpose

Document **WHY** decisions were made, not **WHAT** the code does or **HOW** it works (that's what the code shows).

---

## Structure

```
context/
├── README.md       # This file (governance and entry point)
├── DECISIONS.md    # Core architectural choices
├── OPERATIONS.md   # Operation roadmap and MVP status
├── TOOLS.md        # Tool design patterns (flat tools, MCP integration)
└── WORKFLOW.md     # User experience architecture
```

---

## What Goes Here

### ✅ Document:
- **Architectural decisions** - Why direct FreeCAD imports? Why flat tools?
- **Design rationale** - Why these operations? Why no Python fallback?
- **Technical choices** - Why operation-specific tools vs unified tool?
- **User experience patterns** - Sequential operations, inspection workflows
- **Non-obvious constraints** - FreeCAD API limitations, MCP compatibility
- **MVP status** - What's implemented, what's next

### ❌ Don't Document:
- Parameter lists (see code + MCP schema)
- API reference (see FreeCAD docs)
- Implementation details (code is self-documenting)
- Complete code samples (max 5-10 lines for patterns)
- Rejected alternatives (decision + brief rationale only)

---

## Governance

**Philosophy:** Critical context only. Each file serves one clear purpose.

### Size Limits

| File | Purpose | Target | Hard Limit |
|------|---------|--------|------------|
| README.md | Governance | 60 lines | 100 lines |
| DECISIONS.md | Core architecture | 150 lines | 220 lines |
| OPERATIONS.md | Operation roadmap + MVP status | 120 lines | 180 lines |
| TOOLS.md | Tool design patterns | 100 lines | 150 lines |
| WORKFLOW.md | UX patterns | 150 lines | 200 lines |
| **TOTAL** | | **~580 lines** | **850 lines** |

**Rationale:** Small project, focused scope. Exceeding limits = bloat or content that belongs in code.

### Content Principles

1. **One source of truth** - Each decision documented once
2. **WHY over WHAT** - Explain rationale, not mechanics
3. **Scannable** - Bullet points over prose
4. **Minimal examples** - Max 5-10 lines to show pattern

### Maintenance

**Update when:** Major architectural change, new tool category, MVP milestone
**Don't update for:** Individual tools, parameter tweaks, bug fixes, refactoring

---

## Quick Reference

- **New contributor:** Read all context files (5-7 min)
- **Add operation:** Check OPERATIONS.md patterns (1 min)
- **Architectural change:** Update relevant context file
- **Standard feature:** No context update needed

---

**Last Updated:** 2025-11-18
