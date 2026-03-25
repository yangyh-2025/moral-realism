"""
增强日志记录引擎 - 记录所有行动、发言、决策理由和数据统计

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import logging
from logging import FileHandler
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
class DecisionReasoning:
    """决策理由 - 详细记录智能体决策的完整推理过程"""
    decision_id: str
    agent_id: str
    round: int
    situation_analysis: str           # 局势分析
    strategic_consideration: str      # 战略考量
    expected_outcome: str            # 预期结果
    alternatives: List[str]            # 替代方案
    full_reasoning: str               # 完整决策理由

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "decision_id": self.decision_id,
            "agent_id": self.agent_id,
            "round": self.round,
            "situation_analysis": self.situation_analysis,
            "strategic_consideration": self.strategic_consideration,
            "expected_outcome": self.expected_outcome,
            "alternatives": self.alternatives,
            "full_reasoning": self.full_reasoning
        }

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

    def __init__(self, log_dir: str = "logs", simulation_id: Optional[str] = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.simulation_id = simulation_id

        # 创建仿真特定的文件夹
        if self.simulation_id:
            self.sim_log_dir = self.log_dir / self.simulation_id
            self.sim_log_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.sim_log_dir = self.log_dir

        # 配置Python标准日志
        self._setup_standard_logger()

        # 日志条目存储
        self._log_entries: List[LogEntry] = []
        # LLM请求响应存储
        self._llm_logs: List[Dict] = []
        # 指标存储
        self._metrics_logs: List[Dict] = []

        # JSON日志文件路径 - 存储在仿真特定文件夹中
        if self.simulation_id:
            self.json_log_file = self.sim_log_dir / "simulation.json"
        else:
            self.json_log_file = self.log_dir / "simulation.json"

    def _setup_standard_logger(self):
        """设置标准日志记录器"""
        log_file = self.log_dir / "simulation.log"

        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 文件处理器
        file_handler = FileHandler(log_file, encoding='utf-8')
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

        # 保存到JSON文件
        self._save_to_json()

        return log_id

    def log_action(
        self,
        simulation_id: str,
        round: int,
        agent_id: str,
        action_type: str,
        action_content: str,
        outcome: str,
        reasoning: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        记录行动日志

        Args:
            simulation_id: 仿真ID
            round: 轮次
            agent_id: 智能体ID
            action_type: 行动类型
            action_content: 行动内容
            outcome: 行动结果
            reasoning: 行动理由
            metadata: 附加元数据

        Returns:
            日志ID
        """
        log_id = f"log_action_{datetime.now().timestamp()}"
        log_entry = LogEntry(
            log_id=log_id,
            log_type=LogType.ACTION,
            simulation_id=simulation_id,
            round=round,
            agent_id=agent_id,
            timestamp=datetime.now(),
            content=f"[行动] {agent_id}执行了{action_type}: {action_content}, 结果: {outcome}",
            details={
                "action_type": action_type,
                "action_content": action_content,
                "outcome": outcome,
                "metadata": metadata or {}
            },
            reasoning=reasoning
        )
        self._log_entries.append(log_entry)
        self.logger.info(
            f"行动记录: {action_type}",
            extra={
                "simulation_id": simulation_id,
                "round": round,
                "agent_id": agent_id,
                "outcome": outcome
            }
        )
        # 保存到JSON文件
        self._save_to_json()
        return log_id

    def log_speech(
        self,
        simulation_id: str,
        round: int,
        agent_id: str,
        speech_type: str,
        content: str,
        target_id: Optional[str] = None,
        audience: Optional[str] = None,
        reception: Optional[str] = None,
        reasoning: Optional[str] = None
    ) -> str:
        """
        记录发言日志

        Args:
            simulation_id: 仿真ID
            round: 轮次
            agent_id: 智能体ID
            speech_type: 发言类型
            content: 发言内容
            target_id: 目标ID
            audience: 听众
            reception: 接受度
            reasoning: 发言理由

        Returns:
            日志ID
        """
        log_id = f"log_speech_{datetime.now().timestamp()}"
        log_entry = LogEntry(
            log_id=log_id,
            log_type=LogType.SPEECH,
            simulation_id=simulation_id,
            round=round,
            agent_id=agent_id,
            timestamp=datetime.now(),
            content=f"[发言] {agent_id}发表{speech_type}: {content[:100]}...",
            details={
                "speech_type": speech_type,
                "content": content,
                "target_id": target_id,
                "audience": audience,
                "reception": reception
            },
            reasoning=reasoning
        )
        self._log_entries.append(log_entry)
        self.logger.info(
            f"发言记录: {speech_type}",
            extra={
                "simulation_id": simulation_id,
                "round": round,
                "agent_id": agent_id
            }
        )
        # 保存到JSON文件
        self._save_to_json()
        return log_id

    def log_event(
        self,
        simulation_id: str,
        round: int,
        event_type: str,
        description: str,
        event_data: Optional[Dict] = None
    ) -> str:
        """
        记录事件日志

        Args:
            simulation_id: 仿真ID
            round: 轮次
            event_type: 事件类型
            description: 事件描述
            event_data: 事件数据

        Returns:
            日志ID
        """
        log_id = f"log_event_{datetime.now().timestamp()}"
        log_entry = LogEntry(
            log_id=log_id,
            log_type=LogType.EVENT,
            simulation_id=simulation_id,
            round=round,
            agent_id=None,
            timestamp=datetime.now(),
            content=f"[事件] {description}",
            details={
                "event_type": event_type,
                "event_data": event_data or {}
            }
        )
        self._log_entries.append(log_entry)
        self.logger.info(
            f"事件记录: {event_type}",
            extra={
                "simulation_id": simulation_id,
                "round": round
            }
        )
        # 保存到JSON文件
        self._save_to_json()
        return log_id

    def log_error(
        self,
        simulation_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None
    ) -> None:
        """
        记录错误日志

        Args:
            simulation_id: 仿真ID
            error_type: 错误类型
            error_message: 错误消息
            context: 错误上下文
        """
        log_entry = LogEntry(
            log_id=f"log_error_{datetime.now().timestamp()}",
            log_type=LogType.ERROR,
            simulation_id=simulation_id,
            round=0,
            agent_id=None,
            timestamp=datetime.now(),
            content=f"[错误] {error_type}: {error_message}",
            details={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            }
        )
        self._log_entries.append(log_entry)
        self.logger.error(
            error_message,
            extra={
                "simulation_id": simulation_id,
                "error_type": error_type
            }
        )
        # 保存到JSON文件
        self._save_to_json()

    def log_info(
        self,
        simulation_id: str,
        message: str,
        round: Optional[int] = None,
        agent_id: Optional[str] = None
    ) -> None:
        """
        记录信息日志

        Args:
            simulation_id: 仿真ID
            message: 消息
            round: 轮次
            agent_id: 智能体ID
        """
        log_entry = LogEntry(
            log_id=f"log_info_{datetime.now().timestamp()}",
            log_type=LogType.DEBUG,
            simulation_id=simulation_id,
            round=round or 0,
            agent_id=agent_id,
            timestamp=datetime.now(),
            content=message,
            details={}
        )
        self._log_entries.append(log_entry)
        self.logger.info(
            message,
            extra={
                "simulation_id": simulation_id,
                "round": round,
                "agent_id": agent_id
            }
        )
        # 保存到JSON文件
        self._save_to_json()

    def get_logs(
        self,
        simulation_id: Optional[str] = None,
        log_type: Optional[LogType] = None,
        agent_id: Optional[str] = None,
        round: Optional[int] = None,
        include_reasoning: bool = False,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取日志

        Args:
            simulation_id: 按仿真ID筛选
            log_type: 按日志类型筛选
            agent_id: 按智能体ID筛选
            round: 按轮次筛选
            include_reasoning: 是否包含理由
            limit: 返回数量限制

        Returns:
            日志列表
        """
        filtered_logs = self._log_entries

        if simulation_id:
            filtered_logs = [log for log in filtered_logs if log.simulation_id == simulation_id]

        if log_type:
            filtered_logs = [log for log in filtered_logs if log.log_type == log_type]

        if agent_id:
            filtered_logs = [log for log in filtered_logs if log.agent_id == agent_id]

        if round is not None:
            filtered_logs = [log for log in filtered_logs if log.round == round]

        # 按时间倒序排序
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)

        # 转换为字典
        result = [log.to_dict(include_reasoning=include_reasoning) for log in filtered_logs[:limit]]

        return result

    def clear_logs(self, simulation_id: Optional[str] = None) -> None:
        """
        清空日志

        Args:
            simulation_id: 指定仿真ID的日志，None则清空全部
        """
        if simulation_id:
            self._log_entries = [log for log in self._log_entries if log.simulation_id != simulation_id]
        else:
            self._log_entries.clear()

    def log_llm_request(
        self,
        simulation_id: str,
        agent_id: str,
        agent_name: str,
        round: Optional[int] = None,
        prompt: str = "",
        functions: Optional[List[Dict]] = None,
        model: str = "",
        system_message: Optional[str] = None
    ) -> None:
        """
        记录LLM请求

        Args:
            simulation_id: 仿真ID
            agent_id: 智能体ID
            agent_name: 智能体名称
            round: 当前轮次
            prompt: 提示词
            functions: 可用函数列表
            model: 模型名称
            system_message: system消息内容
        """
        log_entry = {
            "type": "llm_request",
            "timestamp": datetime.now().isoformat(),
            "simulation_id": simulation_id,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "round": round,
            "system_message": system_message,
            "prompt_preview": prompt[:500] if prompt else "",
            "prompt": prompt,
            "functions": [f.get('name', '') for f in functions] if functions else [],
            "model": model
        }
        self._llm_logs.append(log_entry)
        self._save_to_json()

    def log_llm_response(
        self,
        simulation_id: str,
        agent_id: str,
        agent_name: str,
        round: Optional[int] = None,
        function_name: Optional[str] = None,
        function_args: Optional[Dict] = None,
        content: str = "",
        usage: Optional[Dict] = None,
        status_code: Optional[int] = None
    ) -> None:
        """
        记录LLM响应

        Args:
            simulation_id: 仿真ID
            agent_id: 智能体ID
            agent_name: 智能体名称
            round: 当前轮次
            function_name: 决策函数名称
            function_args: 决策函数参数
            content: 响应内容
            usage: Token使用情况
            status_code: HTTP状态码
        """
        log_entry = {
            "type": "llm_response",
            "timestamp": datetime.now().isoformat(),
            "simulation_id": simulation_id,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "round": round,
            "function": function_name,
            "arguments": function_args,
            "content": content[:500] if content else "",
            "content_full": content,
            "usage": usage,
            "status_code": status_code
        }
        self._llm_logs.append(log_entry)
        self._save_to_json()

    def log_metric(
        self,
        simulation_id: str,
        round: int,
        metric_name: str,
        metric_value: float,
        metric_category: str = "",
        metadata: Optional[Dict] = None
    ) -> None:
        """
        记录指标数据

        Args:
            simulation_id: 仿真ID
            round: 轮次
            metric_name: 指标名称
            metric_value: 指标值
            metric_category: 指标分类
            metadata: 附加元数据
        """
        log_entry = LogEntry(
            log_id=f"log_metric_{datetime.now().timestamp()}",
            log_type=LogType.METRIC,
            simulation_id=simulation_id,
            round=round,
            agent_id=None,
            timestamp=datetime.now(),
            content=f"[指标] {metric_name}: {metric_value}",
            details={
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metric_category": metric_category,
                "metadata": metadata or {}
            }
        )
        self._log_entries.append(log_entry)
        self._save_to_json()

    def log_power_metrics(
        self,
        simulation_id: str,
        round: int,
        agent_id: str,
        agent_name: str,
        power_metrics: Dict,
        comprehensive_power: float
    ) -> None:
        """
        记录实力指标

        Args:
            simulation_id: 仿真ID
            round: 轮次
            agent_id: 智能体ID
            agent_name: 智能体名称
            power_metrics: 实力指标字典
            comprehensive_power: 综合实力
        """
        metric_entry = {
            "type": "power_metrics",
            "timestamp": datetime.now().isoformat(),
            "simulation_id": simulation_id,
            "round": round,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "power_metrics": power_metrics,
            "comprehensive_power": comprehensive_power
        }
        self._metrics_logs.append(metric_entry)
        self._save_to_json()

    def log_order_metrics(
        self,
        simulation_id: str,
        round: int,
        order_type: str,
        confidence: float,
        metrics: Dict
    ) -> None:
        """
        记录国际秩序指标

        Args:
            simulation_id: 仿真ID
            round: 轮次
            order_type: 秩序类型
            confidence: 置信度
            metrics: 其他秩序指标
        """
        metric_entry = {
            "type": "order_metrics",
            "timestamp": datetime.now().isoformat(),
            "simulation_id": simulation_id,
            "round": round,
            "order_type": order_type,
            "confidence": confidence,
            "metrics": metrics
        }
        self._metrics_logs.append(metric_entry)
        self._save_to_json()

    def log_environment_indicators(
        self,
        simulation_id: str,
        round: int,
        indicators: Dict
    ) -> None:
        """
        记录环境指标

        Args:
            simulation_id: 仿真ID
            round: 轮次
            indicators: 环境指标字典
        """
        metric_entry = {
            "type": "environment_indicators",
            "timestamp": datetime.now().isoformat(),
            "simulation_id": simulation_id,
            "round": round,
            "indicators": indicators
        }
        self._metrics_logs.append(metric_entry)
        self._save_to_json()

    def log_round_summary(
        self,
        simulation_id: str,
        round: int,
        summary: Dict
    ) -> None:
        """
        记录轮次总结

        Args:
            simulation_id: 仿真ID
            round: 轮次
            summary: 轮次总结信息
        """
        metric_entry = {
            "type": "round_summary",
            "timestamp": datetime.now().isoformat(),
            "simulation_id": simulation_id,
            "round": round,
            "summary": summary
        }
        self._metrics_logs.append(metric_entry)
        self._save_to_json()

    def _save_to_json(self) -> None:
        """
        保存所有日志到JSON文件
        """
        try:
            # 准备JSON数据
            log_data = {
                "simulation_id": self.simulation_id or "unknown",
                "start_time": datetime.now().isoformat(),
                "entries": [log.to_dict(include_reasoning=True) for log in self._log_entries],
                "llm_logs": self._llm_logs,
                "metrics_logs": self._metrics_logs,
                "total_entries": len(self._log_entries),
                "total_llm_logs": len(self._llm_logs),
                "total_metrics_logs": len(self._metrics_logs)
            }

            # 写入JSON文件
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

            # 同时保存为单独的日志文件分类
            if self.simulation_id:
                self._save_categorized_json(log_data)

        except Exception as e:
            # 避免日志错误影响主流程
            print(f"保存JSON日志失败: {e}")

    def _save_categorized_json(self, log_data: Dict) -> None:
        """
        保存分类的JSON日志文件

        Args:
            log_data: 日志数据
        """
        try:
            # 保存LLM日志
            llm_log_file = self.sim_log_dir / "llm_logs.json"
            with open(llm_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data.get("llm_logs", []), f, indent=2, ensure_ascii=False)

            # 保存指标日志
            metrics_log_file = self.sim_log_dir / "metrics_logs.json"
            with open(metrics_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data.get("metrics_logs", []), f, indent=2, ensure_ascii=False)

            # 保存决策日志
            decisions = [e for e in log_data.get("entries", []) if e.get("log_type") == "decision"]
            decisions_log_file = self.sim_log_dir / "decisions.json"
            with open(decisions_log_file, 'w', encoding='utf-8') as f:
                json.dump(decisions, f, indent=2, ensure_ascii=False)

            # 保存行动日志
            actions = [e for e in log_data.get("entries", []) if e.get("log_type") == "action"]
            actions_log_file = self.sim_log_dir / "actions.json"
            with open(actions_log_file, 'w', encoding='utf-8') as f:
                json.dump(actions, f, indent=2, ensure_ascii=False)

            # 保存发言日志
            speeches = [e for e in log_data.get("entries", []) if e.get("log_type") == "speech"]
            speeches_log_file = self.sim_log_dir / "speeches.json"
            with open(speeches_log_file, 'w', encoding='utf-8') as f:
                json.dump(speeches, f, indent=2, ensure_ascii=False)

            # 保存事件日志
            events = [e for e in log_data.get("entries", []) if e.get("log_type") == "event"]
            events_log_file = self.sim_log_dir / "events.json"
            with open(events_log_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"保存分类JSON日志失败: {e}")

    def get_json_logs(self) -> Optional[Dict]:
        """
        读取JSON日志

        Returns:
            日志字典，如果文件不存在返回None
        """
        try:
            if not self.json_log_file.exists():
                return None

            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            print(f"读取JSON日志失败: {e}")
            return None
