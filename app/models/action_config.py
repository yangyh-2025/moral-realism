"""
ActionConfig model - 互动行为配置表
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .action_record import ActionRecord


class ActionCategoryEnum(str, PyEnum):
    DIPLOMATIC = "外交手段"
    ECONOMIC = "经济手段"
    MILITARY = "军事手段"
    INFORMATION = "信息手段"


class ActionConfig(Base):
    """
    互动行为配置表
    100%对齐《模型建构_改6.docx》表1的20项互动行为集，只保留学术文档中定义的字段。
    系统初始化时自动入库，全程不可修改。
    """

    __tablename__ = "action_config"

    action_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    action_en_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    action_category: Mapped[str] = mapped_column(String(50), nullable=False)
    action_desc: Mapped[str] = mapped_column(String(1000), nullable=False)
    respect_sov: Mapped[bool] = mapped_column(Boolean, nullable=False)
    initiator_power_change: Mapped[int] = mapped_column(Integer, nullable=False)
    target_power_change: Mapped[int] = mapped_column(Integer, nullable=False)
    is_initiative: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_response: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relationships
    action_records = relationship("ActionRecord", back_populates="action_config")

    def __repr__(self) -> str:
        return f"<ActionConfig(id={self.action_id}, name={self.action_name}, category={self.action_category})>"
