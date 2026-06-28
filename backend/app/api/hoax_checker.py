from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.ai import analyze_hoax

router = APIRouter(prefix="/api/hoax-checker", tags=["Hoax Checker"])

class HoaxCheckRequest(BaseModel):
    text: str
    type: str = "text"

@router.post("")
def hoax_check(request: HoaxCheckRequest):
    try:
        return analyze_hoax(request.text, request.type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
