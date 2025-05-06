from fastapi import HTTPException
from typing import Any, Optional

def get_or_404(obj: Optional[Any], error_message: str) -> Any:
    """
    Return obj if it's not None; otherwise raise a 404 HTTPException.
    """
    if obj is None:
        raise HTTPException(status_code=404, detail=error_message)
    return obj

def assert_true_or_404(condition: bool, error_message: str) -> None:
    """
    If condition is False, raise a 404 HTTPException.
    """
    if not condition:
        raise HTTPException(status_code=404, detail=error_message)
