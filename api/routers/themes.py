from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from schemas import Theme, ThemeCreate, ThemeUpdate

router = APIRouter(prefix="/themes", tags=["themes"])

# TODO: のちほどインメモリの仮ストアからDBに置き換える
themes_db: dict[int, Theme] = {}
next_id: int = 1


@router.post("/themes", response_model=Theme, status_code=201)
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


@router.get("", response_model=list[Theme])
async def list_themes():
    return list(themes_db.values())


@router.get("/{theme_id}", response_model=Theme)
async def get_theme(theme_id: int):
    if theme_id not in themes_db:
        raise HTTPException(status_code=404, detail="Theme not found")
    return themes_db[theme_id]


@router.patch("/{theme_id}", response_model=Theme)
async def update_theme(theme_id: int, body: ThemeUpdate):
    if theme_id not in themes_db:
        raise HTTPException(status_code=404, detail="Theme not found")
    current = themes_db[theme_id]
    updated = current.model_copy(update=body.model_dump(exclude_unset=True))
    themes_db[theme_id] = updated
    return updated


@router.delete("/{theme_id}", status_code=204)
async def delete_theme(theme_id: int):
    if theme_id not in themes_db:
        raise HTTPException(status_code=404, detail="Theme not found")
    del themes_db[theme_id]
