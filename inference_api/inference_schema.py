from pydantic import BaseModel
from typing import Optional

class InferenceRequest(BaseModel):
    """
    Pydantic model for request validation
    """
    query: str
    api_key: str
    chat_history: Optional[str] = None