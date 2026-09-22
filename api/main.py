from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from rate_limit import limiter
from routers import research, themes

app = FastAPI(title="Research Agent API")

app.state.limiter = limiter
# レートリミット超えると429
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(themes.router)
app.include_router(research.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
