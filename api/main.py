import os
from fastapi import FastAPI
from routers import themes

app = FastAPI(title="Research Agent API")
app.include_router(themes.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
