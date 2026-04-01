from fastapi import FastAPI
from routers.tasks import router as tasks_router

app = FastAPI(
    title="Task Approval Workflow API",
    description="Handles approval workflows for DataAccess, ResourceProvision, and ConfigChange tasks.",
    version="1.0.0",
)

app.include_router(tasks_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
