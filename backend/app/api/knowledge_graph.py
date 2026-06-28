from fastapi import APIRouter
from app.core.ai import get_knowledge_graph

router = APIRouter(prefix="/api/knowledge-graph", tags=["Knowledge Graph"])

@router.get("")
async def knowledge_graph():
    return get_knowledge_graph()
