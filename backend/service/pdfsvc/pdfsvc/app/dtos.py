from pydantic import BaseModel
from typing import Dict, Any


class PDFInDTO(BaseModel):
    report_id: int
    params: Dict[str, Any]
    source_img: str
    od_img: str
    av_img: str
    mac_img: str
    text: str

class PDFOutDTO(BaseModel):
    success: bool
    pdf_bytes: bytes

