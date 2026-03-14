"""
结构化日志配置

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("Warning: structlog not installed. Install with: pip install structlog")


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = False,
    service_name: str = "abm-simulation"
):
    """
    配置结构化日志

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        json_logs: 是否使用JSON格式（生产环境推荐）
        service_name: 服务名称
    """
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)

    if STRUCTLOG_AVAILABLE:
        _configure_structlog(level, log_file, json_logs, service_name)
    else:
        _configure_standard_logging(level, log_file, service_name)


def _configure_structlog(level: int, log_file: Optional[str], json_logs: bool, service_name: str):
    """配置structlog"""
    import structlog

    # 配置标准日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level
    )

    # 配置输出处理器
    if json_logs:
        # JSON格式（生产环境）
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    else:
        # 人类可读格式（开发环境）
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer()
        ]

    # 添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
            wrapper_class=structlog.stdlib.BoundLogger,
        )

        # 为文件处理器添加日志
        file_logger = logging.getLogger(service_name)
        file_logger.addHandler(file_handler)
        file_logger.setLevel(level)
    else:
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
            wrapper_class=structlog.stdlib.BoundLogger,
        )


def _configure_standard_logging(level: int, log_file: Optional[str], service_name: str):
    """配置标准Python日志（当structlog不可用时）"""
    logger = logging.getLogger(service_name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger(name: str = __name__) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)
