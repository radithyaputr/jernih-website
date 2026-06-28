from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import dataclasses
from app.core.ai import analyze_situation, CasualResponse

router = APIRouter(prefix="/api/copilot", tags=["AI Civic Copilot"])

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@router.post("/chat")
def chat(request: ChatRequest):
    try:
        result = analyze_situation(request.message)

        # Casual response (greetings, simple chat)
        if isinstance(result, CasualResponse):
            return {
                "session_id": result.session_id,
                "type": "casual",
                "message": result.message,
            }

        # Analysis response (full civic analysis)
        result_dict = dataclasses.asdict(result)
        return {
            "session_id": result_dict["session_id"],
            "type": "analysis",
            "response": {
                "summary": result_dict["summary"],
                "analysis": result_dict["analysis"],
                "relevant_programs": result_dict["relevant_programs"],
                "required_documents": result_dict["required_documents"],
                "risk_factors": result_dict["risk_factors"],
                "timeline": result_dict["timeline"],
                "action_plan": result_dict["action_plan"],
                "success_probability": result_dict["success_probability"],
                "trust_score": result_dict["trust_score"],
                "sources": result_dict["sources"],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

