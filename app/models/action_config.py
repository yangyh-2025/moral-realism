"""
ActionConfig model - 互动行为配置表
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .action_record import ActionRecord


class Base(DeclarativeBase):
    pass


class ActionCategoryEnum(str, PyEnum):
    DIPLOMATIC = "外交手段"
    ECONOMIC = "经济手段"
    MILITARY = "军事手段"
    INFORMATION = "信息手段"


class ActionConfig(Base):
    """
    互动行为配置表
    100%对齐《模型建构_改6.docx》表1的20项互动行为集，硬编码所有行为属性。
    系统初始化时自动入库，全程不可修改。
    """

    __tablename__ = "action_config"

    action_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    action_en_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    action_category: Mapped[str] = mapped_column(String(50), nullable=False)
    action_desc: Mapped[str] = mapped_column(String(1000), nullable=False)
    respect_sov: Mapped[bool] = mapped_column(Boolean, nullable=False)
    initiator_power_change: Mapped[int] = mapped_column(Integer, nullable=False)  # 绝对值≤10
    target_power_change: Mapped[int] = mapped_column(Integer, nullable=False)  # 绝对值≤10
    is_initiative: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_response: Mapped[bool] = mapped_column(Boolean, nullable=False)
    allowed_initiator_level: Mapped[str] = mapped_column(String(500), nullable=False)  # JSON array
    allowed_responder_level: Mapped[str] = mapped_column(String(500), nullable=False)  # JSON array
    forbidden_leader_type: Mapped[str] = mapped_column(String(500), nullable=False)  # JSON array

    created_at: Mapped[datetime] = mapped_column(
        type_=func.now(), nullable=False
    )  # SQLite compatibility

    # Relationships
    action_records = relationship("ActionRecord", back_populates="action_config")

    def __repr__(self) -> str:
        return f"<ActionConfig(id={self.action_id}, name={self.action_name}, category={self.action_category})>"
