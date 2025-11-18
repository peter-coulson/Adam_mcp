# CAD Operations

Operation types, MVP status, and expansion strategy for adam-mcp.

---

## MVP Operations (v0.1) - ✅ COMPLETE

**Goal:** Demonstrate three core workflows through M10 bolt + washer creation

**The 7 operations:**
1. ✅ **create_cylinder** - Cylindrical primitives (bolt shaft)
2. ✅ **create_sketch** - 2D sketches on XY/XZ/YZ planes
3. ✅ **add_sketch_circle** - Circles in sketches (washer profile/hole)
4. ✅ **create_pad** - Extrude sketch into solid (washer body)
5. ✅ **create_pocket** - Cut from solid using sketch (washer hole)
6. ✅ **create_thread** - Add ISO metric threads (bolt threads)
7. ✅ **modify_object** - Edit object properties (change dimensions post-creation)

**Coverage:** Complete CAD workflows
- Primitive-based creation (cylinder → thread)
- Sketch-based creation (sketch → circles → pad → pocket)
- Property modification (inspect → modify)

**Implementation:** ~2,520 LOC across 24 files, average ~105 LOC/file

---

## Success Criteria - ✅ READY FOR TESTING

- ✅ Create M10×40 bolt from scratch (primitive workflow)
- ✅ Add M10 threads to bolt (intelligent context)
- ✅ Create M10 washer via sketches (sketch workflow)
- ✅ Modify washer thickness (editing workflow)
- ✅ Verify washer fits bolt (dimensional inspection)
- ✅ 3-layer validation (Pydantic → Semantic → Geometry)
- ✅ Clear error messages with recovery guidance

See **DEMO_PLAN.md** for test scenarios.

---

## Post-MVP Expansion

Add operations incrementally as real needs arise. Each operation: ~75 LOC.

### Priority Additions (Next 5 operations)
- **create_box** - Box primitives (testing, bases)
- **create_fillet** - Round edges (polish feature)
- **create_fusion** - Boolean union (combine parts)
- **add_sketch_line** - Line segments (general profiles)
- **create_chamfer** - Bevel edges (nut chamfers)

### Future Expansion Categories
- **Additional primitives** (Sphere, Cone, Torus) - 3 ops
- **Additional sketch geometry** (Arc, Rectangle, Constraints) - 3 ops
- **Additional features** (Revolution, Hole, Loft) - 3 ops
- **Pattern operations** (Linear, Polar, Mirror) - 3 ops
- **Boolean operations** (Cut, Common/Intersection) - 2 ops

**Total future scope:** ~25-30 operations for comprehensive coverage

---

## Operation Boundary

**One operation = Create or modify ONE FreeCAD object**

**Allowed:**
- ✓ Create one object with all its properties
- ✓ Modify multiple properties of one object
- ✓ Create one sketch with multiple geometry elements
- ✓ Create one boolean (references others, creates one result)

**NOT allowed (split into multiple operations):**
- ✗ Create multiple independent objects
- ✗ Create AND modify in one operation
- ✗ Modify multiple independent objects

**Rationale:** Clear error attribution, tractable validation, natural debugging.

---

## Validation Strategy

**3-layer validation for ALL operations:**

1. **Pre-execution (Pydantic)** - Types, ranges, required fields
2. **Semantic (Custom)** - Object existence, geometric constraints, dependencies
3. **Post-execution (FreeCAD)** - Document recomputes, shapes valid, no corruption

**Catches:** Syntax errors → Invalid references → Corrupted geometry

---

## Adding New Operations

Pattern (see existing operations for examples):

1. Define Pydantic model in `models/operations/{category}.py`
2. Add to Operation union in `operations/dispatcher.py`
3. Implement handler in `operations/handlers/{category}.py`
4. Add execution function in `tools/execution.py`
5. Register MCP tool in `core/server.py`
6. Add to OPERATION_HANDLERS map in dispatcher

**Implementation checklist:**
- [ ] Pydantic model with validation
- [ ] Handler with semantic checks
- [ ] Execution function with flat params
- [ ] MCP tool registration
- [ ] Add to dispatcher
- [ ] Test with real example

---

**Last Updated:** 2025-11-18
