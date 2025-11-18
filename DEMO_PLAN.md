# Demo Plan - adam-mcp

Demonstration strategy for adam-mcp MCP server showcasing **complete-looking industrial parts** through **creation from scratch** and **modification of complex existing parts**.

---

## Demo Philosophy

This demo showcases **two key value propositions** of the adam-mcp MCP server:

1. **Full Creation Workflow** - Create complex industrial parts from scratch that look 100% complete (no missing visual features)
2. **Modification Beyond Current Capabilities** - Edit pre-existing complex parts that use operations we can't create yet (Revolution, Chamfer, Fusion)

**Why this matters:** Shows both what the system can create NOW (pipe flange) and its extensibility via modification (nyloc nut with advanced features). Both parts look professionally complete - no "half-finished" appearance like threaded parts without visible threads.

---

## Demo Flow (2-3 minutes)

### Part 1: Create 4-inch Class 150 Pipe Flange from Scratch (0:00-2:00)
**Shows: Complete multi-feature industrial part creation**

```
User: "Create a 4-inch Class 150 raised face weld neck pipe flange"

Claude executes:
  1. create_sketch(
       name="FlangeProfile",
       plane="XY",
       description="Flange body profile with concentric circles"
     )

  2. add_sketch_circle(
       sketch_name="FlangeProfile",
       center=(0, 0),
       radius=82.5,
       description="Outer diameter 165mm (6.5 inches)"
     )

  3. add_sketch_circle(
       sketch_name="FlangeProfile",
       center=(0, 0),
       radius=57,
       description="Bolt circle diameter 114mm (4.5 inches)"
     )

  4. add_sketch_circle(
       sketch_name="FlangeProfile",
       center=(0, 0),
       radius=51,
       description="Bore diameter 102mm (4 inches)"
     )

  5. create_pad(
       name="FlangeBody",
       sketch="FlangeProfile",
       length=16,
       description="Extrude flange body 16mm thick"
     )

  6. create_sketch(
       name="BoltHole1",
       plane="XY",
       description="First bolt hole on bolt circle"
     )

  7. add_sketch_circle(
       sketch_name="BoltHole1",
       center=(57, 0),
       radius=6.5,
       description="M12 bolt hole (13mm diameter)"
     )

  8. create_pocket(
       name="Hole1",
       sketch="BoltHole1",
       length=16,
       description="Cut first bolt hole through flange"
     )

  [Repeat steps 6-8 for remaining 7 bolt holes at 45° intervals]

  9. create_sketch(
       name="RaisedFace",
       plane="XY",
       description="Raised face sealing surface"
     )

  10. add_sketch_circle(
        sketch_name="RaisedFace",
        center=(0, 0),
        radius=58.5,
        description="Raised face diameter 117mm"
      )

  11. create_pad(
        name="FlangeFinal",
        sketch="RaisedFace",
        length=2,
        description="Add 2mm raised face for gasket seal"
      )
```

