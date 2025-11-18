# CAD Operations Roadmap

Operation types and expansion strategy for adam-mcp.

---

## MVP Operations (v0.1) - 12 Core Operations

Target: Engineering-grade machine parts (M10 bolt, nut, flange success criteria)

### Primitives (2 operations)

1. **create_box** - Create box with length/width/height (for testing/validation)
2. **create_cylinder** - Create cylinder with radius/height (shafts, bodies)

### Sketch Operations (3 operations)

3. **create_sketch** - Create new sketch on plane (XY/XZ/YZ)
4. **add_sketch_circle** - Add circle to sketch (holes, profiles)
5. **add_sketch_constraint** - Add constraint (distance, coincident, equal, etc.)

### PartDesign Features (5 operations)

6. **create_pad** - Extrude sketch into solid (hex heads, flanges)
7. **create_pocket** - Cut from solid using sketch (hex holes, cutouts)
8. **create_fillet** - Round edges with specified radius (edge rounding)
9. **create_chamfer** - Bevel edges with specified distance (nut chamfers)
10. **create_thread** - Add threads to cylindrical surface (bolt/nut threads)

### Boolean Operations (2 operations)

11. **create_fusion** - Union of two shapes (combine head + shaft)
12. **create_cut** - Difference of two shapes (subtract material)

**Coverage:** Sufficient for MVP success criteria (M10 bolt, M10 nut, flange).

**Philosophy:** Start minimal, expand incrementally based on real needs. Each operation properly designed with validation.

---

## Post-MVP Expansion - Incremental Growth

Add operations as real needs arise. Each new operation includes:
- Pydantic model with validation
- Handler implementation
- Geometric validation
- Rich schema documentation

**Priority expansion areas:**

### Additional Primitives (3 operations)
- **create_sphere** - Sphere with radius (rounded features)
- **create_cone** - Cone with base/top radius (tapers)
- **create_torus** - Torus with ring/tube radius (rounded profiles)

### Additional Sketch Geometry (3 operations)
- **add_sketch_line** - Line segment (general profiles)
- **add_sketch_arc** - Arc (rounded corners)
- **add_sketch_rectangle** - Rectangle (quick rectangular profiles)

### Additional Features (3 operations)
- **create_revolution** - Revolve sketch around axis (axisymmetric parts)
- **create_hole** - Create hole with depth/type (simple/threaded/countersunk)
- **create_loft** - Loft between profiles (complex transitions)

### Pattern Operations (3 operations)
- **create_linear_pattern** - Array in linear pattern (bolt holes)
- **create_polar_pattern** - Array in circular pattern (flange holes)
- **create_mirror** - Mirror across plane (symmetric parts)

**Total future scope:** ~24 operations for comprehensive coverage (~50 LOC each)

---

## Future Possibilities - Beyond Core Operations

**IF extensive production use reveals needs not met by structured operations:**

### Specialized Workbenches
- Sheet metal (bends, flanges)
- Arch (walls, structural elements)
- TechDraw (2D drawings, dimensions)
- Path (CNC toolpaths)

### Advanced Geometry
- Multi-section loft, helix, pipe
- Datum planes, axes, points
- Advanced constraints (tangent, perpendicular, expressions)

**Approach:** Design proper structured operations for common patterns. Only consider Python fallback if structured approach proves fundamentally insufficient after extensive use.

**See context/DECISIONS.md "Python Fallback - Explicitly Rejected" for reasoning.**

---

## Operation Boundary Definition

**One operation = Create or modify ONE FreeCAD object**

**Allowed in one operation:**
- ✓ Create one object with all its properties
- ✓ Modify multiple properties of one object
- ✓ Create one sketch with multiple geometry elements and constraints
- ✓ Create one boolean operation (references other objects but creates one result)
- ✓ Create one pattern/array (one array object referencing source)

**NOT allowed (split into multiple operations):**
- ✗ Create multiple independent primitives
- ✗ Create object AND add feature to it (create box AND fillet it)
- ✗ Modify multiple independent objects

**Rationale:** One object per operation enables:
- Clear error attribution (know exactly what failed)
- Tractable validation (check one object's state)
- Natural debugging (inspect after each step)
- Sequential workflow matching CAD's dependency chain

---

## Validation Strategy

**3-layer validation for all operations:**

### Layer 1: Pre-execution (Pydantic)
- Type checking (float, str, int, enums)
- Range validation (dimensions > 0, angles within bounds)
- Required fields present
- Enum values valid (plane must be XY/XZ/YZ)

**Catches:** Syntax errors, type mismatches, missing fields, invalid enums

### Layer 2: Semantic validation (Custom)
- Object existence (referenced objects exist in document)
- Geometric constraints (fillet radius doesn't exceed edge length)
- Dependency checks (sketch exists before pad)

**Catches:** Invalid references, impossible geometry, broken dependencies

### Layer 3: Post-execution (FreeCAD validation)
- Document recomputes successfully
- All shapes geometrically valid (Shape.isValid())
- No objects in invalid state
- No broken references

**Catches:** Corrupted geometry, self-intersections, invalid topology

---

## Adding New Operations

**Process for adding operations:**

1. **Define Pydantic model in `models.py`:**
   ```python
   class CreateWidget(BaseOperation):
       action: Literal["create_widget"] = "create_widget"
       name: str
       size: float = Field(gt=0, description="Widget size in mm")
       # ... more parameters
   ```

2. **Add to Operation union type:**
   ```python
   Operation = CreateBox | CreateCylinder | ... | CreateWidget
   ```

3. **Implement execution in `tools/cad_operations.py`:**
   ```python
   def _execute_create_widget(op: CreateWidget, doc) -> str:
       widget = doc.addObject("Part::Widget", op.name)
       widget.Size = op.size
       doc.recompute()
       return op.name
   ```

4. **Add to operation dispatcher:**
   ```python
   OPERATION_HANDLERS = {
       "create_widget": _execute_create_widget,
       # ...
   }
   ```

5. **Test with real example**
6. **Document in this file**

---

## Why No Python Fallback?

**Decision:** adam-mcp uses ONLY structured operations. No `execute_custom_code()` tool.

**Rationale:**
1. **Better validation:** Structured operations validate before execution, not during
2. **Better errors:** "Radius 15mm exceeds edge 10mm" vs "Part.fillet failed"
3. **Better discovery:** MCP schema shows what's possible, Python code doesn't
4. **Forces quality:** Must design proper operations, not write escape-hatch code
5. **Simpler security:** No sandboxing needed, just Pydantic validation

**Alternative:** When you need a new capability, design it properly:
- Add Pydantic model with validation
- Add handler with semantic checks
- Get all benefits: pre-validation, clear errors, schema, type safety

**Full reasoning:** See context/DECISIONS.md "Python Fallback - Explicitly Rejected"

---

**Last Updated:** 2025-11-18
