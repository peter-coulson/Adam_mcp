"""
Constants for adam-mcp

All configuration values, defaults, constraints, and message templates.
Single source of truth for magic numbers and strings.
"""

# ============================================================================
# Server Metadata
# ============================================================================

SERVER_NAME = "adam-mcp"
SERVER_VERSION = "0.1.0"

# ============================================================================
# Document Defaults
# ============================================================================

DEFAULT_DOCUMENT_NAME = "CAD_Design"
DEFAULT_SKETCH_NAME = "Sketch"
MAX_DOCUMENT_NAME_LENGTH = 100

# ============================================================================
# Dimension Constraints (mm)
# ============================================================================

MIN_DIMENSION_MM = 0.1
MAX_DIMENSION_MM = 10000.0
MIN_FILLET_RADIUS_MM = 0.1
MAX_FILLET_RADIUS_MM = 1000.0

# ============================================================================
# Angular Constraints (degrees)
# ============================================================================

MIN_ANGLE_DEGREES = -360.0
MAX_ANGLE_DEGREES = 360.0

# ============================================================================
# Working File Configuration
# ============================================================================

AUTO_SAVE_INTERVAL = 5  # Save working file every N operations
WORK_FILE_SUFFIX = ".work"  # Extension for working files
VALIDATE_BEFORE_COMMIT = True  # Safety gate for commits
WORK_DIR_ENV_VAR = "ADAM_MCP_WORK_DIR"  # Environment variable for custom work directory

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

# ============================================================================
# Error Message Templates
# ============================================================================

# Document errors
ERROR_NO_ACTIVE_DOC = "No active FreeCAD document. Open or create a document first."
ERROR_NO_OPEN_DOC = "No document open. Use open_document() or create_document() first."
ERROR_FREECAD_API = "FreeCAD API error: {error}. {suggestion}"
ERROR_INVALID_DIMENSION = "Dimension {value} mm is outside valid range ({min_val}-{max_val} mm)"
ERROR_INVALID_OBJECT = "Object '{name}' not found in active document"
ERROR_FILE_NOT_FOUND = "File not found: {path}"
ERROR_VALIDATION_FAILED = (
    "Document validation failed. Cannot commit corrupted state. "
    "Fix errors or use rollback_working_changes() to discard changes."
)

# Environment setup errors
ERROR_PATH_NOT_FOUND = "FreeCAD installation not found at expected path: {}"
ERROR_PLATFORM_UNSUPPORTED = "Unsupported platform: {}"
ERROR_INSTALL_INSTRUCTIONS = """
FreeCAD not found. Please install FreeCAD:

macOS:
  brew install freecad

Linux (Ubuntu/Debian):
  sudo apt-get install freecad

Linux (Fedora):
  sudo dnf install freecad

Windows:
  Download from https://www.freecad.org/downloads.php

Or set FREECAD_PATH environment variable to custom installation location.
"""

# ============================================================================
# Success Message Templates
# ============================================================================

SUCCESS_DOC_CREATED = "Created document: {name}"
SUCCESS_DOC_OPENED = "Opened document: {name}"
SUCCESS_OPERATION = "Operation completed successfully"
SUCCESS_CHANGES_COMMITTED = "Changes committed to {path}"
SUCCESS_CHANGES_ROLLED_BACK = "Working changes discarded. Reset to last commit: {path}"

# ============================================================================
# Status Messages
# ============================================================================

MSG_SUCCESS = "✓ FreeCAD environment configured"
MSG_LIBRARY_PATH = "  - Library path: {}"
MSG_MODULES_PATH = "  - Modules path: {}"
MSG_EXTENSIONS_PATH = "  - Extensions path: {}"
MSG_PLATFORM = "  - Platform: {}"
MSG_ENV_OVERRIDE = "  - Using FREECAD_PATH override: {}"
