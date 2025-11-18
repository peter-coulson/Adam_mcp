"""Path resolution utilities"""

from pathlib import Path

from adam_mcp.constants.paths import DEFAULT_PROJECTS_DIR


def resolve_project_path(path: str) -> str:
    """
    Resolve project path to absolute path within the default projects directory.

    SECURITY: Only relative paths are allowed. All files must be within the
    configured projects directory (DEFAULT_PROJECTS_DIR). This prevents
    accidental or malicious file system access outside the project sandbox.

    Args:
        path: Relative path (filename or subdirectory/filename)

    Returns:
        Absolute path to project file within DEFAULT_PROJECTS_DIR

    Raises:
        ValueError: If path is absolute (starts with / or ~)

    Examples:
        "bracket.FCStd" -> "{DEFAULT_PROJECTS_DIR}/bracket.FCStd"
        "designs/bracket.FCStd" -> "{DEFAULT_PROJECTS_DIR}/designs/bracket.FCStd"
        "fasteners/m10/bolt.FCStd" -> "{DEFAULT_PROJECTS_DIR}/fasteners/m10/bolt.FCStd"
    """
    path_obj = Path(path).expanduser()

    # Reject absolute paths for security
    if path_obj.is_absolute():
        raise ValueError(
            f"Absolute paths not allowed: '{path}'. "
            f"Use relative paths only (e.g., 'bracket.FCStd' or 'designs/bracket.FCStd'). "
            f"Files will be saved to: {DEFAULT_PROJECTS_DIR}"
        )

    # Relative path or filename → resolve to default projects directory
    default_dir = Path(DEFAULT_PROJECTS_DIR).expanduser().resolve()
    resolved_path = (default_dir / path_obj).resolve()

    # Security check: ensure resolved path is still within default directory
    # (prevents ../../../etc/passwd type attacks)
    if not str(resolved_path).startswith(str(default_dir)):
        raise ValueError(
            f"Path escapes project directory: '{path}'. "
            f"Paths must stay within: {DEFAULT_PROJECTS_DIR}"
        )

    return str(resolved_path)


def ensure_projects_directory() -> Path:
    """
    Ensure default projects directory exists.

    Creates the directory if it doesn't exist.

    Returns:
        Path to default projects directory

    Raises:
        RuntimeError: If directory cannot be created
    """
    try:
        projects_dir = Path(DEFAULT_PROJECTS_DIR).expanduser().resolve()
        projects_dir.mkdir(parents=True, exist_ok=True)
        return projects_dir
    except OSError as e:
        raise RuntimeError(
            f"Failed to create projects directory {DEFAULT_PROJECTS_DIR}: {e}"
        ) from e
