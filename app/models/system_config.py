"""
SystemConfig model - 系统配置表
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class SystemConfig(Base):
    """
    系统配置表
    移除用户相关配置，核心配置项：LLM模型名称、API密钥、调用超时时间、最大重试次数、仿真并发数、日志级别、默认场景ID等。
   。
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
