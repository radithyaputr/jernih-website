"""JERNIH OS API — Main Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import copilot, knowledge_graph, analytics, action_plan, hoax_checker, policy_simulator

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="JERNIH OS - AI Civic Operating System API",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.app_version, "app": settings.app_name}

# Include routers
app.include_router(copilot.router)
app.include_router(knowledge_graph.router)
app.include_router(analytics.router)
app.include_router(action_plan.router)
app.include_router(hoax_checker.router)
app.include_router(policy_simulator.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
