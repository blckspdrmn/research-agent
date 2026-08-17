import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import models
from agent import run_research
from database import get_db
from schemas import ReportOut

router = APIRouter(tags=["research"])


@router.post("/themes/{theme_id}/research", response_model=ReportOut, status_code=201)
async def execute_research(
    theme_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]
):
    theme = await db.get(models.Theme, theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Theme not found")

    research_result = await run_research(theme.title, theme.description)
    report = models.Report(
        theme_id=theme.id,
        content_md=research_result["content_md"],
        status=models.ReportStatus.COMPLETED,
        total_input_tokens=research_result["total_input_tokens"],
        total_output_tokens=research_result["total_output_tokens"],
        llm_call_count=research_result["llm_call_count"],
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report
