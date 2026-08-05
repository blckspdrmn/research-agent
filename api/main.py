from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException

from schemas import Theme, ThemeCreate, ThemeUpdate

app = FastAPI(title="Research Agent API")

# TODO: のちほどインメモリの仮ストアからDBに置き換える
themes_db: dict[int, Theme] = {}
next_id: int = 1


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/themes", response_model=Theme, status_code=201)
async def create_theme(body: ThemeCreate):
    global next_id
    theme = Theme(
        id=next_id,
        title=body.title,
        description=body.description,
        created_at=datetime.now(UTC),
    )
    themes_db[theme.id] = theme
    next_id += 1
    return theme


@app.get("/themes", response_model=list[Theme])
async def list_themes():
    return list(themes_db.values())


@app.get("/themes/{theme_id}", response_model=Theme)
async def get_theme(theme_id: int):
    if theme_id not in themes_db:
        raise HTTPException(status_code=404, detail="Theme not found")
    return themes_db[theme_id]


@app.patch("/themes/{theme_id}", response_model=Theme)
async def update_theme(theme_id: int, body: ThemeUpdate):
    if theme_id not in themes_db:
        raise HTTPException(status_code=404, detail="Theme not found")
    current = themes_db[theme_id]
    updated = current.model_copy(update=body.model_dump(exclude_unset=True))
    themes_db[theme_id] = updated
    return updated


@app.delete("/themes/{theme_id}", status_code=204)
async def delete_theme(theme_id: int):
    if theme_id not in themes_db:
        raise HTTPException(status_code=404, detail="Theme not found")
    del themes_db[theme_id]
