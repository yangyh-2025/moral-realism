"""
工作流编排完善 - 对应技术方案3.5节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime
import os
import pickle
import json
import uuid


class WorkflowState(str, Enum):
    """工作流状态"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowEvent(str, Enum):
    """工作流事件"""
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    COMPLETE = "complete"
    FAIL = "fail"


class WorkflowTransitionError(Exception):
    """工作流转换错误"""
    def __init__(self, current_state: WorkflowState, event: WorkflowEvent, message: str = ""):
        self.current_state = current_state
        self.event = event
        self.message = message or f"Invalid transition: {current_state.value} + {event.value}"
        super().__init__(self.message)


class WorkflowStateMachine:
    """工作流状态机"""

    # 状态转换表
    _TRANSITIONS = {
        WorkflowState.INITIALIZED: {
            WorkflowEvent.START: WorkflowState.RUNNING,
        },
        WorkflowState.RUNNING: {
            WorkflowEvent.PAUSE: WorkflowState.PAUSED,
            WorkflowEvent.CANCEL: WorkflowState.CANCELLED,
            WorkflowEvent.COMPLETE: WorkflowState.COMPLETED,
            WorkflowEvent.FAIL: WorkflowState.FAILED,
        },
        WorkflowState.PAUSED: {
            WorkflowEvent.RESUME: WorkflowState.RUNNING,
            WorkflowEvent.CANCEL: WorkflowState.CANCELLED,
        },
        WorkflowState.COMPLETED: {
            # 终态，不允许转换
        },
        WorkflowState.FAILED: {
            # 终态，不允许转换
        },
        WorkflowState.CANCELLED: {
            # 终态，不允许转换
        },
    }

    def __init__(self, initial_state: WorkflowState = WorkflowState.INITIALIZED):
        """
        Args:
            initial_state: 初始状态
        """
        self._state = initial_state
        self._transition_history: List[Dict] = []

    def transition(self, event: WorkflowEvent) -> WorkflowState:
        """
        状态转换

        Args:
            event: 触发事件

        Returns:
            新状态

        Raises:
            WorkflowTransitionError: 转换无效时抛出
        """
        # 检查转换是否有效
        allowed_transitions = self._TRANSITIONS.get(self._state, {})

        if event not in allowed_transitions:
            raise WorkflowTransitionError(self._state, event)

        # 执行转换
        new_state = allowed_transitions[event]

        # 记录转换历史
        self._transition_history.append({
            "from_state": self._state.value,
            "event": event.value,
            "to_state": new_state.value,
            "timestamp": datetime.now().isoformat()
        })

        self._state = new_state
        return new_state

    def get_current_state(self) -> WorkflowState:
        """
        获取当前状态

        Returns:
            当前状态
        """
        return self._state

    def get_allowed_transitions(self) -> List[WorkflowEvent]:
        """
        获取允许的转换

        Returns:
            允许的事件列表
        """
        return list(self._TRANSITIONS.get(self._state, {}).keys())

    def get_transition_history(self) -> List[Dict]:
        """
        获取转换历史

        Returns:
            转换历史列表
        """
        return self._transition_history.copy()

    def is_terminal_state(self) -> bool:
        """
        是否为终态

        Returns:
            是否为终态
        """
        return self._state in [
            WorkflowState.COMPLETED,
            WorkflowState.FAILED,
            WorkflowState.CANCELLED
        ]


