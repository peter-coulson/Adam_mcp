"""
Working file infrastructure for adam-mcp

Manages working files for safe editing with auto-save and commit/rollback.
"""

import os
import shutil
import tempfile
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, cast

from adam_mcp.constants.operations import AUTO_SAVE_INTERVAL, WORK_DIR_ENV_VAR, WORK_FILE_SUFFIX

T = TypeVar("T")

if TYPE_CHECKING:
    import FreeCAD
else:
    # Import FreeCAD at runtime after environment setup
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


# ============================================================================
# Global State (Working File Management)
# ============================================================================

_active_main_file_path: str | None = None
_active_work_file_path: str | None = None
_operation_counter: int = 0


# ============================================================================
# State Accessors
# ============================================================================


def get_active_main_file_path() -> str | None:
    """Get the current main file path"""
    return _active_main_file_path


def get_active_work_file_path() -> str | None:
    """Get the current working file path"""
    return _active_work_file_path


def set_active_files(main_path: str, work_path: str) -> None:
    """Set the active main and working file paths"""
    global _active_main_file_path, _active_work_file_path
    _active_main_file_path = main_path
    _active_work_file_path = work_path


def reset_operation_counter() -> None:
    """Reset the operation counter to zero"""
    global _operation_counter
    _operation_counter = 0


# ============================================================================
# Working File Path Management
# ============================================================================


def _is_valid_freecad_file(file_path: str) -> bool:
    """
    Validate that a file can be opened by FreeCAD

    Args:
        file_path: Path to file to validate

    Returns:
        True if file can be opened, False otherwise

    This is used to detect corrupted .work files before attempting to use them.
    """
    if not FreeCAD:
        return False

    try:
        # Try to open the file in a new document
        # Store current active document to restore after validation
        current_doc = FreeCAD.ActiveDocument
        current_doc_name = current_doc.Name if current_doc else None

        # Attempt to open the file
        test_doc = FreeCAD.open(file_path)

        # If successful, close it and restore previous state
        if test_doc:
            FreeCAD.closeDocument(test_doc.Name)

        # Restore previous active document if there was one
        if current_doc_name and current_doc_name in [
            d.Name for d in FreeCAD.listDocuments().values()
        ]:
            FreeCAD.setActiveDocument(current_doc_name)

        return True

    except (RuntimeError, OSError):
        # File is corrupted or invalid
        return False


def get_work_file_path(main_file_path: str) -> str:
    """
    Determine working file path from main file path

    Args:
        main_file_path: Path to main .FCStd file

    Returns:
        Path to working file (with _work suffix before .FCStd extension)

    Examples:
        - "bracket.FCStd" → "bracket_work.FCStd"
        - "/path/to/bolt.FCStd" → "/path/to/bolt_work.FCStd"

    Uses environment variable ADAM_MCP_WORK_DIR if set, otherwise
    places working file in same directory as main file.
    """
    main_path = Path(main_file_path).resolve()

    # Check for custom work directory
    work_dir_str = os.environ.get(WORK_DIR_ENV_VAR)

    if work_dir_str:
        # Use ternary operator for temp directory selection
        work_dir: Path = (
            Path(tempfile.gettempdir()) / "adam_mcp_work"
            if work_dir_str == "temp"
            else Path(work_dir_str)
        )

        # Create work directory if needed
        work_dir.mkdir(parents=True, exist_ok=True)

        # Insert suffix before extension: "bracket.FCStd" → "bracket_work.FCStd"
        work_file_name = main_path.stem + WORK_FILE_SUFFIX + main_path.suffix
        return str(work_dir / work_file_name)

    # Default: same directory as main file
    # Insert suffix before extension: "bracket.FCStd" → "bracket_work.FCStd"
    work_file_name = main_path.stem + WORK_FILE_SUFFIX + main_path.suffix
    return str(main_path.parent / work_file_name)


def setup_working_file(main_file_path: str) -> str:
    """
    Setup working file from main file

    Args:
        main_file_path: Path to main .FCStd file

    Returns:
        Path to working file

    RESUME BY DEFAULT: If working file already exists and is valid, it is used as-is
    (preserves uncommitted changes). If the working file exists but is corrupted,
    it will be replaced with a fresh copy from the main file.

    Use rollback_working_changes() to explicitly discard changes and reset from main.
    """
    work_file_path = get_work_file_path(main_file_path)

    # Resume editing if work file already exists AND is valid
    if Path(work_file_path).exists():
        # Validate the work file by attempting to open it with FreeCAD
        if FreeCAD and _is_valid_freecad_file(work_file_path):
            return work_file_path
        # Work file is corrupted - delete it and recreate from main
        Path(work_file_path).unlink(missing_ok=True)

    # Initialize work file from main if main exists
    if Path(main_file_path).exists():
        shutil.copy2(main_file_path, work_file_path)

    return work_file_path


# ============================================================================
# Auto-save Infrastructure
# ============================================================================


def auto_save_working_file() -> None:
    """
    Auto-save working file (called after operations)

    Saves the active document to the working file path.
    Silent fail if no active document or no working file configured.
    """
    global _active_work_file_path

    if FreeCAD is None:
        return

    doc = FreeCAD.ActiveDocument
    if doc and _active_work_file_path:
        try:
            doc.save()
        except (RuntimeError, OSError) as e:
            # Log but don't crash - auto-save is best-effort
            print(f"Warning: Auto-save failed: {e}")


def increment_operation_counter() -> None:
    """
    Track operations and trigger auto-save

    Increments operation counter and triggers auto-save
    every AUTO_SAVE_INTERVAL operations.
    """
    global _operation_counter

    _operation_counter += 1

    if _operation_counter % AUTO_SAVE_INTERVAL == 0:
        auto_save_working_file()


def auto_save_after(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator: auto-save working file after tool execution

    Wraps a tool function to automatically increment the operation
    counter and trigger auto-save after successful execution.

    Args:
        func: Tool function to wrap

    Returns:
        Wrapped function with auto-save behavior
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        result = func(*args, **kwargs)
        increment_operation_counter()
        return result

    return cast(Callable[..., T], wrapper)
