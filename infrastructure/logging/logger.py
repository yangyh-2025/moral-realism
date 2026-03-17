"""
增强日志记录引擎 - 记录所有行动、发言、决策理由和数据统计

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class LogType(str, Enum):
    """日志类型枚举"""
    DECISION = "decision"           # 决策类日志
    ACTION = "action"               # 行动类日志
    SPEECH = "speech"               # 发言类日志
    JUDGMENT = "judgment"           # 判断类日志
    METRIC = "metric"               # 数据统计类日志
    EVENT = "event"                 # 事件触发日志
    ERROR = "error"                 # 错误日志
    DEBUG = "debug"                 # 调试日志

@dataclass
class LogEntry:
    """日志条目 - 支持理由保密性的日志系统"""
    log_id: str
    log_type: LogType
    simulation_id: str
    round: int
    agent_id: Optional[str]  # 可能为None（系统级日志）
    timestamp: datetime
    content: str              # 日志内容描述
    details: Dict             # 详细数据
    reasoning: Optional[str] = None  # 决策/判断/行动的理由（仅在日志中保存，不对外共享）
    is_reasoning_private: bool = True  # 理由是否为私有，默认是

    def to_dict(self, include_reasoning: bool = False) -> Dict:
        """转换为字典，支持过滤理由"""
        result = {
            "log_id": self.log_id,
            "log_type": self.log_type,
            "simulation_id": self.simulation_id,
            "round": self.round,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "details": self.details
        }

        if include_reasoning and self.reasoning:
            result["reasoning"] = self.reasoning

        return result

class EnhancedLogger:
    """
    增强日志记录器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 配置Python标准日志
        self._setup_standard_logger()

        # 日志条目存储
        self._log_entries: List[LogEntry] = []

    def _setup_standard_logger(self):
        """设置标准日志记录器"""
        log_file = self.log_dir / "simulation.log"

        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        # 配置根日志器
        self.logger = logging.getLogger("ABM_Simulation")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def log_decision(
        self,
        simulation_id: str,
        round: int,
        agent_id: str,
        decision_type: str,
        decision_content: str,
        reasoning: Dict,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        记录决策日志（包含完整理由）

        Args:
            simulation_id: 仿真ID
            round: 轮次
            agent_id: 智能体ID
            decision_type: 决策类型
            decision_content: 决策内容
            reasoning: 决策理由（包含局势分析、战略考量、预期结果、替代方案）
            metadata: 附加元数据

        Returns:
            日志ID
        """
        log_id = f"log_decision_{datetime.now().timestamp()}"

        # 创建日志条目
        log_entry = LogEntry(
            log_id=log_id,
            log_type=LogType.DECISION,
            simulation_id=simulation_id,
            round=round,
            agent_id=agent_id,
            timestamp=datetime.now(),
            content=f"[决策] {agent_id}做出了{decision_type}决策: {decision_content}",
            details={
                "decision_type": decision_type,
                "decision_content": decision_content,
                "reasoning": reasoning,
                "metadata": metadata or {}
            },
            reasoning=json.dumps(reasoning, ensure_ascii=False)
        )

        self._log_entries.append(log_entry)

        # 记录到标准日志
        self.logger.info(
            f"决策记录: {decision_type}",
            extra={
                "simulation_id": simulation_id,
                "round": round,
                "agent_id": agent_id
            }
        )

        return log_id
