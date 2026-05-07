"""
互动行为配置模型 - ActionConfig（CINC版）
定义仿真系统中智能体可以执行的20种标准互动行为。
这些行为来自学术文档，分为外交、经济、军事、信息四大类，系统初始化时自动入库，全程不可修改。

CINC更新：
- 新增 primary_indicator 字段，标识行为主要影响的CINC底层指标
- 新增 secondary_indicator 字段，标识行为次要影响的CINC底层指标
- 保留 initiator_power_change/target_power_change 作为相对强度（-1到+1）
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .action_record import ActionRecord


class ActionCategoryEnum(str, PyEnum):
    """行为类型枚举"""
    DIPLOMATIC = "外交手段"
    ECONOMIC = "经济手段"
    MILITARY = "军事手段"
    INFORMATION = "信息手段"


class ActionConfig(Base):
    """
    互动行为配置表（CINC版）

    属性说明：
    - 行为名称：中文名称和英文名称
    - 行为类型：外交、经济、军事或信息手段
    - 行为描述：详细说明行为的内容和影响
    - 主权尊重：是否尊重目标方主权
    - 国力变化：行为对发起方和目标方的国力影响相对强度（-1到+1）
    - 行为属性：是否可作为发起行为、是否可作为响应行为
    - CINC指标映射：主要影响的底层指标、次要影响的底层指标
    """

    __tablename__ = "action_config"

    action_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    action_en_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    action_category: Mapped[str] = mapped_column(String(50), nullable=False)
    action_desc: Mapped[str] = mapped_column(String(1000), nullable=False)
    respect_sov: Mapped[bool] = mapped_column(Boolean, nullable=False)
    initiator_power_change: Mapped[float] = mapped_column(Float, nullable=False)
    target_power_change: Mapped[float] = mapped_column(Float, nullable=False)
    is_initiative: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_response: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # CINC指标映射（可选，为空时使用类别默认权重）
    primary_indicator: Mapped[str] = mapped_column(String(20), nullable=False, default="pec")
    secondary_indicator: Mapped[str] = mapped_column(String(20), nullable=False, default="irst")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relationships
    action_records = relationship("ActionRecord", back_populates="action_config")

    def __repr__(self) -> str:
        return f"<ActionConfig(id={self.action_id}, name={self.action_name}, category={self.action_category})>"
