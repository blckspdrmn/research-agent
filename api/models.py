import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ReportStatus(enum.StrEnum):
    """レポート生成の実行状態。pending → running → completed / failed"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuidv7()")
    )
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    themes: Mapped[list["Theme"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuidv7()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="themes")
    reports: Mapped[list["Report"]] = relationship(
        back_populates="theme", cascade="all, delete-orphan", passive_deletes=True
    )


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuidv7()")
    )
    theme_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("themes.id", ondelete="CASCADE"), index=True
    )
    content_md: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ReportStatus] = mapped_column(
        Enum(
            ReportStatus,
            native_enum=False,
            length=20,
            create_constraint=True,
            name="ck_reports_status",
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        default=ReportStatus.PENDING,
        index=True,
    )
    error_message: Mapped[str | None] = mapped_column(String(500), default=None)
    total_input_tokens: Mapped[int | None] = mapped_column(default=None)
    total_output_tokens: Mapped[int | None] = mapped_column(default=None)
    llm_call_count: Mapped[int | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    theme: Mapped["Theme"] = relationship(back_populates="reports")
