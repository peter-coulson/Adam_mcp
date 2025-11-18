# Demo Plan - adam-mcp

Demonstration strategy for adam-mcp MCP server showcasing **creation from scratch**, **intelligent editing via context discovery**, and **property modification**.

---

## Demo Philosophy

This demo showcases **three key value propositions** of the adam-mcp MCP server:

1. **Structured CAD Operations** - Create engineering parts from scratch using validated operations
2. **Intelligent Context Discovery** - Claude inspects existing designs, understands dimensions
3. **Property Modification** - Claude edits object properties based on inspection and requirements ⭐ NEW

**Why this matters:** Most CAD automation is blind execution. adam-mcp enables Claude to **understand what exists**, **inspect properties**, and **modify them intelligently** - like a human engineer would.

---

## Demo Flow (2-3 minutes)

### Part 1: Create M10 Bolt from Scratch (0:00-0:30)
**Shows: Basic primitive operation**

```
User: "Create an M10×40 bolt"

Claude executes:
  1. create_cylinder(name="Bolt", radius=5, height=40, description="M10 bolt body")
```

**Result:** Basic cylindrical bolt body (10mm diameter, 40mm length)
**Operations used:** create_cylinder
**Time:** 15-30 seconds

---

### Part 2: Claude Inspects and Adds Threads (0:30-1:00)
**Shows: Intelligent modification via inspection**

```
User: "Add M10 threads to the bolt"

Claude workflow:
  1. list_objects() → ["Bolt"]
  2. get_object_details(["Bolt"]) → Inspects geometry

  Claude reasoning:
    "The bolt has a 5mm radius (10mm diameter).
     This matches M10 threads (10mm nominal diameter).
     I'll add ISO metric threads to the cylindrical surface."

  3. create_thread(
       name="ThreadedBolt",
       base="Bolt",
       face_index=2,
       thread_type="M10",
       length=35,
       description="Add M10 threads to bolt shaft"
     )
```

**Result:** Professional M10 bolt with ISO-standard threads
**Operations used:** list_objects, get_object_details, create_thread
**Key insight:** Claude **understood** the existing geometry before modifying
**Time:** 30 seconds

---

### Part 3: Create M10 Washer (1:00-1:45)
**Shows: Sketch-based workflow (more complex than primitives)**

```
User: "Create an M10 washer to go with that bolt"

Claude executes:
  1. create_sketch(name="WasherProfile", plane="XY", description="Washer outer profile")
  2. add_sketch_circle(sketch="WasherProfile", center=(0,0), radius=10, description="20mm OD")
  3. create_pad(name="WasherBody", sketch="WasherProfile", length=2, description="Extrude 2mm")
  4. create_sketch(name="Hole", plane="XY", description="Center hole")
  5. add_sketch_circle(sketch="Hole", center=(0,0), radius=5.5, description="11mm ID for M10")
  6. create_pocket(name="Washer", sketch="Hole", length=2, description="Cut center hole")
```

**Result:** M10 washer (20mm OD, 11mm ID, 2mm thick)
**Operations used:** create_sketch, add_sketch_circle, create_pad, create_pocket
**Progression:** Shows sketch-based workflow vs primitive-based (bolt)
**Time:** 45 seconds

---

### Part 4: Claude Verifies and Modifies (1:45-2:30)
**Shows: Inspection, analysis, and property modification** ⭐ KEY DEMO

```
User: "Check if the washer fits the bolt, and make it heavy-duty"

Claude workflow:
  1. list_objects() → ["ThreadedBolt", "Washer"]
  2. get_object_details(["ThreadedBolt", "Washer"])

  Claude analysis:
    "ThreadedBolt diameter: 10mm (M10 standard)
     Washer inner diameter: 11mm → Clearance: 1mm ✓
     Washer outer diameter: 20mm → Good bearing surface ✓
     Washer thickness (Length): 2mm → Standard thickness

     For heavy-duty use, increase thickness to 4mm."

  3. modify_object(
       name="Washer",
       property="Length",
       value=4.0,
       description="Increase thickness for heavy-duty use"
     )

  4. get_object_details(["Washer"]) → Verify Length now shows 4mm
```

**Result:** Washer thickness increased from 2mm to 4mm based on requirements
**Operations used:** list_objects, get_object_details, modify_object
**Key insight:** Claude **inspects**, **analyzes**, and **modifies** properties intelligently
**Time:** 45 seconds

---

### Part 5: Show in FreeCAD GUI (2:30-2:45)
**Shows: Professional 3D output**

```
Claude executes:
  open_in_freecad_gui()
```

