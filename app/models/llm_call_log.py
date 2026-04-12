"""
LLM 调用日志模型 - LLMCallLog
记录每一次大语言模型调用的全量提示词、模型响应、元数据与耗时统计。
支持分类检索与全文回溯，用于仿真调试和决策审计。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class LLMCallLog(Base):
    """
    LLM 调用日志表

    每行对应一次 LLM 调用，分类存储完整 prompt 和 response。
    与 simulation_project 级联删除（ondelete="CASCADE"）。
    """

    __tablename__ = "llm_call_log"

    call_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("simulation_project.project_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    round_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    call_type: Mapped[str] = mapped_column(
        String(40), nullable=False, index=True,
        comment="llm_interaction / llm_following / llm_goal_evaluation / llm_relationship_evolution"
    )

    phase: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True,
        comment="initiative / response, 仅决策类使用"
    )

    agent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    target_agent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    model_name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    prompt_full: Mapped[str] = mapped_column(Text, nullable=False, comment="全量提示词")

    response_full: Mapped[str] = mapped_column(Text, nullable=False, comment="全量响应")

    response_parsed: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="已结构化的 JSON 结果")

    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="success",
        comment="success / failed / timeout / retried"
    )

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<LLMCallLog(id={self.call_id}, project={self.project_id}, "
            f"type={self.call_type}, round={self.round_num})>"
        )
