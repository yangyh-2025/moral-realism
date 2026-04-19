"""
日志配置模块
统一的日志系统配置，使用 loguru 库提供结构化的日志输出。
支持控制台和文件输出，支持日志切割、压缩和保留策略。
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logging(
    log_level: str = "DEBUG",
    log_to_file: bool = True,
    log_dir: str = "logs"
):
    """
    配置日志系统

    初始化并配置 loguru 日志系统，支持控制台输出和文件输出。

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_to_file: 是否记录到文件
        log_dir: 日志文件存储目录
    """
    # 移除默认的 handler，避免重复输出
    logger.remove()

    # 确保日志目录存在
    log_path = Path(log_dir)
    if log_to_file:
        log_path.mkdir(parents=True, exist_ok=True)

    # 控制台输出配置 - 彩色格式化输出
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # 文件输出配置 - 所有日志
    if log_to_file:
        logger.add(
            log_path / "abm_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

    # 文件输出配置 - 仅错误日志
    if log_to_file:
        logger.add(
            log_path / "abm_error_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

    logger.info(f"日志系统配置完成: level={log_level}, log_to_file={log_to_file}")


def get_logger(name: str = None):
    """
    获取 logger 实例

    支持通过名称绑定获取特定的日志记录器实例。

    Args:
        name: logger 名称 (模块名)

    Returns:
        loguru logger 实例
    """
    if name:
        return logger.bind(name=name)
    return logger


# 自动配置日志（如果尚未配置）
if not logger._core.handlers:
    setup_logging(log_level="INFO")
