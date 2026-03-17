"""
仿真管理服务 - 仿真生命周期管理和查询

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import uuid
import json

from infrastructure.storage.storage_engine import StorageEngine


class SimulationStatus(Enum):
    """仿真状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class SimulationConfig:
    """仿真配置"""
    simulation_id: str
    total_rounds: int = 100
    round_duration_months: int = 6
    random_event_prob: float = 0.1
    agent_configs: List[Dict] = field(default_factory=list)
    event_config: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Simulation:
    """仿真实例"""
    simulation_id: str
    config: SimulationConfig
    status: SimulationStatus
    current_round: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class SimulationResult:
    """仿真结果"""
    simulation_id: str
    total_rounds: int
    completed_rounds: int
    status: SimulationStatus
    summary: Dict = field(default_factory=dict)
    final_state: Dict = field(default_factory=dict)


@dataclass
class ProgressInfo:
    """仿真进度信息"""
    simulation_id: str
    current_round: int
    total_rounds: int
    percentage: float
    estimated_remaining: Optional[float] = None
    current_phase: Optional[str] = None


@dataclass
class QueryFilters:
    """查询过滤器"""
    status: Optional[SimulationStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


class SimulationLifecycle:
    """
    仿真生命周期管理

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, storage: StorageEngine):
        self.storage = storage
        self._active_simulations: Dict[str, Simulation] = {}
        self._simulation_tasks: Dict[str, asyncio.Task] = {}

    async def create_simulation(self, config: SimulationConfig) -> Simulation:
        """
        创建仿真实例

        Args:
            config: 仿真配置

        Returns:
            Simulation: 创建的仿真实例
        """
        if config.simulation_id in self._active_simulations:
            raise ValueError(f"仿真 {config.simulation_id} 已存在")

        simulation = Simulation(
            simulation_id=config.simulation_id,
            config=config,
            status=SimulationStatus.PENDING,
            start_time=datetime.now()
        )

        self._active_simulations[simulation.simulation_id] = simulation

        # 保存仿真开始记录到存储
        self.storage.save_simulation_start(
            simulation_id=simulation.simulation_id,
            config=config.__dict__
        )

        return simulation

    async def start_simulation(self, simulation_id: str) -> SimulationResult:
        """
        启动仿真

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationResult: 仿真结果
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status == SimulationStatus.RUNNING:
            raise ValueError(f"仿真 {simulation_id} 正在运行中")

        simulation.status = SimulationStatus.RUNNING
        simulation.start_time = datetime.now() if not simulation.start_time else simulation.start_time

        # 在实际实现中，这里会启动仿真运行任务
        # await self._run_simulation(simulation)

        return SimulationResult(
            simulation_id=simulation.simulation_id,
            total_rounds=simulation.config.total_rounds,
            completed_rounds=simulation.current_round,
            status=simulation.status,
            summary={"message": "仿真已启动"}
        )

    async def pause_simulation(self, simulation_id: str) -> None:
        """
        暂停仿真

        Args:
            simulation_id: 仿真ID
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status != SimulationStatus.RUNNING:
            raise ValueError(f"仿真 {simulation_id} 未在运行")

        simulation.status = SimulationStatus.PAUSED

        # 在实际实现中，这里会暂停仿真任务
        # if simulation_id in self._simulation_tasks:
        #     self._simulation_tasks[simulation_id].cancel()

    async def resume_simulation(self, simulation_id: str) -> SimulationResult:
        """
        继续仿真

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationResult: 仿真结果
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status != SimulationStatus.PAUSED:
            raise ValueError(f"仿真 {simulation_id} 未处于暂停状态")

        simulation.status = SimulationStatus.RUNNING

        # 在实际实现中，这里会继续仿真任务

        return SimulationResult(
            simulation_id=simulation.simulation_id,
            total_rounds=simulation.config.total_rounds,
            completed_rounds=simulation.current_round,
            status=simulation.status,
            summary={"message": "仿真已继续"}
        )

    async def stop_simulation(self, simulation_id: str) -> None:
        """
        停止仿真

        Args:
            simulation_id: 仿真ID
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status not in [SimulationStatus.RUNNING, SimulationStatus.PAUSED]:
            raise ValueError(f"仿真 {simulation_id} 未在运行")

        simulation.status = SimulationStatus.STOPPED
        simulation.end_time = datetime.now()

        # 在实际实现中，这里会停止仿真任务
        # if simulation_id in self._simulation_tasks:
        #     self._simulation_tasks[simulation_id].cancel()

    async def delete_simulation(self, simulation_id: str) -> None:
        """
        删除仿真

        Args:
            simulation_id: 仿真ID
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        # 只允许删除已完成的仿真
        if simulation.status not in [SimulationStatus.COMPLETED, SimulationStatus.STOPPED, SimulationStatus.ERROR]:
            raise ValueError(f"只能删除已完成或停止的仿真")

        del self._active_simulations[simulation_id]

        # 在实际实现中，这里会清理存储中的数据


class SimulationQuery:
    """
    仿真状态查询

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, lifecycle: SimulationLifecycle):
        self.lifecycle = lifecycle

    def get_simulation_status(self, simulation_id: str) -> SimulationStatus:
        """
        获取仿真状态

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationStatus: 仿真状态
        """
        if simulation_id not in self.lifecycle._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        return self.lifecycle._active_simulations[simulation_id].status

    def get_simulation_config(self, simulation_id: str) -> SimulationConfig:
        """
        获取仿真配置

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationConfig: 仿真配置
        """
        if simulation_id not in self.lifecycle._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        return self.lifecycle._active_simulations[simulation_id].config

    def get_simulation_progress(self, simulation_id: str) -> ProgressInfo:
        """
        获取仿真进度

        Args:
            simulation_id: 仿真ID

        Returns:
            ProgressInfo: 进度信息
        """
        if simulation_id not in self.lifecycle._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self.lifecycle._active_simulations[simulation_id]
        total_rounds = simulation.config.total_rounds
        current_round = simulation.current_round

        percentage = (current_round / total_rounds * 100) if total_rounds > 0 else 0.0

        # 简单估算剩余时间
        estimated_remaining = None
        if simulation.start_time and current_round > 0:
            elapsed = (datetime.now() - simulation.start_time).total_seconds()
            if elapsed > 0:
                time_per_round = elapsed / current_round
                estimated_remaining = time_per_round * (total_rounds - current_round)

        return ProgressInfo(
            simulation_id=simulation_id,
            current_round=current_round,
            total_rounds=total_rounds,
            percentage=percentage,
            estimated_remaining=estimated_remaining,
            current_phase=self._get_current_phase(simulation)
        )

    def list_simulations(self, filters: Optional[QueryFilters] = None) -> List[Simulation]:
        """
        列出仿真

        Args:
            filters: 查询过滤器

        Returns:
            List[Simulation]: 仿真列表
        """
        if filters is None:
            filters = QueryFilters()

        simulations = list(self.lifecycle._active_simulations.values())

        # 应用过滤器
        if filters.status is not None:
            simulations = [s for s in simulations if s.status == filters.status]

        if filters.start_date is not None:
            simulations = [
                s for s in simulations
                if s.start_time and s.start_time >= filters.start_date
            ]

        if filters.end_date is not None:
            simulations = [
                s for s in simulations
                if s.start_time and s.start_time <= filters.end_date
            ]

        # 应用分页
        simulations = simulations[filters.offset:filters.offset + filters.limit]

        return simulations

    def _get_current_phase(self, simulation: Simulation) -> Optional[str]:
        """获取当前仿真阶段"""
        total_rounds = simulation.config.total_rounds
        current_round = simulation.current_round

        if current_round == 0:
            return "初始化"
        elif current_round >= total_rounds:
            return "完成"
        else:
            percentage = current_round / total_rounds
            if percentage < 0.25:
                return "早期阶段"
            elif percentage < 0.5:
                return "中期阶段"
            elif percentage < 0.75:
                return "后期阶段"
            else:
                return "收尾阶段"
