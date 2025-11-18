# Planning

## Project Overview

Building a minimal MCP server that exposes CAD operations for AI interaction through the Model Context Protocol.

## Core Technology Decisions

### CAD Platform: FreeCAD

**Chosen:** FreeCAD

**Rationale:**
- Native Python API (direct imports vs REST overhead)
- Free and open source (no licensing requirements)
- Cross-platform support
- Existing MCP implementation available as reference (`bonninr/freecad_mcp`)
- Strong Python/OOP fit with team experience

**Alternatives Considered:**
- Onshape: Excellent docs, but archived Python client and REST API overhead
- Fusion 360: Requires license
- Rhino: Expensive, dual Python versions

### MCP Framework: Official MCP Python SDK

**Chosen:** `mcp` (Official MCP Python SDK with FastMCP API)

**Installation:**
```bash
pip install mcp
```

**Import Pattern:**
```python
from mcp.server.fastmcp import FastMCP
```

**Rationale:**
- Official Anthropic SDK (maintained by MCP creators)
- Strict specification compliance
- Built specifically for Claude Desktop integration
- Well-documented with progressive complexity
- Decorator-based API (`@mcp.tool()`) minimizes boilerplate
- Type hint integration with automatic Pydantic schema generation
- Python ≥3.10 support

**Alternatives Considered:**
- FastMCP 2.0: More features but independent/overkill for minimal project
- Official SDK is appropriate complexity for 3-5 tools

### Validation Strategy: Pydantic (Selective)

**Approach:** Use Pydantic models where they improve tool quality

**When to Use:**
- Value constraints needed (min/max ranges)
- CAD domain knowledge encoding (radius vs dimension relationships)
- Complex nested structures
- Better schema documentation for Claude

**When to Skip:**
- Simple type validation (FastMCP handles automatically)
- Read-only operations with no parameters
- Basic CRUD where type hints suffice

**Decision Point:** Evaluate per-tool during implementation

## Key Constraints from Brief

1. **Scope:** 3-5 tools (prefer quality over quantity)
2. **Architecture:** Minimal and lightweight
3. **Demo Flow:** Create rounded box (sketch rectangle → extrude → fillet edges)
4. **Local Execution:** Must run locally
5. **Language:** Python (TypeScript also acceptable per brief, but Python chosen)

## Dependencies

### Required
- `mcp` - Official MCP Python SDK
- `FreeCAD` - CAD platform (system install, not pip)
- Python ≥3.10

### Optional
- `pydantic` - Already included with MCP SDK, used for tool parameter validation

## Reference Implementation

**Existing FreeCAD MCP:** `bonninr/freecad_mcp`

**What to Learn From It:**
- Tool design patterns (what operations make sense)
- FreeCAD API usage examples
- Document context structure

**What NOT to Copy:**
- Socket-based IPC architecture (unnecessary complexity)
- `exec()` usage (security risk)
- Hardcoded configuration values
- Limited error handling

**Our Approach:** Simpler single-component architecture with direct FreeCAD API imports

## Architecture Principles

1. **Minimal Server Complexity** - Simple architecture, clear code
2. **Excellent Tool Functionality** - Robust, well-documented operations
3. **Direct API Integration** - No socket layer, direct FreeCAD imports
4. **Type Safety** - Type hints throughout, Pydantic where beneficial

## Development Environment

- Python 3.10+
- FreeCAD installed locally
- MCP SDK via pip
- Development with standard Python tooling

## Notes

- Tool definitions and implementation details to be determined during development
- Validation approach will be evaluated per-tool based on quality requirements
- Focus on demonstrating the minimal flow from brief while maintaining excellent functionality
