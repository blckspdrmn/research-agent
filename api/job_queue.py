from azure.storage.queue.aio import QueueClient

from config import settings
from schemas import ResearchJob

QUEUE_NAME = "research-jobs"


async def enqueue_research(job: ResearchJob) -> None:
    """リサーチ依頼をQueueへ送る。APIプロセスが終了しても依頼は残る"""
    async with QueueClient.from_connection_string(
        settings.azure_storage_connection_string, queue_name=QUEUE_NAME
    ) as client:
        await client.send_message(job.model_dump_json())
