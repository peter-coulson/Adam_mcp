# Demo Plan - adam-mcp

Demonstration strategy for adam-mcp MCP server showcasing both **creation from scratch** and **intelligent editing via context discovery**.

---

## Demo Philosophy

This demo showcases **two key value propositions** of the adam-mcp MCP server:

1. **Structured CAD Operations** - Create engineering parts from scratch using validated JSON operations
2. **Intelligent Context Discovery** - Claude inspects existing designs, understands dimensions, and makes smart modifications

**Why this matters:** Most CAD automation is blind execution. adam-mcp enables Claude to **understand what exists** before making changes - like a human engineer would.

---

## Demo Flow (2-3 minutes)

### Part 1: Create M10 Bolt from Scratch (0:00-0:45)
**Shows: Basic operation workflow**

```
User: "Create an M10×40 hex bolt"

Claude executes:
  1. CreateCylinder(name="Shaft", radius=5, height=40)
  2. CreateCylinder(name="Head", radius=8, height=6.5, position=(0,0,40))
  3. CreateFusion(name="BoltBody", base="Shaft", tool="Head")
  4. CreateFillet(name="Bolt", base="BoltBody", edges=[top_edges], radius=0.5)
```

**Result:** Basic bolt shape (shaft + head, rounded edges)
**Operations used:** CreateCylinder, CreateFusion, CreateFillet
**Time:** 30-45 seconds

---

### Part 2: Claude Inspects and Adds Threads (0:45-1:30)
**Shows: Intelligent modification via inspection**

```
User: "Add M10 threads to the shaft"

Claude workflow:
  1. list_objects() → ["Bolt"]
  2. get_object_details(["Bolt"]) → Inspects geometry, identifies shaft

  Claude reasoning:
    "I can see the bolt has a 5mm radius shaft (10mm diameter).
     This is correct for M10 threads (10mm nominal diameter).
     I'll add ISO metric threads to the shaft portion."

  3. CreateThread(
       name="ThreadedBolt",
       base="Bolt",
       face_index=2,
       thread_type="M10",
       length=30
     )
```

**Result:** Professional M10 bolt with ISO-standard threads
**Operations used:** list_objects, get_object_details, CreateThread
**Key insight:** Claude **understood** the existing geometry before modifying
**Time:** 30-45 seconds

---

### Part 3: Create M10 Washer (1:30-2:15)
**Shows: Sketch-based workflow (more complex than primitives)**

```
User: "Create an M10 washer to go with that bolt"

Claude executes:
  1. CreateSketch(name="WasherProfile", plane="XY")
  2. AddSketchCircle(sketch="WasherProfile", center=(0,0), radius=10)
  3. CreatePad(name="WasherBody", sketch="WasherProfile", length=2)
  4. CreateSketch(name="Hole", plane="XY")
  5. AddSketchCircle(sketch="Hole", center=(0,0), radius=5.5)
  6. CreatePocket(name="Washer", sketch="Hole", length=2)
  7. CreateFillet(name="FinishedWasher", base="Washer", edges=[inner, outer], radius=0.3)
```

**Result:** M10 washer (20mm OD, 11mm ID, 2mm thick, rounded edges)
**Operations used:** CreateSketch, AddSketchCircle, CreatePad, CreatePocket, CreateFillet
**Progression:** Shows sketch-based workflow vs primitive-based (bolt)
**Time:** 45 seconds

---

### Part 4: Claude Verifies Compatibility (2:15-2:45)
**Shows: Smart dimensional analysis and verification**

```
User: "Check if the washer fits the bolt"

Claude workflow:
  1. list_objects() → ["ThreadedBolt", "FinishedWasher"]
  2. get_object_details(["ThreadedBolt", "FinishedWasher"])

  Claude analysis:
    "ThreadedBolt shaft diameter: 10mm (M10 standard)
     FinishedWasher inner diameter: 11mm
     Clearance: 1mm

     ✓ Washer fits the bolt with appropriate clearance for M10 hardware.
     ✓ Outer diameter (20mm) provides adequate bearing surface.
     ✓ Standard M10 washer specifications met."

User: "Make it a heavy-duty washer"

Claude workflow:
  1. get_object_details(["FinishedWasher"]) → Sees 2mm thickness

  Claude reasoning:
    "Current washer is 2mm thick (standard).
     Heavy-duty washers are typically 3-4mm.
     I'll increase to 4mm thickness."

  2. ModifyObject(name="FinishedWasher", property="Height", value=4)
     # OR recreate with new dimensions if ModifyObject not available
```

**Result:** Washer modified based on intelligent analysis
**Key insight:** Claude **understands ISO standards** and **applies engineering knowledge**
**Time:** 30 seconds

---

### Part 5: Show in FreeCAD GUI (2:45-3:00)
**Shows: Professional 3D output**

```
Claude executes:
  open_in_freecad_gui()
```

**Viewer shows:**
- Professional 3D models with proper geometry
- Threaded bolt with ISO-standard thread profile
- Washer with rounded edges
- Parts that match real engineering specifications

**Time:** 15 seconds

---

## Required Operations (8 core operations)

**Primitives:**
1. **CreateCylinder** - Create cylindrical shapes (bolt shaft/head)

**Sketches:**
2. **CreateSketch** - Start 2D sketch on plane
3. **AddSketchCircle** - Add circles to sketch (washer profile/hole)

**Features:**
4. **CreatePad** - Extrude sketch to create solid (washer body)
5. **CreatePocket** - Cut into solid using sketch (washer hole)
6. **CreateFillet** - Round edges (bolt head, washer edges)
7. **CreateThread** - Add ISO threads (bolt shaft)

**Booleans:**
8. **CreateFusion** - Union shapes (combine bolt shaft + head)

**Query Tools (already implemented):**
- **list_objects()** - Discover what exists in document
- **get_object_details()** - Inspect geometry and properties

---

## Why These Operations?

**Chosen specifically to demonstrate:**

1. **Two workflows:** Primitive-based (bolt) + Sketch-based (washer)
2. **Additive + Subtractive:** Pad (add material) + Pocket (remove material)
3. **Basic + Advanced:** Simple fusion → Complex threading
4. **Context discovery:** Query tools enable intelligent inspection
5. **Real engineering:** ISO-standard parts (M10 bolt/washer), not abstract shapes

**Design principle:** Minimum operations to tell maximum story

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
✅ **Structured operations provide validation** (type-safe, pre-checked)
✅ **Context discovery enables intelligent editing** (like a human engineer)
✅ **Professional output** (ISO standards, proper geometry)

---

## Script Notes

**Opening (5 seconds):**
"This is adam-mcp - an MCP server that lets Claude design CAD parts in FreeCAD. Watch how Claude creates an M10 bolt and matching washer."

**Part 1 narration (30 seconds):**
"First, Claude creates the bolt from scratch using primitive operations - a shaft cylinder, head cylinder, fuses them together, and rounds the edges."

**Part 2 narration (30 seconds):**
"Now here's the interesting part - Claude inspects the bolt it just created, understands it's a 10mm diameter shaft, and adds proper ISO M10 threads. This isn't blind execution - Claude understands what it's modifying."

**Part 3 narration (45 seconds):**
"Next, Claude creates a matching washer using sketch-based operations - more complex than primitives. It sketches circles, extrudes the body, cuts the center hole, and rounds the edges."

**Part 4 narration (30 seconds):**
"Finally, Claude verifies the parts are compatible - it inspects both, confirms the 11mm washer hole fits the 10mm bolt with appropriate clearance, and validates against ISO M10 standards."

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
