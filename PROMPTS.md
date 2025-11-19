# Demo Prompts

Two separate chat sessions demonstrating different adam-mcp capabilities.

---

## Important: GUI Management

**Between each prompt below:**
1. Claude calls `open_in_freecad_gui()` at end
2. **User manually closes GUI window** (known limitation)
3. Proceed to next prompt

---

# CHAT 1: Creation + Iteration Workflow

## Part 1: Create Spindle Shaft

```
Create an elongated spindle shaft - starting at 80mm diameter × 40mm base, stepping down to 65mm × 80mm, then 50mm × 100mm, then 35mm × 90mm, then tapering to 20mm × 70mm tip
```

**Expected workflow:**
- Claude calls `open_in_freecad_gui()` at START (shows empty document)
- User closes GUI
- Claude creates spindle (multiple cylinders stacked vertically)
- Claude calls `open_in_freecad_gui()` at END
- User sees complete stepped spindle shaft

---

## Part 2: Mirror the Spindle

```
Mirror this spindle so that it is the same size on the other side
```

**Expected workflow:**
- Claude analyzes existing structure
- Claude creates mirrored geometry (inverted step sequence)
- Claude calls `open_in_freecad_gui()` at END
- User sees symmetrical double-sided spindle
- **Claude MUST prompt user to commit changes**
- User runs: `commit_changes()`

---

# CHAT 2: Project Discovery + Modification Workflow

**New chat session starts here** - Demonstrates project management and file inspection

## Part 1: Discover and Inspect

```
List the available projects
```

**Expected workflow:**
- Claude calls `list_projects_tool()`
- Shows available projects with metadata

**Then:**
```
Open the bolt head project and understand its structure
```

**Expected workflow:**
- Claude calls `open_document_tool()` with bolt head path
- Claude calls `open_in_freecad_gui()` to show current state
- User closes GUI
- Claude calls `list_objects_tool()` to see object tree
- Claude calls `get_object_details_tool()` to understand geometry
- Claude explains structure to user

---

## Part 2: Modify Bolt Head

```
Show me in the GUI
```

**Expected workflow:**
- Claude calls `open_in_freecad_gui()` to display current model
- User sees bolt head structure visually

**Then:**
```
Make the shaft twice as long
```

**Expected workflow:**
- Claude identifies shaft geometry (cylinder or pad)
- Claude modifies shaft length/height property to double the current value
- Claude calls `open_in_freecad_gui()` at END
- User sees doubled-length shaft
- **Claude MUST prompt user to commit changes**

**Then:**
```
Commit the changes
```

**Expected workflow:**
- User runs: `commit_changes()`
- Changes validated and saved to main file

**Then (optional exploration):**
```
What could you do without failing the first time as an edit to this image?
Could you extend the length of the cylinder? What is best
```

**Expected workflow:**
- Claude analyzes modifiable properties
- Claude recommends cylinder Height modification as most reliable
- Demonstrates understanding of what operations are safe vs. risky

---

**See context/DEMO.md for strategy and rationale**
