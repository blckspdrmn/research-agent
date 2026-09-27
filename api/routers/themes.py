from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from deps import CurrentUser, OwnedTheme
from schemas import ThemeCreate, ThemeListItemOut, ThemeOut, ThemeUpdate

router = APIRouter(prefix="/themes", tags=["themes"])

# これより古いpending/runningは止まったとみなし、実行中として扱わない
RESEARCH_STALE_AFTER = timedelta(minutes=30)


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


@router.get("", response_model=list[ThemeListItemOut])
async def list_themes(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    latest_report_status = (
        select(models.Report.status)
        .where(models.Report.theme_id == models.Theme.id)
        .order_by(models.Report.created_at.desc(), models.Report.id.desc())
        .limit(1)
        .scalar_subquery()
    )
    is_researching = exists().where(
        models.Report.theme_id == models.Theme.id,
        models.Report.status.in_(
            [models.ReportStatus.PENDING, models.ReportStatus.RUNNING]
        ),
        models.Report.created_at > func.now() - RESEARCH_STALE_AFTER,
    )
    stmt = (
        select(models.Theme, latest_report_status, is_researching)
        .where(models.Theme.user_id == user.id)
        .order_by(models.Theme.created_at.desc(), models.Theme.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = await db.execute(stmt)
    return [
        ThemeListItemOut(
            **ThemeOut.model_validate(theme).model_dump(),
            latest_report_status=status,
            is_researching=researching,
        )
        for theme, status, researching in rows
    ]


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
