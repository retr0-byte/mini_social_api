from typing import Literal, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    status: Literal["success", "error"] = "success"
    data: Optional[T] = None