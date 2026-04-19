"""
系统配置模型 - SystemConfig
存储系统的全局配置信息，包括LLM模型配置、API密钥、仿真参数、日志设置等。
这些配置项影响系统的运行行为和性能。
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class SystemConfig(Base):
    """
    系统配置表

    存储系统的全局配置信息，核心配置项包括：
    - LLM模型配置：模型名称、API密钥、API基础URL
    - 调用参数：超时时间、最大重试次数
    - 仿真参数：并发数
    - 日志设置：日志级别
    - 场景设置：默认场景ID

    这些配置项影响系统的运行行为和性能。
    """

    __tablename__ = "system_config"

    config_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    config_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    config_value: Mapped[str] = mapped_column(String(5000), nullable=False)
    config_desc: Mapped[str] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )  # SQLite compatibility
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )  # SQLite compatibility

    def __repr__(self) -> str:
        return f"<SystemConfig(key={self.config_key}, value={self.config_value})>"
