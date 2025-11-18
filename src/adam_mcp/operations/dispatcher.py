"""Operation dispatcher - routes operations to handlers"""


from collections.abc import Callable
from typing import Any

from adam_mcp.core.working_files import auto_save_after
from adam_mcp.models.operations.primitives import CreateCylinder
from adam_mcp.models.operations.sketches import AddSketchCircle, CreateSketch
from adam_mcp.models.responses import OperationResult
from adam_mcp.operations.handlers.primitives import execute_create_cylinder
from adam_mcp.operations.handlers.sketches import (
    execute_add_sketch_circle,
    execute_create_sketch,
)
from adam_mcp.utils.errors import format_freecad_error
from adam_mcp.utils.freecad import get_active_document
from adam_mcp.utils.validation import validate_document

# Union type of all supported operations (MVP Iteration 2: primitives + sketches)
Operation = CreateCylinder | CreateSketch | AddSketchCircle

# Map operation actions to handler functions
OPERATION_HANDLERS: dict[str, Callable[[Any, Any], str]] = {
    "create_cylinder": execute_create_cylinder,
    "create_sketch": execute_create_sketch,
    "add_sketch_circle": execute_add_sketch_circle,
}


@auto_save_after
def execute_operation(operation: Operation) -> OperationResult:
    """
    Execute a CAD operation with 3-layer validation.

    Validation layers:
    1. Pre-execution (Pydantic): Type checking and range validation (automatic)
    2. Semantic validation: Business logic (object existence, geometric constraints)
    3. Post-execution: FreeCAD geometry validation

    Args:
        operation: Validated operation to execute

    Returns:
        OperationResult with success status and message

    Raises:
        No exceptions - all errors caught and returned in OperationResult
    """
    try:
        # Get active document
        doc = get_active_document()

        # Get handler for this operation type
        handler = OPERATION_HANDLERS.get(operation.action)
        if not handler:
            return OperationResult(
                success=False,
                message=f"Unknown operation: {operation.action}",
                error_type="validation",
            )

        # Execute operation (semantic validation happens inside handler)
        affected_name = handler(operation, doc)

        # Post-execution validation (geometry check)
        if not validate_document(doc):
            return OperationResult(
                success=False,
                message="Operation produced invalid geometry. Document validation failed.",
                error_type="geometry",
            )

        return OperationResult(
            success=True,
            message=f"Successfully created {affected_name}",
            affected_object=affected_name,
        )

    except ValueError as e:
        # Semantic validation errors (e.g., object already exists, invalid parameters)
        return OperationResult(
            success=False,
            message=str(e),
            error_type="validation",
        )
    except Exception as e:
        # FreeCAD runtime errors
        return OperationResult(
            success=False,
            message=format_freecad_error(e, "Operation failed"),
            error_type="runtime",
        )
