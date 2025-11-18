# Operation Discovery Tool - Final Decision

Problem: How does Claude know which operations are available and what inputs they require?

**DECISION: Lightweight discovery tool (~100 tokens) + Rich Pydantic descriptions**

This document contains the analysis that led to this decision.

---

## Current Situation

**Auto-generated schema from Pydantic:**
- FastMCP generates JSON schema from `Operation` union type
- Claude receives schema with all 21 operation definitions
- Schema is technically complete but potentially overwhelming

**Example of what Claude sees:**
```json
{
  "tool": "execute_standard_operation",
  "parameters": {
    "operation": {
      "anyOf": [
        {
          "type": "object",
          "properties": {
            "action": {"const": "create_box"},
            "name": {"type": "string", "maxLength": 100},
            "length": {"type": "number", "minimum": 0.1, "maximum": 10000},
            "width": {"type": "number", "minimum": 0.1, "maximum": 10000},
            "height": {"type": "number", "minimum": 0.1, "maximum": 10000},
            "position": {"type": "array", "items": {"type": "number"}}
          },
          "required": ["action", "name", "length", "width", "height"]
        },
        // ... 20 more operation types
      ]
    }
  }
}
```

**Issues:**
- Large schema (~500-800 lines for 21 operations)
- No examples of usage
- Not organized by category
- Difficult to browse/discover

---

## Proposed Solution: Discovery Tool

Add **`list_available_operations()`** query tool that returns curated, organized operation list with examples.

### Tool Signature

```python
@mcp.tool()
def list_available_operations(
    category: Literal["all", "primitives", "sketches", "features", "booleans", "modifications"] | None = None
) -> OperationCatalog:
    """
    List available CAD operations with examples and usage guidance.

    Use this to discover what operations are available before executing them.
    Operations are organized by category for easy browsing.

    Args:
        category: Filter by operation category, or None/"all" for complete list

    Returns:
        Catalog of operations with parameters, examples, and usage notes
    """
```

### Response Model

```python
class OperationInfo(BaseModel):
    """Information about one operation type"""
    name: str = Field(description="Operation action name (e.g., 'create_box')")
    category: str = Field(description="Category (primitives, sketches, features, booleans, modifications)")
    description: str = Field(description="What this operation does")
    parameters: dict[str, str] = Field(description="Parameter names and types")
    required: list[str] = Field(description="Required parameters")
    example: str = Field(description="JSON example of this operation")
    usage_notes: str | None = Field(default=None, description="Special usage considerations")

class OperationCatalog(BaseModel):
    """Catalog of available operations"""
    category: str = Field(description="Category being shown ('all' or specific)")
    total_count: int = Field(description="Total number of operations in this category")
    operations: list[OperationInfo] = Field(description="Operation details")
```

### Example Response (Primitives Category)

```json
{
  "category": "primitives",
  "total_count": 5,
  "operations": [
    {
      "name": "create_box",
      "category": "primitives",
      "description": "Create a rectangular box primitive",
      "parameters": {
        "action": "Literal['create_box']",
        "name": "str",
        "length": "float (0.1-10000 mm)",
        "width": "float (0.1-10000 mm)",
        "height": "float (0.1-10000 mm)",
        "position": "tuple[float, float, float] (optional, default: (0,0,0))"
      },
      "required": ["action", "name", "length", "width", "height"],
      "example": "{\"action\": \"create_box\", \"name\": \"Box\", \"length\": 10, \"width\": 20, \"height\": 30, \"description\": \"Create 10x20x30mm box\"}",
      "usage_notes": "Position is optional. Dimensions must be positive."
    },
    {
      "name": "create_cylinder",
      "category": "primitives",
      "description": "Create a cylindrical primitive",
      "parameters": {
        "action": "Literal['create_cylinder']",
        "name": "str",
        "radius": "float (0.1-10000 mm)",
        "height": "float (0.1-10000 mm)",
        "position": "tuple[float, float, float] (optional)",
        "angle": "float (0-360 degrees, optional, default: 360)"
      },
      "required": ["action", "name", "radius", "height"],
      "example": "{\"action\": \"create_cylinder\", \"name\": \"Cylinder\", \"radius\": 5, \"height\": 20, \"description\": \"Create M10 shaft\"}",
      "usage_notes": "Use angle < 360 for partial cylinder (e.g., 180 for half-cylinder)"
    }
    // ... create_sphere, create_cone, create_torus
  ]
}
```

### Example Response (Features Category)

```json
{
  "category": "features",
  "total_count": 7,
  "operations": [
    {
      "name": "create_pad",
      "category": "features",
      "description": "Extrude a sketch into a solid (PartDesign feature)",
      "parameters": {
        "action": "Literal['create_pad']",
        "name": "str",
        "sketch": "str (name of sketch to extrude)",
        "length": "float (0.1-10000 mm)",
        "reversed": "bool (optional, default: false)"
      },
      "required": ["action", "name", "sketch", "length"],
      "example": "{\"action\": \"create_pad\", \"name\": \"Pad\", \"sketch\": \"Sketch\", \"length\": 10, \"description\": \"Extrude sketch 10mm\"}",
      "usage_notes": "Sketch must be closed. Use list_objects() to find sketch names."
    },
    {
      "name": "create_fillet",
      "category": "features",
      "description": "Round edges with specified radius",
      "parameters": {
        "action": "Literal['create_fillet']",
        "name": "str",
        "base": "str (name of object to fillet)",
        "edges": "list[int] (edge indices to fillet)",
        "radius": "float (0.1-1000 mm)"
      },
      "required": ["action", "name", "base", "edges", "radius"],
      "example": "{\"action\": \"create_fillet\", \"name\": \"Fillet\", \"base\": \"Box\", \"edges\": [0, 2, 4, 6], \"radius\": 2, \"description\": \"Fillet top edges\"}",
      "usage_notes": "Use get_object_details() to identify edge indices. Radius must not exceed edge length."
    }
    // ... create_pocket, create_revolution, create_chamfer, etc.
  ]
}
```