**Viewer shows:**
- Professional 3D models with proper geometry
- Threaded bolt with ISO-standard thread profile
- Heavy-duty washer (4mm thick, modified from original 2mm)
- Parts that match real engineering specifications

**Time:** 15 seconds

---

## Required Operations (7 core operations)

**Primitives:**
1. **create_cylinder** - Create cylindrical shapes (bolt body)

**Sketches:**
2. **create_sketch** - Start 2D sketch on plane
3. **add_sketch_circle** - Add circles to sketch (washer profile/hole)

**Features:**
4. **create_pad** - Extrude sketch to create solid (washer body)
5. **create_pocket** - Cut into solid using sketch (washer hole)
6. **create_thread** - Add ISO threads (bolt shaft)

**Modifications:** ⭐ NEW
7. **modify_object** - Change object properties (washer thickness, cylinder radius, etc.)

**Query Tools (already implemented):**
- **list_objects()** - Discover what exists in document
- **get_object_details()** - Inspect geometry and properties

**Removed from original plan:**
- ~~CreateFillet~~ - Polish feature (post-MVP)
- ~~CreateFusion~~ - Not needed (single cylinder bolt simpler than shaft+head fusion)

---

## Why These Operations?

**Chosen specifically to demonstrate:**

1. **Two workflows:** Primitive-based (bolt) + Sketch-based (washer)
2. **Additive + Subtractive:** Pad (add material) + Pocket (remove material)
3. **Creation + Editing:** Create operations + ModifyObject for property changes ⭐
4. **Context discovery:** Query tools enable intelligent inspection
5. **Real engineering:** ISO-standard parts (M10 bolt/washer), not abstract shapes
6. **Intelligent modification:** Inspect → Analyze → Edit workflow (like human engineer)

**Design principle:** Core workflows (create + edit) over polish features (fillet, fusion)

---

## Demo Variants

### Variant A: Simple (90 seconds)
- Create bolt (primitives)
- Inspect and add threads
- Show in GUI

### Variant B: Full (3 minutes)
- Create bolt
- Inspect and add threads
- Create washer (sketches)
- Verify compatibility
- Show in GUI

### Variant C: Engineering Focus (2 minutes)
- Create bolt
- Create washer
- Claude verifies ISO standards compliance
- Demonstrates engineering knowledge

---

## Success Criteria

After watching the demo, viewers should understand:

✅ **adam-mcp creates real engineering parts** (not toy examples)
✅ **Claude can inspect and understand** existing CAD geometry
✅ **Claude can modify properties** based on inspection and requirements ⭐ NEW
✅ **Structured operations provide validation** (type-safe, pre-checked)
✅ **Context discovery enables intelligent workflows** (inspect → analyze → edit)
✅ **Professional output** (ISO standards, proper geometry)

---

## Script Notes

**Opening (5 seconds):**
"This is adam-mcp - an MCP server that lets Claude create, inspect, and edit CAD parts in FreeCAD. Watch how Claude creates an M10 bolt and washer, then modifies them based on requirements."

**Part 1 narration (20 seconds):**
"First, Claude creates a simple M10 bolt from a cylinder primitive - 10mm diameter, 40mm long."

**Part 2 narration (20 seconds):**
"Now Claude inspects the bolt it just created, understands it's the right diameter for M10 threads, and adds proper ISO metric threading. This isn't blind execution - Claude understands what it's modifying."

**Part 3 narration (30 seconds):**
"Next, Claude creates a matching washer using sketch-based operations - more complex than primitives. It sketches circles for the outer profile and center hole, extrudes the body, then cuts the hole."

**Part 4 narration (30 seconds):**
"Here's the key feature - Claude inspects both parts, verifies the washer fits the bolt, then modifies the washer thickness from 2mm to 4mm for heavy-duty use. This demonstrates true property editing, not just creation."

**Closing (10 seconds):**
"The result: professional engineering parts that meet ISO specifications, created through a conversation with Claude."

---

## Technical Notes

**File structure:**
- Demo uses two documents: `bolt.FCStd` and `washer.FCStd`
- Working file system preserves state between operations
- All operations validated before execution (Pydantic)

**Geometry validation:**
- Post-execution validation ensures valid shapes
- Thread operations check cylindrical surfaces
- Pocket operations verify sketch closure

**Error handling:**
- Clear messages: "Radius 15mm exceeds edge length 10mm. Maximum: 5mm"
- Pre-execution validation catches errors before FreeCAD execution
- Graceful failures with recovery guidance

---

**Last Updated:** 2025-11-18
