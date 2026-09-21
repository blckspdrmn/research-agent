import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from job_queue import enqueue_research
from schemas import ReportOut, ResearchJob

router = APIRouter(tags=["research"])

logger = logging.getLogger(__name__)


@router.get("/themes/{theme_id}/reports", response_model=list[ReportOut])
async def list_reports(
    theme_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    theme = await db.get(models.Theme, theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Theme not found")
    stmt = (
        select(models.Report)
        .where(models.Report.theme_id == theme_id)
        .order_by(models.Report.created_at.desc())
    )
    return (await db.scalars(stmt)).all()


@router.post("/themes/{theme_id}/research", response_model=ReportOut, status_code=202)
async def execute_research(
    theme_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    theme = await db.get(models.Theme, theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Theme not found")

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