---

## Implementation

### Location
Add to `tools/cad_operations.py`

### Code (~150 LOC)

```python
# Operation metadata (single source of truth)
OPERATION_CATALOG = {
    "primitives": [
        OperationInfo(
            name="create_box",
            category="primitives",
            description="Create a rectangular box primitive",
            parameters={
                "action": "Literal['create_box']",
                "name": "str",
                "length": "float (0.1-10000 mm)",
                "width": "float (0.1-10000 mm)",
                "height": "float (0.1-10000 mm)",
                "position": "tuple[float, float, float] (optional, default: (0,0,0))",
            },
            required=["action", "name", "length", "width", "height"],
            example='{"action": "create_box", "name": "Box", "length": 10, "width": 20, "height": 30, "description": "Create box"}',
            usage_notes="Dimensions must be positive. Position is optional.",
        ),
        # ... other primitives
    ],
    "sketches": [
        # ... sketch operations
    ],
    "features": [
        # ... feature operations
    ],
    "booleans": [
        # ... boolean operations
    ],
    "modifications": [
        # ... modification operations
    ],
}

def list_available_operations(
    category: Literal["all", "primitives", "sketches", "features", "booleans", "modifications"] | None = None
) -> OperationCatalog:
    """
    List available CAD operations with examples and usage guidance.

    Use this to discover what operations are available before executing them.
    """
    if category is None or category == "all":
        # Flatten all categories
        all_ops = []
        for cat_ops in OPERATION_CATALOG.values():
            all_ops.extend(cat_ops)
        return OperationCatalog(
            category="all",
            total_count=len(all_ops),
            operations=all_ops,
        )
    else:
        ops = OPERATION_CATALOG.get(category, [])
        return OperationCatalog(
            category=category,
            total_count=len(ops),
            operations=ops,
        )
```

---

## Benefits

### 1. Easy Discovery
**Claude workflow:**
```
User: "Create a hex bolt"
Claude: *calls list_available_operations(category="primitives")*
        "I can see we have cylinders for the shaft. Let me also check features..."
        *calls list_available_operations(category="features")*
        "Perfect, we have create_fillet for rounding edges."
```

### 2. Examples Included
Every operation comes with a working JSON example Claude can adapt.

### 3. Organized by Category
Claude can browse by category instead of scanning 21 flat operations.

### 4. Usage Guidance
Special notes like "Radius must not exceed edge length" help Claude avoid errors.

### 5. Parameter Documentation
Clear parameter types with ranges (e.g., "float (0.1-10000 mm)").

---

## Alternative: Enhance Pydantic Descriptions

**Instead of new tool, make auto-generated schema more helpful:**

```python
class CreateBox(BaseOperation):
    """
    Create a rectangular box primitive.

    Example:
        {"action": "create_box", "name": "Box", "length": 10, "width": 20, "height": 30}
    """
    action: Literal["create_box"] = Field(
        default="create_box",
        description="Operation type (always 'create_box')"
    )
    name: str = Field(
        max_length=100,
        description="Name for the box object (e.g., 'Box', 'BaseBlock')"
    )
    length: float = Field(
        gt=MIN_DIMENSION_MM,
        lt=MAX_DIMENSION_MM,
        description="Box length in millimeters (0.1-10000). Length is X-axis dimension."
    )
    # ... with detailed descriptions
```

**This improves auto-schema but doesn't solve browsing/discovery problem.**

---

## Recommendation

**Implement both:**

1. **Add `list_available_operations()` tool** for discovery and browsing
2. **Enhance Pydantic Field descriptions** for detailed parameter documentation

**Rationale:**
- `list_available_operations()` = browsing/discovery (organized, curated)
- Auto-generated schema = detailed reference (when Claude knows which operation to use)

**Total cost:** ~150 LOC for discovery tool + richer Field descriptions

---

## Updated Tool Count

**MVP tools: 4 total**
1. `list_objects()` - List objects in document
2. `get_object_details(names)` - Get object details
3. **`list_available_operations(category)`** - **NEW: Discover operations**
4. `execute_standard_operation(operation)` - Execute JSON operation

Perfect fit for "3-5 excellent tools" philosophy. Discovery tool is lightweight query, not execution.

---

**FINAL DECISION (2025-11-18):**

Implemented lightweight discovery approach:
- `list_available_operations(category)` returns just operation names by category (~100 tokens)
- Rich Pydantic model docstrings with examples
- Rich Field descriptions with ranges, units, usage notes
- Leverages MCP schema caching (schema sent once at connection, not per-call)
- 4 total tools (structured operations only, no Python fallback)

See MVP_IMPLEMENTATION.md Phase 1.5 for implementation details.
See context/DECISIONS.md for Python fallback rejection reasoning.
