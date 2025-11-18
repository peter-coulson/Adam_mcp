"""
Document management tools for adam-mcp

Tools for creating, opening, and managing FreeCAD documents.
"""

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import Field

from adam_mcp.constants import (
    ERROR_FILE_NOT_FOUND,
    ERROR_NO_OPEN_DOC,
    ERROR_VALIDATION_FAILED,
    SUCCESS_CHANGES_COMMITTED,
    SUCCESS_CHANGES_ROLLED_BACK,
    VALIDATE_BEFORE_COMMIT,
)
from adam_mcp.models import DocumentInfo, HealthCheckResponse
from adam_mcp.utils import (
    format_freecad_error,
    get_active_document,
    get_freecad_version,
    validate_document,
)
from adam_mcp.working_files import (
    get_active_main_file_path,
    get_active_work_file_path,
    reset_operation_counter,
    set_active_files,
    setup_working_file,
)

if TYPE_CHECKING:
    import FreeCAD
else:
    # Import FreeCAD at runtime after environment setup
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


# ============================================================================
# Document Management Tools
# ============================================================================


def health_check() -> HealthCheckResponse:
    """
    Check server health and FreeCAD integration status.

    Returns health information including FreeCAD version and active document status.
    Use this to verify the server is running correctly.
    """
    try:
        version = get_freecad_version()
        active_doc = FreeCAD.ActiveDocument if FreeCAD else None
        doc_name = active_doc.Name if active_doc else None

        return HealthCheckResponse(
            status="healthy",
            freecad_version=version,
            active_document=doc_name,
            message=f"Server running. FreeCAD {version} integrated successfully.",
        )
    except (AttributeError, RuntimeError, ImportError) as e:
        return HealthCheckResponse(
            status="error",
            freecad_version="unknown",
            active_document=None,
            message=f"Health check failed: {str(e)}",
        )


def open_document(path: str = Field(description="Path to .FCStd file to open")) -> DocumentInfo:
    """
    Open existing FreeCAD document for editing.

    Creates a working copy (.work file) for safe editing. The main file is only
    modified when you call commit_changes(). All edits happen on the working file,
    which is auto-saved every 5 operations for crash protection.

    Args:
        path: Path to existing .FCStd file

    Returns:
        Information about the opened document

    Raises:
        FileNotFoundError: If file doesn't exist
        RuntimeError: If file can't be opened
    """
    # Expand user path (~/)
    main_file_path = str(Path(path).expanduser().resolve())

    # Validate main file exists
    if not Path(main_file_path).exists():
        raise FileNotFoundError(ERROR_FILE_NOT_FOUND.format(path=main_file_path))

    try:
        # Setup working file (copies main → work)
        work_file_path = setup_working_file(main_file_path)
        set_active_files(main_file_path, work_file_path)
        reset_operation_counter()

        # Close any existing documents
        if FreeCAD and FreeCAD.ActiveDocument:
            FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)

        # Open working file in FreeCAD
        doc = FreeCAD.open(work_file_path)

        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )

    except (RuntimeError, OSError) as e:
        raise RuntimeError(
            format_freecad_error(e, f"Ensure file is a valid FreeCAD document: {main_file_path}")
        ) from e


def create_document(
    path: str = Field(description="Path where new .FCStd file will be saved"),
) -> DocumentInfo:
    """
    Create new FreeCAD document and save to path.

    Creates both the main file and working file. The main file is saved with the
    initial blank state. All subsequent edits happen on the working file, which is
    auto-saved every 5 operations. Use commit_changes() to update the main file.

    Args:
        path: Path where document will be saved (e.g., ~/designs/bracket.FCStd)

    Returns:
        Information about the created document

    Raises:
        RuntimeError: If document can't be created or saved
    """
    # Expand user path (~/)
    main_file_path = str(Path(path).expanduser().resolve())

    # Ensure parent directory exists
    Path(main_file_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Close any existing documents
        if FreeCAD and FreeCAD.ActiveDocument:
            FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)

        # Create new document
        doc = FreeCAD.newDocument()

        # Save as main file (initial blank state)
        doc.saveAs(main_file_path)

        # Setup working file (copies main → work)
        work_file_path = setup_working_file(main_file_path)
        set_active_files(main_file_path, work_file_path)
        doc.saveAs(work_file_path)
        reset_operation_counter()

        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )

    except (RuntimeError, OSError) as e:
        raise RuntimeError(
            format_freecad_error(e, f"Ensure path is writable: {main_file_path}")
        ) from e


def commit_changes() -> str:
    """
    Commit working file changes to main file.

    This is the ONLY way the main file gets updated. Validates the document before
    committing to ensure geometry is not corrupted. If validation fails, commit is
    rejected and you must fix errors or use rollback_working_changes().

    Returns:
        Success message with path to main file

    Raises:
        RuntimeError: If no document open or validation fails
    """
    main_file_path = get_active_main_file_path()
    work_file_path = get_active_work_file_path()

    if not main_file_path or not work_file_path:
        raise RuntimeError(ERROR_NO_OPEN_DOC)

    doc = get_active_document()

    # Validate before committing (critical safety check)
    if VALIDATE_BEFORE_COMMIT and not validate_document(doc):
        raise RuntimeError(ERROR_VALIDATION_FAILED)

    try:
        # Save work file one more time
        doc.save()

        # Copy work → main (atomic commit)
        shutil.copy2(work_file_path, main_file_path)

        return SUCCESS_CHANGES_COMMITTED.format(path=main_file_path)

    except (OSError, RuntimeError) as e:
        raise RuntimeError(
            format_freecad_error(e, "Check that main file is not open in another application.")
        ) from e


def rollback_working_changes() -> str:
    """
    Discard all working changes and reset from main file.

    Reloads the main file state, discarding all uncommitted work. Use this if you
    mess up and want to start over from the last commit. This is a destructive
    operation - all changes since last commit will be lost.

    Returns:
        Success message with path to main file

    Raises:
        RuntimeError: If no document open
    """
    main_file_path = get_active_main_file_path()
    work_file_path = get_active_work_file_path()

    if not main_file_path or not work_file_path:
        raise RuntimeError(ERROR_NO_OPEN_DOC)

    try:
        # Close current working document
        doc = get_active_document()
        doc_name = doc.Name
        FreeCAD.closeDocument(doc_name)

        # Copy main → work (reset)
        shutil.copy2(main_file_path, work_file_path)

        # Reopen work file
        FreeCAD.open(work_file_path)
        reset_operation_counter()

        return SUCCESS_CHANGES_ROLLED_BACK.format(path=main_file_path)

    except (OSError, RuntimeError) as e:
        raise RuntimeError(format_freecad_error(e, "Failed to rollback changes.")) from e


def get_document_info() -> DocumentInfo:
    """
    Get information about the active document.

    Returns object count and list of objects in the current document.

    Raises:
        RuntimeError: If no active document exists
    """
    try:
        doc = get_active_document()
        return DocumentInfo(
            name=doc.Name, object_count=len(doc.Objects), objects=[obj.Name for obj in doc.Objects]
        )
    except RuntimeError:
        raise
    except AttributeError as e:
        raise RuntimeError(format_freecad_error(e)) from e
