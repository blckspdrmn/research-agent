from fastapi import FastAPI

from routers import llm_test, themes

app = FastAPI(title="Research Agent API")
app.include_router(themes.router)
app.include_router(llm_test.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
