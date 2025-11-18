"""
adam-mcp: FreeCAD MCP Server

IMPORTANT: FreeCAD environment must be configured before importing FreeCAD modules.
This is done via setup_freecad_environment() which configures Python paths and
environment variables for FreeCAD's dynamic libraries.

Pattern:
    1. Call setup_freecad_environment() ONCE at startup
    2. Import FreeCAD modules
    3. Define and run server
"""

from freecad_env import setup_freecad_environment

# Configure FreeCAD environment (must be first)
setup_freecad_environment()

# Now FreeCAD imports will work
# import FreeCAD
# import Part

# TODO: Implement MCP server
# from fastmcp import FastMCP
# mcp = FastMCP("adam-mcp")
