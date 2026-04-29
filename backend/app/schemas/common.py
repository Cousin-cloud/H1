from pydantic import BaseModel
from typing import Optional


class ApiResponse(BaseModel):
    message: str
    data: Optional[dict] = None
