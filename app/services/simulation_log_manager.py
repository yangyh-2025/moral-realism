"""
仿真日志管理器模块
负责管理仿真运行过程中的详细日志记录
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger


class SimulationLogManager:
    """
    仿真日志管理器类

    功能：
    - 在仿真启动时创建 logs/{project_id}/ 文件夹
    - 管理多个独立的日志文件
    - 为每条日志记录添加唯一时间戳
    - 确保异步操作的安全性
    """

    def __init__(self, project_id: int):
        """
        初始化日志管理器

        Args:
            project_id: 项目ID，用于创建日志文件夹
        """
        self.project_id = project_id
        self.base_dir = Path("logs") / str(project_id)
        self.lock = asyncio.Lock()
        self._file_handles: Dict[str, Any] = {}

        # 日志文件定义
        self.log_files = {
            "llm_interaction": "llm_interaction.log",
            "llm_following": "llm_following.log",
            "llm_goal_evaluation": "llm_goal_evaluation.log",
            "power_changes": "power_changes.log",
            "order_changes": "order_changes.log",
            "goal_evaluations": "goal_evaluations.log",
            "follower_relations": "follower_relations.log",
            "interactions": "interactions.log"
        }

        # 初始化日志文件夹和文件
        self._initialize_log_files()

    def _initialize_log_files(self):
        """创建日志文件夹和文件"""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建日志文件夹: {self.base_dir}")

            for log_type, filename in self.log_files.items():
                file_path = self.base_dir / filename
                if not file_path.exists():
                    file_path.touch()
                    logger.debug(f"创建日志文件: {file_path}")
        except Exception as e:
            logger.error(f"初始化日志文件失败: {e}", exc_info=True)
            raise

    def _get_timestamp(self) -> str:
        """获取唯一时间戳"""
        return datetime.now().isoformat()

    async def _write_log(self, log_type: str, data: Dict[str, Any]):
        """
        异步写入日志记录

        Args:
            log_type: 日志类型
            data: 要写入的数据字典
        """
        async with self.lock:
            try:
                file_path = self.base_dir / self.log_files[log_type]
                data["timestamp"] = self._get_timestamp()
                line = json.dumps(data, ensure_ascii=False) + "\n"

                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception as e:
                logger.error(f"写入日志失败 [{log_type}]: {e}", exc_info=True)

    async def log_llm_call(
        self,
        category: str,
        full_prompt: str,
        full_system_prompt: str,
        full_response: Any,
        **context
    ):
        """
        记录LLM调用（包含完整提示词和响应）

        Args:
            category: LLM调用类别 (interaction, following, goal_evaluation)
            full_prompt: 完整的用户提示词
            full_system_prompt: 完整的系统提示词
            full_response: 完整的LLM响应
            **context: 额外上下文信息 (round_num, agent_id, agent_name等)
        """
        log_data = {
            "full_prompt": full_prompt,
            "full_system_prompt": full_system_prompt,
            "full_response": full_response,
            **context
        }
        await self._write_log(f"llm_{category}", log_data)

    async def log_power_change(self, round_num: int, power_data: Dict[str, Any]):
        """
        记录国力变化

        Args:
            round_num: 轮次编号
            power_data: 国力变化数据
        """
        log_data = {
            "round_num": round_num,
            **power_data
        }
        await self._write_log("power_changes", log_data)

    async def log_order_change(self, round_num: int, order_data: Dict[str, Any]):
        """
        记录秩序变化

        Args:
            round_num: 轮次编号
            order_data: 秩序变化数据
        """
        log_data = {
            "round_num": round_num,
            **order_data
        }
        await self._write_log("order_changes", log_data)

    async def log_goal_evaluation(self, evaluation_data: Dict[str, Any]):
        """
        记录战略目标评价

        Args:
            evaluation_data: 评价数据
        """
        await self._write_log("goal_evaluations", evaluation_data)

    async def log_follower_relation(self, round_num: int, relation_data: Dict[str, Any]):
        """
        记录追随关系

        Args:
            round_num: 轮次编号
            relation_data: 追随关系数据
        """
        log_data = {
            "round_num": round_num,
            **relation_data
        }
        await self._write_log("follower_relations", log_data)

    async def log_interaction(self, round_num: int, interaction_data: Dict[str, Any]):
        """
        记录国家互动

        Args:
            round_num: 轮次编号
            interaction_data: 互动数据
        """
        log_data = {
            "round_num": round_num,
            **interaction_data
        }
        await self._write_log("interactions", log_data)

    async def close(self):
        """关闭日志文件句柄（如果需要）"""
        async with self.lock:
            self._file_handles.clear()
            logger.info(f"日志管理器已关闭: project_id={self.project_id}")
