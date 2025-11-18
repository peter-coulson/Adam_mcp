# adam-mcp

**MCP server for creating and editing industrial CAD parts in FreeCAD.**

Use tool discovery to understand available operations. Focus on structured workflows.

---

## Workflow

### For CAD Operations (Creating/Modifying Parts)

1. **Tool Discovery** - Use MCP tool list to understand available operations
2. **Execute Operations** - Use discovered tools to perform CAD operations
3. **Verify** - Use `open_in_freecad_gui()` to verify results visually

**Tools are self-documenting** - Read tool descriptions and parameters to understand capabilities.

---

## Demo

See `PROMPTS.md` for exact demo prompts:
- Part 1: Create 4-inch Class 150 pipe flange from scratch
- Part 2: Modify pre-existing M3 nyloc nut for M6 size

See `context/DEMO.md` for strategy and rationale

---

**Last Updated:** 2025-11-18
