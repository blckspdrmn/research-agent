import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, or_, update

import models
from agent_graph import run_research
from database import SessionLocal
from schemas import ResearchJob

logger = logging.getLogger(__name__)

RESEARCH_TIMEOUT_SECONDS = 300
LEASE_SECONDS = 700  # Queueのvisibility_timeoutと揃える
MAX_ATTEMPTS = 3


async def process_job(job: ResearchJob) -> bool:
    """1件のリサーチリクエストを処理する。

    戻り値は「結果が確定したか」であって成功/失敗ではない。
    - True  : completed / failed のいずれかをDBへ保存できた。Queueから削除してよい
    - False : リクエスト重複が起きてしまったなどで、別のworkerが処理中の場合等。

    """
    async with SessionLocal() as db:
        now = datetime.now(UTC)
        claim = (
            update(models.Report)
            .where(
                models.Report.id == job.report_id,
                models.Report.attempt_count < MAX_ATTEMPTS,
                or_(
                    models.Report.status == models.ReportStatus.PENDING,
                    and_(
                        models.Report.status == models.ReportStatus.RUNNING,
                        models.Report.lease_until < now,  # lease切れは再取得可能
                    ),
                ),
            )
            .values(
                status=models.ReportStatus.RUNNING,
                attempt_count=models.Report.attempt_count + 1,
                lease_until=now + timedelta(seconds=LEASE_SECONDS),
            )
            .returning(models.Report.attempt_count)
        )  # SQLを組み立て
        attempt = await db.scalar(claim)  # SQLを実行して更新されたattempt_countを取得
        await db.commit()

        if attempt is None:  # whereの条件に合わなかったとき
            return await _handle_unclaimable(db, job)

    # --- リサーチ本体 ---
    # 数分かかりうるのでDBセッションを閉じてから実行する（接続を占有しない）
    content_md = ""
    error_message: str | None = None
    tokens: dict[str, int] = {}
    try:
        async with asyncio.timeout(RESEARCH_TIMEOUT_SECONDS):
            result = await run_research(job.theme_title, job.theme_description)
        content_md = result["content_md"]
        tokens = {
            "total_input_tokens": result["total_input_tokens"],
            "total_output_tokens": result["total_output_tokens"],
            "llm_call_count": result["llm_call_count"],
        }
        status = models.ReportStatus.COMPLETED
        logger.info("research completed: report_id=%s", job.report_id)
    except TimeoutError:
        status = models.ReportStatus.FAILED
        error_message = "リサーチが制限時間内に完了しませんでした"
        logger.warning("research timed out: report_id=%s", job.report_id)
    except Exception:
        status = models.ReportStatus.FAILED
        error_message = "リサーチ中にエラーが発生しました"
        logger.exception("research failed: report_id=%s", job.report_id)

    # --- 結果の保存 ---
    async with SessionLocal() as db:
        save = (
            update(models.Report)
            .where(
                models.Report.id == job.report_id,
                models.Report.status == models.ReportStatus.RUNNING,
                # lease切れで別のworkerが権利を取り直している場合に
                # 元のworkerが結果を書き込まないように
                models.Report.attempt_count == attempt,
            )
            .values(
                status=status,
                content_md=content_md,
                error_message=error_message,
                lease_until=None,
                **tokens,
            )
            .returning(models.Report.id)
        )
        saved = await db.scalar(save)
        await db.commit()

    if saved is None:
        logger.info("stale result discarded: report_id=%s", job.report_id)
    return True


async def _handle_unclaimable(db, job: ResearchJob) -> bool:
    """claimできなかったときに、Queueから削除してよいかを判定する"""
    report = await db.get(models.Report, job.report_id)

    if report is None:
        # テーマごと削除された。処理する対象がない
        logger.info("report not found, acking: report_id=%s", job.report_id)
        return True

    if report.status in (
        models.ReportStatus.COMPLETED,
        models.ReportStatus.FAILED,
    ):
        # 結果確定済み。再実行しない
        return True

    if (
        report.status == models.ReportStatus.RUNNING
        and report.lease_until is not None
        and report.lease_until > datetime.now(UTC)
    ):
        # 別の実行が進行中なので後ほどまた確認しにくる
        logger.info("already running, deferring: report_id=%s", job.report_id)
        return False

    if report.attempt_count >= MAX_ATTEMPTS:
        # 3回使い切った。failedで確定させて打ち切る（LLMの再課金を止める）
        report.status = models.ReportStatus.FAILED
        report.error_message = "リサーチが規定回数内に完了しませんでした"
        report.lease_until = None
        await db.commit()
        logger.warning("max attempts reached: report_id=%s", job.report_id)
        return True

    # lease切れ、または移行期のlease未設定。次の受信でclaimし直せるので後回しにする
    logger.info("not claimable yet, deferring: report_id=%s", job.report_id)
    return False
