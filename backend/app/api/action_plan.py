from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.ai import generate_action_plan

router = APIRouter(prefix="/api/action-plan", tags=["Action Plan"])

class ActionPlanRequest(BaseModel):
    situation: str

@router.post("")
def action_plan(request: ActionPlanRequest):
    try:
        return generate_action_plan(request.situation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
