from fastapi import APIRouter
from pydantic import BaseModel

from llm import get_chat_model

router = APIRouter(prefix="/llm-test", tags=["llm-test"])


class Ask(BaseModel):
    question: str


@router.post("")
async def ask(body: Ask):
    model = get_chat_model()
    response = await model.ainvoke(body.question)
    return response.model_dump()
