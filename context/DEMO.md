# Demo Strategy

Critical decisions for adam-mcp demonstration.

---

## Demo Philosophy

Two separate chat sessions showcasing different capabilities:

**Chat 1 - Creation + Iteration:**
1. **Full Creation Workflow** - Create complex multi-feature part from scratch
2. **Iterative Modification** - Modify and extend the part in the same session
3. **Commit Workflow** - Save changes to main file

**Chat 2 - Discovery + Modification:**
1. **Project Management** - List and discover existing projects
2. **File Inspection** - Open and understand existing geometry
3. **Targeted Modification** - Make specific changes to existing parts
4. **Commit Workflow** - Validate and save changes

**Why:** Demonstrates full project lifecycle - creation, inspection, modification, persistence

---

## Known Limitations for Demo

**GUI Management:**
- ✅ Call `open_in_freecad_gui()` at START of operations (before making changes)
- ⚠️ User must manually close GUI between operations (FreeCAD limitation)
- ✅ Call `open_in_freecad_gui()` at END of operations (verify final result)
- **Why:** FreeCAD GUI requires manual close between operations for file reload

**Demo Flow:**
1. Claude calls `open_in_freecad_gui()` → User sees initial state
2. User manually closes GUI window
3. Claude performs operations (create/modify)
4. Claude calls `open_in_freecad_gui()` → User sees final result
5. Repeat for next operation

---

## Part Selection Rationale

### Chat 1: Spindle Shaft Creation + Iteration

**Part 1 - Elongated Spindle Shaft:**
- ✅ Multi-feature complexity (5 cylindrical sections with varying dimensions)
- ✅ Demonstrates sequential stacking and positioning
- ✅ Realistic mechanical component (machine spindle)
- ✅ Clear visual result (stepped diameter profile)
- ✅ Natural setup for Part 2 mirroring operation

**Demonstrates:**
- Sequential primitive creation (5 cylinders)
- Vertical stacking and positioning (cumulative height tracking)
- Dimensional variation (80mm → 65mm → 50mm → 35mm → 20mm diameters)
- Complex geometry from simple operations

**Part 2 - Mirror the Spindle:**
- ✅ Demonstrates iterative modification in same conversation
- ✅ Shows Claude can analyze existing structure
- ✅ Creates symmetrical geometry (common industrial requirement)
- ✅ Builds on Part 1 (conversational workflow)
- ✅ Results in complete double-sided spindle

**Demonstrates:**
- Analysis of existing geometry (identify dimensions, positions)
- Inverted sequence creation (70mm tip → 90mm → 100mm → 80mm → 40mm base)
- Conversational iteration (create → inspect → extend)
- Cumulative positioning (continuing from existing shaft end)
- **Commit workflow** (save changes to main file)

---

### Chat 2: Bolt Head Discovery + Modification

**Part 1 - Discover and Inspect:**
- ✅ Demonstrates project discovery (`list_projects_tool`)
- ✅ Shows file metadata (size, modified time, working file status)
- ✅ Opens existing project (resume workflow)
- ✅ Systematic inspection (`list_objects` → `get_object_details`)
- ✅ Claude explains structure to user

**Demonstrates:**
- Project management workflow
- File discovery and selection
- Object tree navigation
- Property inspection and analysis
- Understanding existing geometry without modification

**Part 2 - Modify Bolt Head:**
- ✅ Single focused modification (make bolt head larger)
- ✅ Demonstrates targeted property changes
- ✅ Simple operation on pre-existing complex part
- ✅ Shows modification workflow distinct from creation

**Demonstrates:**
- Identifying correct object to modify
- Property-based modification (`modify_object_tool`)
- Visual verification of changes
- **Commit workflow** (validate and save changes)

---

## Success Criteria

After watching both demo chats, viewers understand:

**Core Capabilities:**
✅ adam-mcp creates complex multi-feature parts from primitives
✅ Sequential operations build up geometry step-by-step
✅ Conversational workflow enables iterative design
✅ Claude can analyze and extend existing geometry
✅ Structured operations provide clear, predictable results
✅ System handles realistic mechanical components

**Project Management:**
✅ Project discovery and listing (`list_projects_tool`)
✅ File inspection and understanding (`list_objects`, `get_object_details`)
✅ Resume workflow (working files preserved across sessions)
✅ Commit workflow (validate and save changes to main file)

**Two-Chat Structure:**
✅ Chat 1 shows creation + iteration workflow
✅ Chat 2 shows discovery + modification workflow
✅ Both demonstrate mandatory commit workflow
✅ Clear separation of concerns (create vs inspect vs modify)

---

## Why NOT Other Parts

**Pipe flanges (previous demo):**
- ❌ Requires sketch operations (circles, patterns) - more complex
- ❌ Engineering standards add cognitive overhead
- ❌ Less clear visual progression

**Threaded bolts:**
- ❌ Current thread tool only adds metadata (cosmetic)
- ❌ Helical thread geometry requires Revolution + Sweep (not implemented)
- ❌ Would look incomplete without visible threads

**Nyloc nuts (previous demo):**
- ❌ Requires pre-existing file (not pure creation)
- ❌ Doesn't demonstrate conversational iteration in same session

**Gears:**
- ❌ Requires parametric tooth profiles (complex sketch operations not implemented)

---

**Last Updated:** 2025-11-18
