# Demo Prompts

Exact prompts for reproducible adam-mcp demonstration.

---

## Part 1: Create Pipe Flange (2 minutes)

```
Create a 4-inch Class 150 raised face weld neck pipe flange
```

**Expected:** Complete ISO 7005 flange with outer diameter, 8 bolt holes, bore, and raised face

**Verify:**
```
Open the flange in FreeCAD GUI to verify geometry
```

---

## Part 2: Modify Nyloc Nut (1 minute)

```
Open the M3 nyloc nut from dev_projects/test_samples/nyloc_nut_m3.FCStd and inspect its structure
```

**Expected:** List objects (Revolution, Pocket, Chamfer, Cut, Fusion, Compound) and analyze properties

```
Modify this nyloc nut to adapt it for M6 size instead of M3
```

**Expected:** Increase pocket depth (5mm → 8mm) and reposition nylon ring

---

**See context/DEMO.md for strategy and rationale**
