import asyncio
import logging
import os

from azure.storage.queue.aio import QueueClient
from pydantic import ValidationError

from config import settings
from research_runner import process_job
from schemas import ResearchJob

logger = logging.getLogger(__name__)


async def process_once(client: QueueClient, poison: QueueClient) -> None:
    async for msg in client.receive_messages(max_messages=1, visibility_timeout=700):
        try:
            job = ResearchJob.model_validate_json(msg.content)
        except ValidationError:
            # 不正メッセージは調査せず隔離。隔離保存に失敗したら削除しない。
            await poison.send_message(msg.content)
            await client.delete_message(msg)
            logger.error("Invalid job quarantined")
            return
        if await process_job(job):
            await client.delete_message(msg)
        else:
            await client.update_message(msg, visibility_timeout=60)


async def main() -> None:
    client = QueueClient.from_connection_string(
        settings.azure_storage_connection_string, queue_name="research-jobs"
    )
    poison = QueueClient.from_connection_string(
        settings.azure_storage_connection_string, queue_name="research-jobs-poison"
    )
    polling = os.getenv("WORKER_POLL") == "1"  # 本番ではFalse
    async with client, poison:
        while True:
            try:
                async with asyncio.timeout(600):
                    await process_once(client, poison)
            except Exception:
                logger.exception("Job execution failed")
                if not polling:
                    raise  # 本番では失敗として記録する。Queueは後で再可視化される
            if not polling:  # 本番ではここでループを抜ける（1件処理して終了）
                return
            await asyncio.sleep(5)  # ローカルでは5秒ごとにpolling


# `python -m worker`コマンドで呼ばれる
# ローカル：Composeのworkerサービス 本番：ACA Jobs
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Azure SDKのログはWarning以上のみに
    logging.getLogger("azure").setLevel(logging.WARNING)
    asyncio.run(main())
