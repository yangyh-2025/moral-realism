"""
JSON导出服务 - 导出仿真完整数据到JSON格式

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JSONExporter:
    """
    JSON导出服务

    将仿真数据导出为JSON格式，存储在仿真特定的文件夹中
    """

    def __init__(self, log_dir: str = "logs"):
        """
        初始化导出服务

        Args:
            log_dir: 日志目录根路径
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def export_simulation(
        self,
        simulation_id: str,
        data: Dict[str, Any]
    ) -> str:
        """
        导出仿真完整数据

        Args:
            simulation_id: 仿真ID
            data: 仿真数据字典，包含：
                - agents: 智能体列表
                - decisions: 决策列表
                - interactions: 互动列表
                - metrics: 指标数据
                - events: 事件列表
                - llm_logs: LLM日志

        Returns:
            导出文件路径
        """
        # 创建仿真特定的导出文件夹
        sim_export_dir = self.log_dir / simulation_id
        sim_export_dir.mkdir(parents=True, exist_ok=True)

        # 添加元数据
        export_data = {
            "simulation_id": simulation_id,
            "export_time": datetime.now().isoformat(),
            "summary": {
                "total_agents": len(data.get("agents", [])),
                "total_decisions": len(data.get("decisions", [])),
                "total_interactions": len(data.get("interactions", [])),
                "total_events": len(data.get("events", [])),
                "total_llm_logs": len(data.get("llm_logs", []))
            },
            "data": data
        }

        # 导出完整数据
        export_file = sim_export_dir / "full_export.json"
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"仿真数据已导出到: {export_file}")
            return str(export_file)

        except Exception as e:
            logger.error(f"导出仿真数据失败: {e}", exc_info=True)
            raise

    def export_round_data(
        self,
        simulation_id: str,
        round: int,
        data: Dict[str, Any]
    ) -> str:
        """
        导出单轮数据

        Args:
            simulation_id: 仿真ID
            round: 轮次
            data: 轮次数据

        Returns:
            导出文件路径
        """
        # 创建仿真特定的导出文件夹
        sim_export_dir = self.log_dir / simulation_id / "rounds"
        sim_export_dir.mkdir(parents=True, exist_ok=True)

        # 导出轮次数据
        round_file = sim_export_dir / f"round_{round}.json"
        try:
            with open(round_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"轮次数据已导出: {round_file}")
            return str(round_file)

        except Exception as e:
            logger.error(f"导出轮次数据失败: {e}", exc_info=True)
            raise

    def export_agent_states(
        self,
        simulation_id: str,
        agents: List[Any]
    ) -> str:
        """
        导出智能体状态

        Args:
            simulation_id: 仿真ID
            agents: 智能体列表

        Returns:
            导出文件路径
        """
        # 创建仿真特定的导出文件夹
        sim_export_dir = self.log_dir / simulation_id
        sim_export_dir.mkdir(parents=True, exist_ok=True)

        # 提取智能体状态
        agent_states = []
        for agent in agents:
            if hasattr(agent, 'state'):
                state_dict = {
                    'agent_id': agent.state.agent_id,
                    'name': agent.state.name,
                    'region': agent.state.region
                }

                # 添加实力指标
                if hasattr(agent.state, 'power_metrics') and agent.state.power_metrics:
                    state_dict['power_metrics'] = {
                        'critical_mass': agent.state.power_metrics.critical_mass,
                        'economic_capability': agent.state.power_metrics.economic_capability,
                        'military_capability': agent.state.power_metrics.military_capability,
                        'strategic_purpose': agent.state.power_metrics.strategic_purpose,
                        'national_will': agent.state.power_metrics.national_will,
                        'comprehensive_power': agent.state.power_metrics.calculate_comprehensive_power()
                    }

                # 添加关系
                if hasattr(agent.state, 'relationships'):
                    state_dict['relationships'] = agent.state.relationships

                # 添加记忆
                if hasattr(agent.state, 'public_memory'):
                    state_dict['public_memory'] = agent.state.public_memory
                if hasattr(agent.state, 'private_memory'):
                    state_dict['private_memory'] = agent.state.private_memory

                agent_states.append(state_dict)

        # 导出智能体状态
        agent_file = sim_export_dir / "agent_states.json"
        try:
            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'agents': agent_states
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"智能体状态已导出: {agent_file}")
            return str(agent_file)

        except Exception as e:
            logger.error(f"导出智能体状态失败: {e}", exc_info=True)
            raise

    def get_export_summary(self, simulation_id: str) -> Dict[str, Any]:
        """
        获取导出摘要

        Args:
            simulation_id: 仿真ID

        Returns:
            导出摘要信息
        """
        sim_dir = self.log_dir / simulation_id

        if not sim_dir.exists():
            return {
                "simulation_id": simulation_id,
                "exported": False,
                "message": "仿真导出目录不存在"
            }

        # 统计文件
        files = list(sim_dir.glob("*.json"))
        round_files = list((sim_dir / "rounds").glob("*.json")) if (sim_dir / "rounds").exists() else []

        summary = {
            "simulation_id": simulation_id,
            "exported": True,
            "export_dir": str(sim_dir),
            "main_files": [f.name for f in files],
            "round_files_count": len(round_files),
            "total_files": len(files) + len(round_files),
            "export_timestamp": datetime.now().isoformat()
        }

        # 尝试读取导出摘要
        export_file = sim_dir / "full_export.json"
        if export_file.exists():
            try:
                with open(export_file, 'r', encoding='utf-8') as f:
                    export_data = json.load(f)
                    summary['export_summary'] = export_data.get('summary', {})
            except Exception as e:
                logger.warning(f"读取导出摘要失败: {e}")

        return summary


# 全局导出器实例
_global_exporter: Optional[JSONExporter] = None


def get_json_exporter(log_dir: str = "logs") -> JSONExporter:
    """
    获取全局JSON导出器实例（单例模式）

    Args:
        log_dir: 日志目录

    Returns:
        JSONExporter实例
    """
    global _global_exporter
    if _global_exporter is None:
        _global_exporter = JSONExporter(log_dir=log_dir)
    return _global_exporter


def clear_global_exporter() -> None:
    """清除全局导出器实例"""
    global _global_exporter
    _global_exporter = None
