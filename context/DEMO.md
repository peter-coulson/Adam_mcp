# Demo Strategy

Critical decisions for adam-mcp demonstration.

---

## Demo Philosophy

Showcase **two key value propositions**:

1. **Full Creation Workflow** - Create complete industrial parts from scratch
2. **Modification Beyond Current Capabilities** - Edit parts using operations we can't create yet

**Why:** Shows current capabilities (pipe flange) AND extensibility (nyloc nut with Revolution, Chamfer, Fusion)

---

## Part Selection Rationale

### Part 1: 4-inch Class 150 Pipe Flange

**Why this part:**
- ✅ Looks 100% complete (flanges use bolts, no threads needed)
- ✅ Multi-feature complexity (concentric circles, bolt pattern, raised face)
- ✅ Real ISO 7005 standard (professional industrial component)
- ✅ Demonstrates full creation workflow from scratch
- ❌ NOT chosen: Bolts (would need helical threads to look complete)

**Demonstrates:**
- Sequential operations (sketch → pad → pocket pattern → raised face)
- Pattern creation (8 bolt holes at 45° intervals)
- Engineering standards (ISO 7005 dimensions)

### Part 2: M3 Nyloc Nut

**Why this part:**
- ✅ Demonstrates modification of complex pre-existing parts
- ✅ Uses operations beyond current creation capabilities (Revolution, Chamfer, Fusion)
- ✅ Real-world use case (editing CAD library parts)
- ✅ Proves extensibility (can work with operations we can't create yet)
- ✅ Looks complete (internal threads not primary visual feature)

**Demonstrates:**
- Inspection workflow (list_objects → get_object_details)
- Modification workflow (modify properties while preserving complex features)
- Extensibility (edit Revolution, Chamfer, Fusion without creation tools)

---

## Success Criteria

After watching demo, viewers understand:

✅ adam-mcp creates complete industrial parts (no missing visual features)
✅ System works with complex pre-existing parts
✅ Modification extends beyond creation capabilities
✅ Professional output meets engineering standards (ISO 7005)
✅ Structured operations provide type-safe validation
✅ Extensible architecture (edit advanced features before implementing creation tools)

---

## Why NOT Other Parts

**Threaded bolts:**
- ❌ Current thread tool only adds metadata (cosmetic)
- ❌ Helical thread geometry requires Revolution + Sweep (not implemented)
- ❌ Would look incomplete without visible threads

**Simple washers:**
- ❌ Too trivial for demo (2 circles + extrude)
- ❌ Doesn't showcase multi-feature complexity

**Gears:**
- ❌ Requires parametric tooth profiles (complex sketch operations not implemented)

---

**Last Updated:** 2025-11-18
