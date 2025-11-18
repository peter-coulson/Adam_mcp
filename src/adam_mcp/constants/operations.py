"""Operation-specific constants"""

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
# Working File Configuration
# ============================================================================

AUTO_SAVE_INTERVAL = 1  # Save working file every N operations (immediate GUI sync)
WORK_FILE_SUFFIX = "_work"  # Suffix for working files (inserted before .FCStd extension)
VALIDATE_BEFORE_COMMIT = True  # Safety gate for commits
WORK_DIR_ENV_VAR = "ADAM_MCP_WORK_DIR"  # Environment variable for custom work directory

# ============================================================================
# Operation Categories (for discovery tool)
# ============================================================================

# Operation categories for discovery (populated incrementally during MVP implementation)
OPERATION_CATEGORIES: dict[str, list[str]] = {
    "primitives": [
        "create_cylinder",  # Iteration 1
    ],
    "sketches": [],
    "features": [],
    "booleans": [],
    "modifications": [],
}
