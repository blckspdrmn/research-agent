from langchain_openai import ChatOpenAI

from config import settings


def get_chat_model(
    temperature: float = 0.0, max_completion_tokens: int = 1000
) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.azure_openai_chat_deployment,
        base_url=settings.azure_openai_base_url,
        api_key=settings.azure_openai_api_key,
        temperature=temperature,  # TODO: レポート出力機能実装してから調整する
        max_completion_tokens=max_completion_tokens,  # 同上
        timeout=60.0,  # 1回の呼び出しの上限(秒)
        max_retries=2,  # 自動リトライ回数(指数バックオフ)
    )
