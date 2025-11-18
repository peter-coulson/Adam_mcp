"""File paths and environment variables"""

import os

# ============================================================================
# Default Directories
# ============================================================================

# Default directory for CAD projects (configurable via environment variable)
DEFAULT_PROJECTS_DIR = os.environ.get(
    "ADAM_MCP_DEFAULT_DIR", "~/Documents/Projects/adam_mcp/dev_projects"
)

# ============================================================================
# FreeCAD Environment - macOS Paths
# ============================================================================

MACOS_APP_PATH = "/Applications/FreeCAD.app/Contents"
MACOS_RESOURCES = f"{MACOS_APP_PATH}/Resources"
MACOS_LIB = f"{MACOS_RESOURCES}/lib"
MACOS_MOD = f"{MACOS_RESOURCES}/Mod"
MACOS_EXT = f"{MACOS_RESOURCES}/Ext"
MACOS_FRAMEWORKS = f"{MACOS_APP_PATH}/Frameworks"

# ============================================================================
# FreeCAD Environment - Linux Paths
# ============================================================================

LINUX_LIB = "/usr/lib/freecad/lib"
LINUX_MOD = "/usr/lib/freecad/Mod"
LINUX_EXT = "/usr/lib/freecad/Ext"

# ============================================================================
# FreeCAD Environment - Windows Paths
# ============================================================================

WINDOWS_PROGRAM_FILES = "C:/Program Files/FreeCAD"
WINDOWS_LIB = f"{WINDOWS_PROGRAM_FILES}/bin"
WINDOWS_MOD = f"{WINDOWS_PROGRAM_FILES}/Mod"
WINDOWS_EXT = f"{WINDOWS_PROGRAM_FILES}/Ext"

# ============================================================================
# Environment Variable Names
# ============================================================================

ENV_VAR_FREECAD_PATH = "FREECAD_PATH"
ENV_VAR_MACOS_LIBRARY = "DYLD_LIBRARY_PATH"
ENV_VAR_MACOS_FRAMEWORK = "DYLD_FRAMEWORK_PATH"
ENV_VAR_LINUX_LIBRARY = "LD_LIBRARY_PATH"
ENV_VAR_WINDOWS_PATH = "PATH"
