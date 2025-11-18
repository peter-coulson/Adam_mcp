# Tool Design Patterns

MCP tool architecture and design decisions for adam-mcp.

---

## Tool Philosophy: Flat, Operation-Specific Tools

**Decision:** One tool per operation with flat parameters (NOT unified tool with complex parameters)

**The 7 MVP operation tools:**
- `create_cylinder_tool(name, radius, height, ...)`
- `create_sketch_tool(name, plane, ...)`
- `add_sketch_circle_tool(sketch_name, center, radius, ...)`
- `create_pad_tool(name, sketch, length, ...)`
- `create_pocket_tool(name, sketch, length, ...)`
- `create_thread_tool(name, base, thread_type, length, ...)`
- `modify_object_tool(name, property, value, ...)`

**Plus infrastructure tools:**
- `list_objects_tool()` - List all objects
- `get_object_details_tool(names)` - Inspect specific objects
- Document management (open, create, commit, rollback, etc.)

**Total: 11 operation tools + 9 infrastructure tools = 20 tools**

---

## Why Flat Tools Over Unified Tool?

**Rejected approach:** Single `execute_operation_tool(operation: Operation)` with nested JSON

**Problems with unified tool:**
1. **MCP integration issues** - Nested Pydantic models get stringified by some MCP clients
2. **Poor discoverability** - One giant tool vs clear operation-specific tools
3. **Token bloat** - Full schema (500-800 lines) sent on every call vs cached per-tool schemas
4. **Unclear errors** - "Invalid operation" vs "Invalid radius for create_cylinder"

**Benefits of flat tools:**
1. **Natural discovery** - Tool list shows all operations directly (no separate discovery tool)
2. **MCP compatible** - Flat parameters work with all MCP clients
3. **Type-safe** - FastMCP generates clean schemas from function signatures
4. **Self-documenting** - Each tool name + docstring is clear
5. **Scales well** - ~17 MVP tools, ~32 for full feature set (manageable)

---

## Discovery: Natural via Tool List

**Decision:** NO separate discovery tool. Tool list provides discovery.

**Rejected:** `list_available_operations(category)` discovery tool

**Why natural discovery works:**
- Claude sees all 20 tools in tool list at connection time
- Tool names are self-explanatory: `create_cylinder_tool`, `create_pad_tool`
- Each tool has rich docstring with examples
- MCP schemas cached (not sent per-call)
- Standard UX pattern (tools = capabilities)

**Example tool list Claude sees:**
```
Available tools:
- create_cylinder_tool: Create cylindrical primitive
- create_pad_tool: Extrude sketch into solid
- modify_object_tool: Modify object properties
- list_objects_tool: List all objects in document
- get_object_details_tool: Get detailed object info
...
```

Clear, scannable, discoverable.

---

## Tool Implementation Pattern

**3-layer architecture:**

1. **MCP tool** (server.py) - Thin wrapper, FastMCP registration
2. **Execution function** (tools/execution.py) - Flat parameters → Pydantic model
3. **Operation handler** (operations/handlers/) - FreeCAD API calls

**Example:**
```python
# Layer 1: MCP tool (server.py)
@mcp.tool()
def create_cylinder_tool(name: str, radius: float, height: float, ...) -> OperationResult:
    """Create cylindrical primitive."""
    return create_cylinder(name, radius, height, ...)

# Layer 2: Execution function (tools/execution.py)
def create_cylinder(name, radius, height, ...) -> OperationResult:
    operation = CreateCylinder(name=name, radius=radius, ...)
    return execute_operation(operation)

# Layer 3: Handler (operations/handlers/primitives.py)
def execute_create_cylinder(op: CreateCylinder, doc) -> str:
    cylinder = doc.addObject("Part::Cylinder", op.name)
    cylinder.Radius = op.radius
    doc.recompute()
    return op.name
```

**Why 3 layers:**
- Layer 1: MCP-friendly interface (flat params)
- Layer 2: Bridge to type-safe models
- Layer 3: FreeCAD operations with validation

---

## Tool Scaling

**Current: 7 operations (MVP)**
- ~60 LOC per operation (model + handler + function + tool)
- Clear, maintainable

**Future: 25-30 operations (full feature set)**
- Same pattern, scales linearly
- Each operation independent
- No refactoring needed

**Pattern proven:** MVP shows this scales without complexity.

---

**Last Updated:** 2025-11-18
