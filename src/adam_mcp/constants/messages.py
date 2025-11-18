"""Error and success message templates"""

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
