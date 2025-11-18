"""Core infrastructure for adam-mcp"""

from adam_mcp.core.freecad_env import setup_freecad_environment
from adam_mcp.core.working_files import (
    auto_save_after,
    auto_save_working_file,
    get_active_main_file_path,
    get_active_work_file_path,
    get_work_file_path,
    increment_operation_counter,
    reset_operation_counter,
    set_active_files,
    setup_working_file,
)

__all__ = [
    "setup_freecad_environment",
    "auto_save_after",
    "get_active_main_file_path",
    "get_active_work_file_path",
    "get_work_file_path",
    "increment_operation_counter",
    "reset_operation_counter",
    "set_active_files",
    "setup_working_file",
    "auto_save_working_file",
]
