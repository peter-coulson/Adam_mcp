# adam-mcp

**MCP server for creating and editing industrial CAD parts in FreeCAD.**

Use tool discovery to understand available operations. Focus on structured workflows.

---

## Workflow

### For CAD Operations (Creating/Modifying Parts)

**CRITICAL:** Always follow this workflow for CAD operations:

1. **Open GUI at start** - Call `open_in_freecad_gui()` BEFORE making any changes
   - User will manually close GUI between operations (known limitation)
   - This provides live preview as you work

2. **Tool Discovery** - Use MCP tool list to understand available operations

3. **Execute Operations** - Use discovered tools to perform CAD operations

4. **Verify at end** - Call `open_in_freecad_gui()` AFTER completing changes
   - Shows final result for verification

5. **Commit changes** - **MANDATORY:** After completing operations, ALWAYS prompt user to commit
   - Tell user: "Your changes are ready. Please commit them by calling `commit_changes()`"
   - User will then run the commit command
   - DO NOT proceed until user commits

**Tools are self-documenting** - Read tool descriptions and parameters to understand capabilities.

---

## Commit Policy

**MANDATORY COMMIT WORKFLOW:**

After ANY set of CAD operations (create, modify, etc.), you MUST:
1. Inform user that changes are complete and ready to commit
2. Explicitly tell user to run: `commit_changes()`
3. Wait for user to execute the commit
4. Only after commit, consider the task complete

**Why commits are mandatory:**
- All edits happen on working file (.work extension)
- Main file only updates when user commits
- Uncommitted changes are preserved across sessions
- Commits validate geometry before saving

---

## Demo

See `PROMPTS.md` for exact demo prompts:

**Chat 1 - Creation + Iteration:**
- Part 1: Create elongated spindle shaft (5 stepped cylinders)
- Part 2: Mirror the spindle for symmetrical double-sided shaft
- Demonstrates: Sequential creation, iterative modification, commit workflow

**Chat 2 - Discovery + Modification:**
- Part 1: List projects, open bolt head, inspect structure
- Part 2: Modify bolt head to be much larger
- Demonstrates: Project discovery, file inspection, targeted modification, commit workflow

See `context/DEMO.md` for strategy and rationale

---

**Last Updated:** 2025-11-18
