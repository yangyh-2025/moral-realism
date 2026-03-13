"""
多轮迭代工作流 - 对应技术方案7.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional
import asyncio


class MultiRoundWorkflow:
    """
    多轮迭代工作流

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        single_round_workflow,  # SingleRoundWorkflow实例
        storage  # StorageEngine实例
    ):
        self.single_round_workflow = single_round_workflow
        self.storage = storage
        self.is_paused = False
        self.is_stopped = False

    async def execute(
        self,
        agents: List,  # BaseAgent实例列表
        simulation_id: str,
        total_rounds: int,
        start_round: int = 0
    ) -> List[Dict]:
        """
        执行多轮迭代仿真

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
            total_rounds: 总轮次
            start_round: 起始轮次

        Returns:
            所有轮次的结果列表
        """
        results = []

        for round in range(start_round, total_rounds):
            # 检查停止标志
            if self.is_stopped:
                break

            # 检查暂停标志
            while self.is_paused and not self.is_stopped:
                await asyncio.sleep(0.1)

            # 执行单轮仿真
            round_result = await self.single_round_workflow.execute(
                agents=agents,
                simulation_id=simulation_id,
                round=round
            )

            results.append(round_result)

        return results

    def pause(self) -> None:
        """暂停仿真"""
        self.is_paused = True

    def resume(self) -> None:
        """继续仿真"""
        self.is_paused = False

    def stop(self) -> None:
        """停止仿真"""
        self.is_stopped = True
        self.is_paused = False
