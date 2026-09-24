import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db
from deps import OwnedTheme
from job_queue import enqueue_research
from rate_limit import limiter
from schemas import ReportOut, ResearchJob

router = APIRouter(tags=["research"])

logger = logging.getLogger(__name__)


async def consume_research_quota(db: AsyncSession) -> bool:
    """上限未満なら受付回数を1増やしてTrueを返す。確認と加算を1文で行い、同時実行でも上限を超えない"""
    stmt = (
        insert(models.ResearchUsage)
        .values(id=1, used_count=1)
        .on_conflict_do_update(
            index_elements=[models.ResearchUsage.id],
            set_={"used_count": models.ResearchUsage.used_count + 1},
            where=models.ResearchUsage.used_count < settings.research_total_limit,
        )
        .returning(models.ResearchUsage.used_count)
    )
    return await db.scalar(stmt) is not None


@router.get("/themes/{theme_id}/reports", response_model=list[ReportOut])
async def list_reports(theme: OwnedTheme, db: Annotated[AsyncSession, Depends(get_db)]):
    stmt = (
        select(models.Report)
        .where(models.Report.theme_id == theme.id)
        .order_by(models.Report.created_at.desc())
    )
    return (await db.scalars(stmt)).all()


@router.post("/themes/{theme_id}/research", response_model=ReportOut, status_code=202)
@limiter.limit("3/minute")  # 連打対策
async def execute_research(
    request: Request,  # slowapi参照用に必要
    theme: OwnedTheme,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not await consume_research_quota(db):
        raise HTTPException(status_code=429, detail="research_quota_exceeded")

    report = models.Report(
        theme_id=theme.id,
        content_md="",
        status=models.ReportStatus.PENDING,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    try:
        await enqueue_research(
            ResearchJob(
                report_id=report.id,
                theme_title=theme.title,
                theme_description=theme.description,
            )
        )
    except Exception:
        logger.exception("enqueue failed: report_id=%s", report.id)
        await db.execute(
            update(models.Report)
            .where(
                models.Report.id == report.id,
                models.Report.status == models.ReportStatus.PENDING,
            )
            .values(
                status=models.ReportStatus.FAILED,
                error_message="リサーチの受付に失敗しました",
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=503, detail="リサーチの受付に失敗しました"
        ) from None

    return report
