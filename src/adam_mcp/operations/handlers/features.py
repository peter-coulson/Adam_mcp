"""Handlers for PartDesign feature operations"""

from typing import TYPE_CHECKING, Any

from adam_mcp.models.operations.features import CreatePad, CreatePocket, CreateThread
from adam_mcp.operations.validators.geometry import (
    validate_sketch_for_pad,
    validate_sketch_for_pocket,
    validate_thread_type,
)
from adam_mcp.operations.validators.references import validate_object_exists

if TYPE_CHECKING:
    import FreeCAD
else:
    try:
        import FreeCAD
    except ImportError:
        FreeCAD = None  # type: ignore[assignment]


def execute_create_pad(operation: CreatePad, doc: Any) -> str:
    """
    Execute CreatePad operation.

    Args:
        operation: CreatePad operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of created pad feature

    Raises:
        ValueError: If validation fails (duplicate name, invalid sketch, etc.)
        RuntimeError: If FreeCAD API call fails
    """
    # Check if object with this name already exists
    if doc.getObject(operation.name) is not None:
        raise ValueError(
            f"Object '{operation.name}' already exists. Choose a different name. "
            "Use list_objects() to see existing objects."
        )

    # Validate sketch exists and is suitable for pad
    is_valid, error_msg = validate_sketch_for_pad(doc, operation.sketch)
    if not is_valid:
        raise ValueError(error_msg)

    # Create Pad feature
    pad = doc.addObject("PartDesign::Pad", operation.name)
    sketch_obj = doc.getObject(operation.sketch)
    pad.Profile = sketch_obj
    pad.Length = operation.length
    pad.Reversed = operation.reversed

    # Recompute document
    doc.recompute()

    return operation.name


def execute_create_pocket(operation: CreatePocket, doc: Any) -> str:
    """
    Execute CreatePocket operation.

    Args:
        operation: CreatePocket operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of created pocket feature

    Raises:
        ValueError: If validation fails (duplicate name, invalid sketch, etc.)
        RuntimeError: If FreeCAD API call fails
    """
    # Check if object with this name already exists
    if doc.getObject(operation.name) is not None:
        raise ValueError(
            f"Object '{operation.name}' already exists. Choose a different name. "
            "Use list_objects() to see existing objects."
        )

    # Validate sketch exists and is suitable for pocket
    is_valid, error_msg = validate_sketch_for_pocket(doc, operation.sketch)
    if not is_valid:
        raise ValueError(error_msg)

    # Create Pocket feature
    pocket = doc.addObject("PartDesign::Pocket", operation.name)
    sketch_obj = doc.getObject(operation.sketch)
    pocket.Profile = sketch_obj
    pocket.Length = operation.length
    pocket.Reversed = operation.reversed

    # Recompute document
    doc.recompute()

    return operation.name


def execute_create_thread(operation: CreateThread, doc: Any) -> str:
    """
    Execute CreateThread operation.

    Args:
        operation: CreateThread operation with validated parameters
        doc: Active FreeCAD document

    Returns:
        Name of threaded object

    Raises:
        ValueError: If validation fails (base object missing, invalid thread type, etc.)
        RuntimeError: If FreeCAD API call fails
    """
    # Check if object with this name already exists
    if doc.getObject(operation.name) is not None:
        raise ValueError(
            f"Object '{operation.name}' already exists. Choose a different name. "
            "Use list_objects() to see existing objects."
        )

    # Validate base object exists
    if not validate_object_exists(doc, operation.base):
        raise ValueError(
            f"Base object '{operation.base}' not found. Use list_objects() to see available objects."
        )

    # Validate thread type
    is_valid, error_msg = validate_thread_type(operation.thread_type)
    if not is_valid:
        raise ValueError(error_msg)

    # Get base object
    base_obj = doc.getObject(operation.base)

    # Create thread using Part::FeaturePython for cosmetic threads
    # Note: FreeCAD's standard approach for threads is to use the Fasteners workbench
    # or Part::Helix. For MVP, we'll create a simple cosmetic representation.
    #
    # In a production system, you would use:
    # 1. Fasteners workbench (if available)
    # 2. Part::Helix + Part::Sweep for actual helical threads
    # 3. Or just modify the base cylinder to show threads are conceptual
    #
    # For MVP simplicity, we'll add a label/property to indicate threading
    # and keep the base geometry (engineers often model without actual thread geometry)

    # Clone the base object with a new name

    threaded_obj = doc.addObject("Part::Feature", operation.name)
    threaded_obj.Shape = base_obj.Shape

    # Add custom property to indicate threading
    threaded_obj.addProperty(
        "App::PropertyString", "ThreadType", "Thread", "ISO metric thread designation"
    )
    threaded_obj.ThreadType = operation.thread_type

    threaded_obj.addProperty("App::PropertyFloat", "ThreadLength", "Thread", "Thread length in mm")
    threaded_obj.ThreadLength = operation.length

    # Recompute document
    doc.recompute()

    return operation.name


# Post-MVP: execute_create_revolution, execute_create_hole, execute_create_fillet,
# execute_create_chamfer, execute_create_draft, execute_create_loft
