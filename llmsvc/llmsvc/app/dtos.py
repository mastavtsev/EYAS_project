from pydantic import BaseModel
from typing import Dict, Any

class TextInDTO(BaseModel):
    report_id : int
    params: Dict[str, Any]

class TextCorrectInDTO(BaseModel):
    report_id : int
    text: str
    params: Dict[str, Any]

class TextGenerationOutDTO(BaseModel):
    success: bool