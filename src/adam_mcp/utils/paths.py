"""Path resolution utilities"""

from pathlib import Path

from adam_mcp.constants.paths import DEFAULT_PROJECTS_DIR


def resolve_project_path(path: str) -> str:
    """
    Resolve project path to absolute path.

    If path is relative or just a filename, resolves to DEFAULT_PROJECTS_DIR.
    If path is absolute, returns as-is after expansion.

    Args:
        path: Path to resolve (can be relative, absolute, or just filename)

    Returns:
        Absolute path to project file

    Examples:
        "bracket.FCStd" -> "~/freecad_projects/bracket.FCStd" (expanded)
        "designs/bracket.FCStd" -> "~/freecad_projects/designs/bracket.FCStd"
        "~/custom/bracket.FCStd" -> "~/custom/bracket.FCStd" (expanded)
        "/abs/path/bracket.FCStd" -> "/abs/path/bracket.FCStd"
    """
    path_obj = Path(path).expanduser()

    # If already absolute, return as-is
    if path_obj.is_absolute():
        return str(path_obj.resolve())

    # Relative path or filename → resolve to default projects directory
    default_dir = Path(DEFAULT_PROJECTS_DIR).expanduser().resolve()
    return str(default_dir / path_obj)


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
