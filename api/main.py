from fastapi import FastAPI

app = FastAPI(title="Research Agent API")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
