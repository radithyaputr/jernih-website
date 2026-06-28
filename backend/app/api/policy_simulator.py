from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.ai import simulate_policy

router = APIRouter(prefix="/api/policy-simulator", tags=["Policy Simulator"])

class PolicySimulationRequest(BaseModel):
    policy: str
    change: str

@router.post("")
async def policy_simulator(request: PolicySimulationRequest):
    try:
        return simulate_policy(request.policy, request.change)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
