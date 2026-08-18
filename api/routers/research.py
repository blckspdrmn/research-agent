import asyncio
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from agent import run_research
from database import SessionLocal, get_db
from schemas import ReportOut

router = APIRouter(tags=["research"])

logger = logging.getLogger(__name__)

RESEARCH_TIMEOUT_SECONDS = 300


async def _run_and_save(
    report_id: uuid.UUID, title: str, description: str | None
) -> None:
    """リサーチ処理をバックグラウンドタスクとして実行"""
    async with SessionLocal() as db:
        report = await db.get(models.Report, report_id)
        if report is None:
            logger.error("report not found: report_id=%s", report_id)
            return
        report.status = models.ReportStatus.RUNNING
        await db.commit()
        try:
            async with asyncio.timeout(RESEARCH_TIMEOUT_SECONDS):
                research_result = await run_research(title, description)
            report.content_md = research_result["content_md"]
            report.status = models.ReportStatus.COMPLETED
            report.total_input_tokens = research_result["total_input_tokens"]
            report.total_output_tokens = research_result["total_output_tokens"]
            report.llm_call_count = research_result["llm_call_count"]
            logger.info("research completed: report_id=%s", report_id)
        except TimeoutError:
            report.status = models.ReportStatus.FAILED
            report.error_message = "リサーチが制限時間内に完了しませんでした"
            logger.warning("research timed out: report_id=%s", report_id)
        except Exception:
            report.status = models.ReportStatus.FAILED
            report.error_message = "リサーチ中にエラーが発生しました"
            logger.exception("research failed: report_id=%s", report_id)
        try:
            await db.commit()
        except Exception:  # research中にthemeが消されたことによりreportも消えた時など
            logger.exception("commit failed: report_id=%s", report_id)


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
    background_tasks: BackgroundTasks,
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

    background_tasks.add_task(
        _run_and_save, report.id, theme.title, theme.description
    )  # バックグラウンドタスクを予約
    return report
