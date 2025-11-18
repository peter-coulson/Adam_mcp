"""
FreeCAD Environment Setup
Configure Python path and environment for FreeCAD integration
"""

import os
import platform
import sys
from pathlib import Path
from typing import NamedTuple

from adam_mcp.constants import (
    ENV_VAR_FREECAD_PATH,
    ENV_VAR_LINUX_LIBRARY,
    ENV_VAR_MACOS_FRAMEWORK,
    ENV_VAR_MACOS_LIBRARY,
    ENV_VAR_WINDOWS_PATH,
    ERROR_INSTALL_INSTRUCTIONS,
    ERROR_PATH_NOT_FOUND,
    ERROR_PLATFORM_UNSUPPORTED,
    LINUX_EXT,
    LINUX_LIB,
    LINUX_MOD,
    MACOS_EXT,
    MACOS_FRAMEWORKS,
    MACOS_LIB,
    MACOS_MOD,
    MSG_ENV_OVERRIDE,
    MSG_EXTENSIONS_PATH,
    MSG_LIBRARY_PATH,
    MSG_MODULES_PATH,
    MSG_PLATFORM,
    MSG_SUCCESS,
    WINDOWS_EXT,
    WINDOWS_LIB,
    WINDOWS_MOD,
)

# ============================================================================
# Data Structures
# ============================================================================


class FreeCADPaths(NamedTuple):
    """FreeCAD installation paths"""

    lib: str
    mod: str
    ext: str
    frameworks: str | None = None  # macOS only


# ============================================================================
# Platform Detection
# ============================================================================


def get_platform_paths() -> FreeCADPaths:
    """
    Detect platform and return appropriate FreeCAD paths

    Returns:
        FreeCADPaths with platform-specific paths

    Raises:
        RuntimeError: If platform is unsupported
    """
    system = platform.system()

    # Check for environment variable override first
    if env_path := os.environ.get(ENV_VAR_FREECAD_PATH):
        print(MSG_ENV_OVERRIDE.format(env_path))
        return FreeCADPaths(
            lib=f"{env_path}/lib",
            mod=f"{env_path}/Mod",
            ext=f"{env_path}/Ext",
            frameworks=f"{env_path}/Frameworks" if system == "Darwin" else None,
        )

    # Platform-specific defaults
    if system == "Darwin":  # macOS
        return FreeCADPaths(
            lib=MACOS_LIB, mod=MACOS_MOD, ext=MACOS_EXT, frameworks=MACOS_FRAMEWORKS
        )
    if system == "Linux":
        return FreeCADPaths(lib=LINUX_LIB, mod=LINUX_MOD, ext=LINUX_EXT)
    if system == "Windows":
        return FreeCADPaths(lib=WINDOWS_LIB, mod=WINDOWS_MOD, ext=WINDOWS_EXT)

    raise RuntimeError(ERROR_PLATFORM_UNSUPPORTED.format(system))


# ============================================================================
# Path Validation
# ============================================================================


def validate_paths(paths: FreeCADPaths) -> None:
    """
    Validate that FreeCAD paths exist

    Args:
        paths: FreeCADPaths to validate

    Raises:
        FileNotFoundError: If required paths don't exist
    """
    # Check library path (most critical)
    if not Path(paths.lib).exists():
        raise FileNotFoundError(ERROR_PATH_NOT_FOUND.format(paths.lib) + ERROR_INSTALL_INSTRUCTIONS)

    # Warn if optional paths missing (don't fail)
    if not Path(paths.mod).exists():
        print(f"Warning: Mod path not found: {paths.mod}")
    if not Path(paths.ext).exists():
        print(f"Warning: Ext path not found: {paths.ext}")


# ============================================================================
# Environment Variable Helpers
# ============================================================================


def _append_to_env_var(var_name: str, new_value: str, separator: str) -> None:
    """
    Append value to environment variable with platform-specific separator

    Args:
        var_name: Environment variable name
        new_value: Value to append (e.g., library path)
        separator: Path separator (":" for Unix, ";" for Windows)
    """
    existing = os.environ.get(var_name, "")
    os.environ[var_name] = f"{new_value}{separator}{existing}" if existing else new_value


# ============================================================================
# Environment Setup
# ============================================================================


def setup_freecad_environment() -> None:
    """
    Configure Python environment for FreeCAD integration

    Call this before importing FreeCAD modules.

    Raises:
        RuntimeError: If platform is unsupported
        FileNotFoundError: If FreeCAD installation not found
    """
    # Detect platform and get paths
    paths = get_platform_paths()
    system = platform.system()

    # Validate paths exist
    validate_paths(paths)

    # Add FreeCAD to Python path
    paths_to_add = [paths.lib, paths.mod, paths.ext]
    for path in paths_to_add:
        if Path(path).exists() and path not in sys.path:
            sys.path.insert(0, path)

    # Set platform-specific environment variables for dynamic library loading
    if system == "Darwin":  # macOS
        os.environ[ENV_VAR_MACOS_LIBRARY] = paths.lib
        if paths.frameworks:
            os.environ[ENV_VAR_MACOS_FRAMEWORK] = paths.frameworks
    elif system == "Linux":
        _append_to_env_var(ENV_VAR_LINUX_LIBRARY, paths.lib, ":")
    elif system == "Windows":
        _append_to_env_var(ENV_VAR_WINDOWS_PATH, paths.lib, ";")

    # Success message
    print(MSG_SUCCESS)
    print(MSG_PLATFORM.format(system))
    print(MSG_LIBRARY_PATH.format(paths.lib))
    print(MSG_MODULES_PATH.format(paths.mod))
    print(MSG_EXTENSIONS_PATH.format(paths.ext))


# ============================================================================
# Test Block
# ============================================================================

if __name__ == "__main__":
    # Constants for test
    TEST_DOC_NAME = "Test"
    TEST_BOX_SIZE_MM = 10.0
    MSG_IMPORT_SUCCESS = "\n✓ FreeCAD imported successfully"
    MSG_VERSION = "  - Version: {}"
    MSG_BUILD = "  - Build: {}"
    MSG_TEST_BOX_CREATED = "\n✓ Created test box"
    MSG_VOLUME = "  - Volume: {} mm³"
    MSG_TEST_PASSED = "\n✓ Setup test passed!"
    ERROR_IMPORT_FAILED = "\n✗ Failed to import FreeCAD: {}"

    try:
        # Setup environment
        setup_freecad_environment()

        # Test FreeCAD import
        import FreeCAD
        import Part

        print(MSG_IMPORT_SUCCESS)
        print(MSG_VERSION.format(".".join(FreeCAD.Version()[:3])))
        print(MSG_BUILD.format(FreeCAD.Version()[3]))

        # Create a simple test object
        doc = FreeCAD.newDocument(TEST_DOC_NAME)
        box = Part.makeBox(TEST_BOX_SIZE_MM, TEST_BOX_SIZE_MM, TEST_BOX_SIZE_MM)

        print(MSG_TEST_BOX_CREATED)
        print(MSG_VOLUME.format(box.Volume))

        FreeCAD.closeDocument(TEST_DOC_NAME)
        print(MSG_TEST_PASSED)

    except (ImportError, FileNotFoundError, RuntimeError) as e:
        print(ERROR_IMPORT_FAILED.format(e))
        sys.exit(1)