**Result:** Professional ISO 7005 pipe flange with:
- 165mm outer diameter
- 8 bolt holes on 114mm bolt circle
- 102mm bore for pipe welding
- 2mm raised face for gasket sealing
- Looks 100% complete (flanges don't need threads!)

**Operations used:** create_sketch, add_sketch_circle, create_pad, create_pocket
**Key insight:** Multi-feature industrial component, visually complete, real-world ISO standard
**Time:** ~2 minutes

---

### Part 2: Modify Pre-Existing Nyloc Nut (2:00-3:00)
**Shows: Editing complex parts beyond current creation capabilities** ⭐ KEY DEMO

```
User: "Open the M3 nyloc nut and inspect it, then modify it for M6 size"

Claude workflow:
  1. open_document(path="test_samples/nyloc_nut_m3.FCStd")

  2. list_objects()
     → Returns: Revolution, Pocket, Chamfer, Cut, Fusion, Compound

  3. get_object_details(["Revolution", "Pocket", "Chamfer", "Cut"])

  Claude analysis:
    "This nyloc nut was created with advanced operations:
     - Revolution (360° revolve) - we don't have this yet
     - Chamfer (edge beveling) - we don't have this yet
     - Fusion (boolean union) - we don't have this yet
     - Cut (nylon ring) with specific placement

     Current pocket depth: 5mm (for M3 threads)
     Chamfer size: 0.2mm
     Nylon ring position: Z=2.6mm

     To adapt for M6 (larger), I need to:
     - Increase pocket depth for deeper threads
     - Adjust nylon ring height
     - Scale chamfer appropriately"

  4. modify_object(
       name="Pocket",
       property="Length",
       value=8.0,
       description="Increase pocket depth from 5mm to 8mm for M6 threads"
     )

  5. modify_object(
       name="Cut",
       property="Placement",
       value=(0, 0, 4.2),
       description="Reposition nylon ring higher for M6 nut geometry"
     )

  6. get_object_details(["Pocket", "Cut"])
     → Verify changes applied correctly

  7. open_in_freecad_gui()
```

**Result:** Modified nyloc nut adapted for different size
**Operations used:** list_objects, get_object_details, modify_object, open_in_freecad_gui
**Key insight:** Can edit complex parts using operations we can't create yet (Revolution, Chamfer, Fusion)
**Demonstrates:** Modification workflow works on pre-existing CAD files
**Time:** ~1 minute

---

## Required Operations (7 core operations)

**Primitives:**
1. **create_cylinder** - Create cylindrical shapes

**Sketches:**
2. **create_sketch** - Start 2D sketch on plane
3. **add_sketch_circle** - Add circles to sketch

**Features:**
4. **create_pad** - Extrude sketch to create solid
5. **create_pocket** - Cut into solid using sketch
6. **create_thread** - Add ISO thread metadata (cosmetic)

**Modifications:**
7. **modify_object** - Change object properties (dimensions, placement, etc.)

**Query Tools (already implemented):**
- **list_objects()** - Discover what exists in document
- **get_object_details()** - Inspect geometry and properties

**Operations Demonstrated via Modification (not implemented yet):**
- Revolution (360° revolve) - seen in nyloc nut
- Chamfer (edge beveling) - seen in nyloc nut
- Fusion (boolean union) - seen in nyloc nut
- Boolean Cut - seen in nyloc nut

---

## Why These Demo Parts?

**Pipe Flange:**
✅ Looks 100% complete (no threads needed - flanges use bolts to connect)
✅ Multi-feature complexity (concentric circles, bolt hole pattern, raised face)
✅ Real ISO 7005 industrial standard ($50-500 depending on size/material)
✅ Demonstrates full creation workflow from scratch
✅ Shows pattern creation (8 bolt holes)
✅ Professional appearance

**Nyloc Nut:**
✅ Demonstrates modification of complex pre-existing parts
✅ Shows we can work with operations beyond current creation capabilities
✅ Real-world use case (editing existing CAD library parts)
✅ Proves extensibility of the system
✅ Looks complete (no visual incompleteness)

**Combined Demo Value:**
✅ Shows both creation AND modification workflows
✅ Both parts look professionally complete
✅ No "half-finished" appearance (unlike bolt without visible threads)
✅ Real industrial components with engineering value
✅ Demonstrates system can grow beyond current operation set

---

## Success Criteria

After watching the demo, viewers should understand:

✅ **adam-mcp creates complete industrial parts** (pipe flange - no missing features)
✅ **System works with complex pre-existing parts** (nyloc nut with advanced operations)
✅ **Modification workflow extends beyond creation capabilities** (edit what we can't create yet)
✅ **Professional output** (ISO standards, proper geometry, no visual incompleteness)
✅ **Structured operations provide validation** (type-safe, pre-checked)
✅ **Extensible architecture** (can edit advanced features before implementing creation tools)

---

## Script Notes

**Opening (5 seconds):**
"This is adam-mcp - an MCP server that lets Claude create and edit industrial CAD parts in FreeCAD. Watch how Claude creates a pipe flange from scratch and modifies a complex nyloc nut."

**Part 1 narration (90 seconds):**
"First, Claude creates a 4-inch Class 150 pipe flange - a real industrial component used in piping systems. It builds up the geometry step by step: outer flange body with concentric circles, then cuts 8 bolt holes in a circular pattern, and adds a raised face for gasket sealing. This is a complete ISO 7005 standard part - no missing visual features."

**Part 2 narration (60 seconds):**
"Now Claude opens a pre-existing nyloc nut that was created with advanced operations - Revolution, Chamfer, and Fusion - operations we don't have creation tools for yet. Claude inspects the part, understands its structure, then modifies properties like pocket depth and nylon ring position. This proves the system can work with complex parts beyond its current creation capabilities."

**Closing (10 seconds):**
"The result: professional industrial parts that are visually complete and meet real engineering standards. Creation and modification workflows working together."

---

## Technical Notes

**File structure:**
- Pipe flange: Created from scratch in `pipe_flange_4in_class150.FCStd`
- Nyloc nut: Pre-existing `dev_projects/test_samples/nyloc_nut_m3.FCStd`
- Working file system preserves state between operations
- All operations validated before execution (Pydantic)

**Geometry validation:**
- Post-execution validation ensures valid shapes
- Sketch operations check plane validity
- Pocket operations verify through-all or specific depth
- Modification operations validate property existence and type

**Error handling:**
- Clear messages: "Property 'InvalidProp' not found on object 'Pocket'. Available properties: Length, Reversed, ..."
- Pre-execution validation catches errors before FreeCAD execution
- Graceful failures with recovery guidance

**Why No Threads in Demo:**
- Current thread tool only adds metadata (cosmetic)
- Actual helical thread geometry requires Revolution + Sweep operations
- Rather than show incomplete-looking parts, we chose parts that look 100% complete
- Flanges naturally don't have threads (they use bolts)
- Nyloc nut thread is internal and not primary visual feature

---

**Last Updated:** 2025-11-18