class Checkpoint(BaseModel):
    """检查点"""
    checkpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="检查点ID")
    simulation_id: str = Field(..., description="仿真ID")
    round: int = Field(..., description="当前轮次")
    state: Dict = Field(..., description="状态数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    metadata: Dict = Field(default_factory=dict, description="元数据")


class WorkflowRecovery:
    """工作流恢复"""

    def __init__(self, checkpoint_dir: str = "data/checkpoints/"):
        """
        Args:
            checkpoint_dir: 检查点目录
        """
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save_checkpoint(
        self,
        simulation_id: str,
        round: int,
        state: Dict,
        metadata: Optional[Dict] = None
    ) -> Checkpoint:
        """
        保存检查点

        Args:
            simulation_id: 仿真ID
            round: 当前轮次
            state: 状态数据
            metadata: 元数据

        Returns:
            检查点
        """
        checkpoint = Checkpoint(
            simulation_id=simulation_id,
            round=round,
            state=state,
            metadata=metadata or {}
        )

        # 保存到磁盘
        checkpoint_file = os.path.join(
            self.checkpoint_dir,
            f"{simulation_id}_round_{round}.pkl"
        )

        try:
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint.model_dump(), f)

            # 同时保存JSON版本（便于查看）
            json_file = checkpoint_file.replace('.pkl', '.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint.model_dump(), f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"保存检查点失败: {e}")

        return checkpoint

    def load_checkpoint(
        self,
        simulation_id: str,
        round: Optional[int] = None
    ) -> Optional[Checkpoint]:
        """
        加载检查点

        Args:
            simulation_id: 仿真ID
            round: 轮次，如果为None则加载最新的检查点

        Returns:
            检查点，如果不存在则返回None
        """
        if round is not None:
            # 加载指定轮次的检查点
            checkpoint_file = os.path.join(
                self.checkpoint_dir,
                f"{simulation_id}_round_{round}.pkl"
            )
        else:
            # 加载最新的检查点
            latest = self._find_latest_checkpoint(simulation_id)
            if latest is None:
                return None
            checkpoint_file = latest

        if not os.path.exists(checkpoint_file):
            return None

        try:
            with open(checkpoint_file, 'rb') as f:
                data = pickle.load(f)
                return Checkpoint(**data)
        except Exception as e:
            print(f"加载检查点失败: {e}")
            return None

    def _find_latest_checkpoint(self, simulation_id: str) -> Optional[str]:
        """查找最新的检查点"""
        pattern = f"{simulation_id}_round_*.pkl"
        checkpoints = []

        for filename in os.listdir(self.checkpoint_dir):
            if filename.startswith(f"{simulation_id}_round_") and filename.endswith('.pkl'):
                checkpoints.append(filename)

        if not checkpoints:
            return None

        # 按轮次排序，取最后一个
        checkpoints.sort()
        latest = checkpoints[-1]

        return os.path.join(self.checkpoint_dir, latest)

    def resume_from_checkpoint(
        self,
        simulation_id: str,
        round: Optional[int] = None
    ) -> Dict:
        """
        从检查点恢复

        Args:
            simulation_id: 仿真ID
            round: 轮次，如果为None则从最新的检查点恢复

        Returns:
            恢复结果
        """
        checkpoint = self.load_checkpoint(simulation_id, round)

        if checkpoint is None:
            return {
                "success": False,
                "message": f"未找到检查点: {simulation_id} round={round}"
            }

        return {
            "success": True,
            "checkpoint_id": checkpoint.checkpoint_id,
            "simulation_id": checkpoint.simulation_id,
            "round": checkpoint.round,
            "state": checkpoint.state,
            "metadata": checkpoint.metadata,
            "timestamp": checkpoint.timestamp
        }

    def list_checkpoints(self, simulation_id: str) -> List[Dict]:
        """
        列出所有检查点

        Args:
            simulation_id: 仿真ID

        Returns:
            检查点信息列表
        """
        checkpoints = []

        for filename in os.listdir(self.checkpoint_dir):
            if filename.startswith(f"{simulation_id}_round_") and filename.endswith('.pkl'):
                try:
                    checkpoint_file = os.path.join(self.checkpoint_dir, filename)
                    with open(checkpoint_file, 'rb') as f:
                        data = pickle.load(f)
                        checkpoints.append({
                            "checkpoint_id": data.get("checkpoint_id"),
                            "round": data.get("round"),
                            "timestamp": data.get("timestamp")
                        })
                except Exception:
                    pass

        # 按轮次排序
        checkpoints.sort(key=lambda x: x.get("round", 0))

        return checkpoints

    def cleanup_checkpoints(self, simulation_id: str, keep_last: int = 3):
        """
        清理旧的检查点

        Args:
            simulation_id: 仿真ID
            keep_last: 保留最近N个检查点
        """
        checkpoints = self.list_checkpoints(simulation_id)

        if len(checkpoints) <= keep_last:
            return

        # 删除旧的检查点
        for checkpoint in checkpoints[:-keep_last]:
            round = checkpoint.get("round")
            checkpoint_file = os.path.join(
                self.checkpoint_dir,
                f"{simulation_id}_round_{round}.pkl"
            )
            json_file = checkpoint_file.replace('.pkl', '.json')

            try:
                if os.path.exists(checkpoint_file):
                    os.remove(checkpoint_file)
                if os.path.exists(json_file):
                    os.remove(json_file)
            except Exception as e:
                print(f"删除检查点失败: {e}")


class ProgressInfo(BaseModel):
    """进度信息"""
    simulation_id: str = Field(..., description="仿真ID")
    current_round: int = Field(0, description="当前轮次")
    total_rounds: int = Field(0, description="总轮次")
    percentage: float = Field(0.0, description="完成百分比")
    estimated_time_remaining: Optional[float] = Field(None, description="预计剩余时间（秒）")
    current_stage: str = Field(default="", description="当前阶段")
    started_at: Optional[str] = Field(None, description="开始时间")


class ParallelWorkflowExecutor:
    """并行工作流执行器"""

    def __init__(self, max_workers: int = 4):
        """
        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self._semaphore = asyncio.Semaphore(max_workers)
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._progress_info: Dict[str, ProgressInfo] = {}

    async def execute_parallel(
        self,
        workflows: List[Dict],
        run_func: Callable
    ) -> List[Dict]:
        """
        并行执行工作流

        Args:
            workflows: 工作流列表
            run_func: 运行函数

        Returns:
            结果列表
        """
        tasks = []

        for workflow in workflows:
            task = asyncio.create_task(self._execute_with_semaphore(workflow, run_func))
            tasks.append(task)

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常
        return [r for r in results if not isinstance(r, Exception)]

    async def _execute_with_semaphore(
        self,
        workflow: Dict,
        run_func: Callable
    ) -> Dict:
        """使用信号量控制并发"""
        async with self._semaphore:
            return await run_func(workflow)

    def update_progress(
        self,
        simulation_id: str,
        current_round: int,
        total_rounds: int,
        current_stage: str = ""
    ):
        """
        更新进度

        Args:
            simulation_id: 仿真ID
            current_round: 当前轮次
            total_rounds: 总轮次
            current_stage: 当前阶段
        """
        if total_rounds > 0:
            percentage = (current_round / total_rounds) * 100
        else:
            percentage = 0.0

        progress = self._progress_info.get(simulation_id)

        if progress:
            progress.current_round = current_round
            progress.percentage = percentage
            if current_stage:
                progress.current_stage = current_stage
        else:
            progress = ProgressInfo(
                simulation_id=simulation_id,
                current_round=current_round,
                total_rounds=total_rounds,
                percentage=percentage,
                current_stage=current_stage,
                started_at=datetime.now().isoformat()
            )
            self._progress_info[simulation_id] = progress

    def monitor_progress(self, simulation_id: str) -> Optional[ProgressInfo]:
        """
        监控进度

        Args:
            simulation_id: 仿真ID

        Returns:
            进度信息
        """
        return self._progress_info.get(simulation_id)

    def get_all_progress(self) -> Dict[str, ProgressInfo]:
        """
        获取所有进度

        Returns:
            所有进度信息字典
        """
        return self._progress_info.copy()


class WorkflowCallbacks:
    """工作流回调"""

    def __init__(self):
        self._on_round_start: Optional[Callable] = None
        self._on_round_complete: Optional[Callable] = None
        self._on_round_fail: Optional[Callable] = None
        self._on_workflow_start: Optional[Callable] = None
        self._on_workflow_complete: Optional[Callable] = None
        self._on_workflow_fail: Optional[Callable] = None

    def on_round_start(self, func: Callable):
        """设置轮次开始回调"""
        self._on_round_start = func

    def on_round_complete(self, func: Callable):
        """设置轮次完成回调"""
        self._on_round_complete = func

    def on_round_fail(self, func: Callable):
        """设置轮次失败回调"""
        self._on_round_fail = func

    def on_workflow_start(self, func: Callable):
        """设置工作流开始回调"""
        self._on_workflow_start = func

    def on_workflow_complete(self, func: Callable):
        """设置工作流完成回调"""
        self._on_workflow_complete = func

    def on_workflow_fail(self, func: Callable):
        """设置工作流失败回调"""
        self._on_workflow_fail = func


class MultiRoundWorkflow:
    """多轮工作流"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Args:
            config: 工作流配置
        """
        self.config = config or {}
        self.state_machine = WorkflowStateMachine(WorkflowState.INITIALIZED)
        self.recovery = WorkflowRecovery(
            self.config.get("checkpoint_dir", "data/checkpoints/")
        )
        self.executor = ParallelWorkflowExecutor(
            self.config.get("max_workers", 4)
        )
        self.callbacks = WorkflowCallbacks()

        # 运行时状态
        self._results: List[Dict] = []
        self._current_round = 0
        self._total_rounds = 0
        self._simulation_id = ""

    async def execute(
        self,
        agents: List,
        simulation_id: str,
        total_rounds: int,
        start_round: int = 0,
        round_func: Optional[Callable] = None,
        checkpoint_interval: int = 10
    ) -> List[Dict]:
        """
        执行多轮迭代仿真

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
            total_rounds: 总轮次
            start_round: 起始轮次
            round_func: 单轮执行函数
            checkpoint_interval: 检查点间隔

        Returns:
            所有轮次的结果列表
        """
        # 初始化状态
        self._simulation_id = simulation_id
        self._total_rounds = total_rounds
        self._current_round = start_round
        self._results = []

        # 触发工作流开始事件
        try:
            self.state_machine.transition(WorkflowEvent.START)
        except WorkflowTransitionError as e:
            raise RuntimeError(f"工作流状态无效: {e}")

        if self.callbacks._on_workflow_start:
            await self._run_callback(self.callbacks._on_workflow_start, simulation_id, total_rounds)

        # 执行各轮
        try:
            for round in range(start_round, total_rounds):
                self._current_round = round

                # 检查是否已取消
                if self.state_machine.get_current_state() == WorkflowState.CANCELLED:
                    break

                # 检查是否已暂停
                while self.state_machine.get_current_state() == WorkflowState.PAUSED:
                    await asyncio.sleep(0.1)

                # 更新进度
                self.executor.update_progress(
                    simulation_id,
                    round + 1,
                    total_rounds,
                    f"执行轮次 {round + 1}/{total_rounds}"
                )

                # 执行单轮
                try:
                    if self.callbacks._on_round_start:
                        await self._run_callback(
                            self.callbacks._on_round_start,
                            simulation_id,
                            round
                        )

                    if round_func:
                        round_result = await round_func(agents, simulation_id, round)
                    else:
                        round_result = {"round": round, "status": "completed"}

                    self._results.append(round_result)

                    if self.callbacks._on_round_complete:
                        await self._run_callback(
                            self.callbacks._on_round_complete,
                            simulation_id,
                            round,
                            round_result
                        )

                    # 保存检查点
                    if (round + 1) % checkpoint_interval == 0:
                        state = {
                            "agents": agents,
                            "results": self._results,
                            "current_round": round
                        }
                        self.recovery.save_checkpoint(simulation_id, round, state)

                except Exception as e:
                    if self.callbacks._on_round_fail:
                        await self._run_callback(
                            self.callbacks._on_round_fail,
                            simulation_id,
                            round,
                            e
                        )
                    raise

            # 完成工作流
            self.state_machine.transition(WorkflowEvent.COMPLETE)

            if self.callbacks._on_workflow_complete:
                await self._run_callback(
                    self.callbacks._on_workflow_complete,
                    simulation_id,
                    self._results
                )

            return self._results

        except Exception as e:
            self.state_machine.transition(WorkflowEvent.FAIL)

            if self.callbacks._on_workflow_fail:
                await self._run_callback(
                    self.callbacks._on_workflow_fail,
                    simulation_id,
                    e
                )

            raise

    async def _run_callback(self, callback: Callable, *args):
        """运行回调函数"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            print(f"回调函数执行失败: {e}")

    def pause(self) -> None:
        """暂停仿真"""
        try:
            self.state_machine.transition(WorkflowEvent.PAUSE)
        except WorkflowTransitionError as e:
            print(f"无法暂停工作流: {e}")

    def resume(self) -> None:
        """继续仿真"""
        try:
            self.state_machine.transition(WorkflowEvent.RESUME)
        except WorkflowTransitionError as e:
            print(f"无法继续工作流: {e}")

    def cancel(self) -> None:
        """停止仿真"""
        try:
            self.state_machine.transition(WorkflowEvent.CANCEL)
        except WorkflowTransitionError as e:
            print(f"无法取消工作流: {e}")

    def get_state(self) -> WorkflowState:
        """获取当前状态"""
        return self.state_machine.get_current_state()

    def get_results(self) -> List[Dict]:
        """获取结果"""
        return self._results.copy()

    def reset(self):
        """重置工作流"""
        self.state_machine = WorkflowStateMachine(WorkflowState.INITIALIZED)
        self._results = []
        self._current_round = 0
        self._simulation_id = ""
        self._total_rounds = 0

    async def resume_from_checkpoint(
        self,
        simulation_id: str,
        agents: List,
        round_func: Callable,
        total_rounds: Optional[int] = None,
        checkpoint_interval: int = 10
    ) -> List[Dict]:
        """
        从检查点恢复

        Args:
            simulation_id: 仿真ID
            agents: 智能体列表
            round_func: 单轮执行函数
            total_rounds: 总轮次，如果为None则使用检查点中的值
            checkpoint_interval: 检查点间隔

        Returns:
            结果列表
        """
        # 加载检查点
        recovery_result = self.recovery.resume_from_checkpoint(simulation_id)

        if not recovery_result.get("success"):
            raise RuntimeError(f"恢复失败: {recovery_result.get('message')}")

        # 恢复状态
        start_round = recovery_result["round"] + 1
        state = recovery_result["state"]

        if total_rounds is None:
            total_rounds = state.get("total_rounds", 100)

        # 恢复智能体状态
        saved_agents = state.get("agents")
        if saved_agents:
            agents = saved_agents

        # 恢复结果
        self._results = state.get("results", [])

        # 继续执行
        return await self.execute(
            agents=agents,
            simulation_id=simulation_id,
            total_rounds=total_rounds,
            start_round=start_round,
            round_func=round_func,
            checkpoint_interval=checkpoint_interval
        )
