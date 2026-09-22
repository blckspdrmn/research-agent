import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models import ReportStatus


class ThemeCreate(BaseModel):
    """テーマ作成時のリクエストボディ"""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class ThemeUpdate(BaseModel):
    """更新時。全項目省略可(部分更新)"""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    # nullで明示的に更新したときだけバリデーションで弾く
    @field_validator("title")
    @classmethod
    def reject_null_title(cls, value: str | None) -> str:
        """省略は許すが、明示的なnullは拒否する（titleはNOT NULL）"""
        if value is None:
            raise ValueError("title cannot be null")
        return value


class ThemeOut(BaseModel):
    """レスポンスとして返す完全なテーマ"""

    id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # SQLAlchemyモデル→Pydanticの変換を許可


class ReportOut(BaseModel):
    id: uuid.UUID
    theme_id: uuid.UUID
    content_md: str
    status: ReportStatus
    error_message: str | None = None
    created_at: datetime
    total_input_tokens: int | None = None
    total_output_tokens: int | None = None
    llm_call_count: int | None = None

    model_config = {"from_attributes": True}


class ResearchJob(BaseModel):
    report_id: uuid.UUID
    theme_title: str
    theme_description: str | None = None
