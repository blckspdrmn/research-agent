from fastapi import FastAPI

from routers import research, themes

app = FastAPI(title="Research Agent API")
app.include_router(themes.router)
app.include_router(research.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
