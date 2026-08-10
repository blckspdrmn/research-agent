import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ThemeCreate(BaseModel):
    """テーマ作成時のリクエストボディ"""

    title: str = Field(min_length=1, max_length=100)
    description: str | None = None


class ThemeUpdate(BaseModel):
    """更新時。全項目省略可(部分更新)"""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class ThemeOut(BaseModel):
    """レスポンスとして返す完全なテーマ"""

    id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # SQLAlchemyモデル→Pydanticの変換を許可
