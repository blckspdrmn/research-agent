from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from deps import CurrentUser, OwnedTheme
from schemas import ThemeCreate, ThemeOut, ThemeUpdate

router = APIRouter(prefix="/themes", tags=["themes"])


@router.post("", response_model=ThemeOut, status_code=201)
async def create_theme(
    body: ThemeCreate,
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    theme = models.Theme(user_id=user.id, **body.model_dump())
    db.add(theme)
    await db.commit()
    await db.refresh(theme)
    return theme


@router.get("", response_model=list[ThemeOut])
async def list_themes(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = (
        select(models.Theme)
        .where(models.Theme.user_id == user.id)
        .order_by(models.Theme.created_at.desc(), models.Theme.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return (await db.scalars(stmt)).all()


@router.get("/{theme_id}", response_model=ThemeOut)
async def get_theme(theme: OwnedTheme):
    return theme


@router.patch("/{theme_id}", response_model=ThemeOut)
async def update_theme(
    theme: OwnedTheme,
    body: ThemeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(theme, field, value)
    await db.commit()
    await db.refresh(theme)
    return theme


@router.delete("/{theme_id}", status_code=204)
async def delete_theme(theme: OwnedTheme, db: Annotated[AsyncSession, Depends(get_db)]):
    await db.delete(theme)
    await db.commit()
