import traceback
from typing import Any


def format_execution_error(error: Exception) -> str:
    if isinstance(error, SyntaxError):
        return f"SyntaxError: {error.msg} (line {error.lineno})"

    formatted = traceback.format_exception_only(type(error), error)
    return "".join(formatted).strip() or str(error)
