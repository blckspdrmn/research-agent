import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db
from schemas import ThemeCreate, ThemeOut, ThemeUpdate

router = APIRouter(prefix="/themes", tags=["themes"])

# TODO: のちほど認証ユーザーに置き換える
# （暫定：直接DBにInsertしたダミーユーザーのIDを用いている）
DUMMY_USER_ID = settings.dummy_user_id


async def _get_owned_theme(db: AsyncSession, theme_id: uuid.UUID) -> models.Theme:
    """無い場合も他人のものも同じ404にする（データの存在を知らせないため）"""
    theme = await db.get(models.Theme, theme_id)
    if theme is None or theme.user_id != DUMMY_USER_ID:
        raise HTTPException(status_code=404, detail="Theme not found")
    return theme


@router.post("", response_model=ThemeOut, status_code=201)
async def create_theme(body: ThemeCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    theme = models.Theme(user_id=DUMMY_USER_ID, **body.model_dump())
    db.add(theme)
    await db.commit()
    await db.refresh(theme)
    return theme


@router.get("", response_model=list[ThemeOut])
async def list_themes(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = (
        select(models.Theme)
        .where(models.Theme.user_id == DUMMY_USER_ID)
        .order_by(models.Theme.created_at.desc(), models.Theme.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return (await db.scalars(stmt)).all()


@router.get("/{theme_id}", response_model=ThemeOut)
async def get_theme(theme_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    return await _get_owned_theme(db, theme_id)


@router.patch("/{theme_id}", response_model=ThemeOut)
async def update_theme(
    theme_id: uuid.UUID,
    body: ThemeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    theme = await _get_owned_theme(db, theme_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(theme, field, value)
    await db.commit()
    await db.refresh(theme)
    return theme


@router.delete("/{theme_id}", status_code=204)
async def delete_theme(
    theme_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    theme = await _get_owned_theme(db, theme_id)
    await db.delete(theme)
    await db.commit()
