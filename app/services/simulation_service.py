"""
仿真流程控制服务
负责仿真项目的启动、执行、暂停和重置等操作（CINC版）
"""

from typing import Optional, List, Dict, Any, Tuple
import asyncio
import math
from datetime import datetime
from sqlalchemy import select, update, delete
from loguru import logger

from app.config.database import db_config
from app.core.decision_engine import InfoPool
from app.models import SimulationProject, AgentConfig, ActionRecord, AgentPowerHistory, SimulationRound, FollowerRelation
from app.services.project_service import project_service
from app.services.agent_service import agent_service
from app.services.simulation_log_manager import SimulationLogManager


class SimulationService:
    """
    仿真流程控制服务（CINC版）

    负责仿真项目的完整生命周期管理：
    - 启动仿真
    - 执行仿真轮次
    - 暂停/继续/停止仿真
    - 重置仿真
    """

    def __init__(self):
        """初始化仿真服务"""
        self.running_simulations = {}  # 跟踪正在运行的仿真
        self.EVALUATION_INTERVAL = 10  # 评估间隔轮次（每10轮评估一次）
        self._last_update_results = []  # 保存CINC更新结果供_save_power_history使用
        self._stop_flags = {}  # 项目ID -> 是否请求停止（用于快速响应终止/重置）

    async def _get_max_concurrency(self) -> int:
        """从系统配置读取最大并发数，默认5，范围1-20。"""
        try:
            from app.services.system_service import get_system_config_service
            sys_cfg_svc = get_system_config_service()
            val = await sys_cfg_svc.get_config_value("simulation_concurrency", 5)
            max_concurrent = int(val or 5)
        except Exception:
            max_concurrent = 5
        return max(1, min(max_concurrent, 20))

    async def start_simulation(self, project_id: int) -> dict:
        """
        启动仿真项目

        检查项目状态和智能体配置，初始化仿真环境，
        并启动后台任务自动执行仿真。

        Args:
            project_id: 项目ID

        Returns:
            启动结果字典
        """
        logger.debug(f"start_simulation 被调用: project_id={project_id}")
        logger.info(f"正在启动项目 {project_id} 的仿真")

        # 获取项目信息
        project = await project_service.get_project(project_id)
        if not project:
            logger.error(f"项目 {project_id} 未找到")
            raise ValueError(f"项目 {project_id} 未找到")

        # 检查项目状态
        if project.get('status') not in ['未启动', '错误']:
            logger.warning(f"项目 {project_id} 当前状态: {project.get('status')}，无法启动")
            return {
                "project_id": project_id,
                "status": project.get('status'),
                "message": f"项目当前状态为 {project.get('status')}，无法启动"
            }

        # 检查是否有智能体
        agents = await agent_service.get_agents(project_id)
        if not agents:
            logger.error(f"项目 {project_id} 中没有智能体")
            raise ValueError(f"项目 {project_id} 中没有智能体，无法启动仿真")

        logger.info(f"项目 {project_id} 有 {len(agents)} 个智能体")

        # 更新项目状态为运行中,首次启动时记录 started_at
        async for session in db_config.get_session():
            project = await session.get(SimulationProject, project_id)
            project.status = "运行中"
            project.current_round = 1
            if project.started_at is None:
                project.started_at = datetime.now()
            project.updated_at = datetime.now()
            await session.commit()

        # 初始化日志管理器
        try:
            log_manager = SimulationLogManager(project_id)
            logger.info(f"项目 {project_id} 日志管理器初始化完成")
        except Exception as e:
            logger.error(f"日志管理器初始化失败: {e}", exc_info=True)
            raise

        # 初始化仿真环境
        try:
            await self._initialize_simulation_environment(project_id, agents)
            logger.info(f"项目 {project_id} 仿真环境初始化完成")
        except Exception as e:
            logger.error(f"仿真环境初始化失败: {e}", exc_info=True)
            # 回滚状态
            async for session in db_config.get_session():
                await session.execute(
                    update(SimulationProject)
                    .where(SimulationProject.project_id == project_id)
                    .values(status="未启动", updated_at=datetime.now())
                )
                await session.commit()
            raise

        # 启动后台任务自动执行仿真
        task = asyncio.create_task(self._run_simulation_loop(project_id, log_manager))
        self.running_simulations[project_id] = task
        logger.info(f"项目 {project_id} 后台任务已启动")

        return {
            "project_id": project_id,
            "status": "运行中",
            "message": f"仿真已启动，共 {len(agents)} 个智能体"
        }

    async def _run_simulation_loop(self, project_id: int, log_manager: SimulationLogManager) -> None:
        """
        后台循环执行仿真轮次

        自动执行仿真轮次，直到完成所有轮次或项目状态改变。

        Args:
            project_id: 项目ID
            log_manager: 日志管理器实例
        """
        logger.debug(f"仿真循环启动: project_id={project_id}")
        logger.info(f"开始项目 {project_id} 的仿真循环")

        try:
            while True:
                # 检查停止请求
                if self._stop_flags.get(project_id, False):
                    logger.info(f"项目 {project_id} 收到停止请求，退出循环")
                    break

                # 检查项目状态
                project = await project_service.get_project(project_id)
                if not project:
                    logger.error(f"项目 {project_id} 未找到，停止循环")
                    break

                status = project.get('status')
                if status != '运行中':
                    logger.info(f"项目 {project_id} 状态为 '{status}'，停止循环")
                    break

                # 执行一轮仿真 (带最多2次重试)
                max_retries = 2
                step_success = False
                result = None
                for attempt in range(max_retries + 1):
                    try:
                        result = await self.step_simulation(project_id, log_manager)
                        logger.info(
                            f"第 {result.get('round')} 轮执行完成: {result.get('message')}"
                        )
                        step_success = True
                        break
                    except Exception as e:
                        if attempt < max_retries:
                            logger.warning(
                                f"项目 {project_id} 单步执行失败 "
                                f"(尝试 {attempt + 1}/{max_retries + 1}, 原因: {e}), {2}秒后重试..."
                            )
                            await asyncio.sleep(2)
                        else:
                            logger.error(
                                f"项目 {project_id} 仿真循环错误 "
                                f"(已重试 {max_retries} 次仍失败): {e}",
                                exc_info=True
                            )
                            # 更新状态为错误
                            async for session in db_config.get_session():
                                await session.execute(
                                    update(SimulationProject)
                                    .where(SimulationProject.project_id == project_id)
                                    .values(status="错误", updated_at=datetime.now())
                                )
                                await session.commit()
                if not step_success:
                    break

                # 检查是否完成
                if result.get('status') == '已完成':
                    logger.info(f"项目 {project_id} 仿真完成")
                    break

                # 短暂休眠避免过度占用CPU
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"项目 {project_id} 仿真循环已取消")
        except Exception as e:
            logger.error(f"项目 {project_id} 仿真循环崩溃: {e}", exc_info=True)
        finally:
            # 清理任务引用和停止标志
            if project_id in self.running_simulations:
                del self.running_simulations[project_id]
            self._stop_flags.pop(project_id, None)
            logger.info(f"项目 {project_id} 仿真循环结束")

    async def step_simulation(self, project_id: int, log_manager: Optional[SimulationLogManager] = None) -> dict:
        """
        单步执行一轮仿真

        执行完整的一轮仿真流程：
        1. 创建轮次记录
        2. 执行决策生成（主动阶段）
        3. 执行决策生成（响应阶段）
        4. 更新国力
        5. 保存国力历史
        6. 执行追随投票阶段
        7. 秩序判定阶段
        8. 保存追随关系
        9. 更新轮次记录统计信息
        10. 触发战略目标评估（每10轮）
        11. 更新轮次

        Args:
            project_id: 项目ID
            log_manager: 日志管理器实例（可选；未提供则按 project_id 自建）

        Returns:
            执行结果字典
        """
        if log_manager is None:
            log_manager = SimulationLogManager(project_id)
        # 获取项目信息
        project = await project_service.get_project(project_id)
        if not project:
            logger.error(f"项目 {project_id} 未找到")
            raise ValueError(f"项目 {project_id} 未找到")

        status = project.get('status')
        current_round = project.get('current_round', 0)
        total_rounds = project.get('total_rounds', 50)

        # 检查状态
        if status != '运行中':
            logger.warning(f"项目 {project_id} 未运行 (状态: {status})")
            return {
                "project_id": project_id,
                "status": status,
                "message": f"项目当前状态为 {status}，无法执行单步"
            }

        # 检查是否已完成
        if current_round > total_rounds:
            logger.info(f"项目 {project_id} 已完成所有轮次")
            async for session in db_config.get_session():
                project = await session.get(SimulationProject, project_id)
                project.status = "已完成"
                project.completed_at = datetime.now()
                if project.started_at:
                    project.duration_seconds = int(
                        (datetime.now() - project.started_at).total_seconds()
                    )
                project.updated_at = datetime.now()
                await session.commit()
            return {
                "project_id": project_id,
                "status": "已完成",
                "message": "仿真已完成所有轮次"
            }

        logger.debug(f"第 {current_round}/{total_rounds} 轮开始执行")
        logger.info(
            f"\n{'='*58}\n"
            f"  项目 {project_id} - 第 {current_round}/{total_rounds} 轮 开始执行\n"
            f"{'='*58}"
        )

        try:
            import time as _time
            _round_start_ts = _time.time()
            # 0. 创建轮次记录
            round_id = await self._create_round_record(project_id, current_round)

            # 1. 获取所有智能体
            agents = await agent_service.get_agents(project_id)
            if not agents:
                raise ValueError(f"项目 {project_id} 中没有智能体")

            # 2. 执行决策生成（主动阶段）
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过主动决策")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            initiative_records = await self._generate_decisions(
                project_id, agents, current_round, round_id, phase="initiative", log_manager=log_manager
            )

            # 3. 执行决策生成（响应阶段）
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过响应决策")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            response_records = await self._generate_decisions(
                project_id, agents, current_round, round_id, phase="response", log_manager=log_manager
            )

            # 4. 更新国力（使用CINCPowerUpdateEngine）
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过CINC更新")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            logger.info(f"[阶段3/6] 项目{project_id} R{current_round} CINC更新中...")
            await self._update_power(project_id, agents, initiative_records + response_records)

            # 4.5 保存国力历史
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过国力历史保存")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            await self._save_power_history(project_id, round_id, current_round, agents, log_manager)

            # 5. 追随投票阶段
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过追随投票")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            logger.info(f"[阶段4/6] 项目{project_id} R{current_round} 追随投票中...")
            follower_decisions = await self._generate_follower_decisions(
                project_id, agents, round_id, current_round, log_manager
            )
            logger.info(f"  生成 {len(follower_decisions)} 条追随决策")

            # 6. 秩序判定阶段
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过秩序判定")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            logger.info(f"[阶段5/6] 项目{project_id} R{current_round} 秩序判定中...")
            order_result = await self._determine_order(
                project_id, current_round,
                initiative_records + response_records,
                follower_decisions,
                log_manager
            )
            logger.info(f"  秩序类型: {order_result.order_type.value}")

            # 7. 保存追随关系到数据库
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过保存追随关系")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            await self._save_follower_relations(project_id, round_id, current_round, follower_decisions, log_manager)

            # 8. 更新轮次记录统计信息
            if self._stop_flags.get(project_id, False):
                logger.info(f"项目 {project_id} 收到停止请求，跳过更新轮次统计")
                return {"project_id": project_id, "status": "已终止", "message": "Simulation stopped by user"}
            logger.info(f"[阶段6/6] 项目{project_id} R{current_round} 更新轮次统计")
            await self._update_round_record(project_id, current_round, initiative_records + response_records, order_result)

            # 9. 每10轮触发一次战略目标评估
            eval_message = ""
            if not self._stop_flags.get(project_id, False) and current_round % self.EVALUATION_INTERVAL == 0 and current_round > 0:
                try:
                    from app.services.goal_evaluation_service import get_goal_evaluation_service
                    evaluation_service = get_goal_evaluation_service(log_manager=log_manager)

                    await evaluation_service.evaluate_all_agents(project_id, current_round)
                    logger.info(f"第 {current_round} 轮战略目标评估完成")
                    eval_message = " (含战略目标评估)"
                except Exception as e:
                    logger.warning(
                        f"第 {current_round} 轮战略目标评估跳过 (原因: {e})",
                        exc_info=True
                    )
                    eval_message = " (评估跳过)"

            # 10. 战略关系演变评估（每轮）
            evolve_message = ""
            if not self._stop_flags.get(project_id, False):
                try:
                    from app.services.relationship_evolution_service import get_relationship_evolution_service
                    evolution_service = get_relationship_evolution_service(log_manager=log_manager)
                    changes = await evolution_service.evolve_relationships(project_id, current_round)
                    logger.info(f"第 {current_round} 轮战略关系演变完成，{len(changes)} 对关系发生变化")
                    if changes:
                        evolve_message = f" (战略关系变化: {len(changes)}对)"
                except Exception as e:
                    logger.warning(
                        f"第 {current_round} 轮战略关系演变跳过 (原因: {e})",
                        exc_info=True
                    )
                    evolve_message = " (关系演变跳过)"

            # 更新轮次
            next_round = current_round + 1
            next_status = "已完成" if next_round > total_rounds else "运行中"

            async for session in db_config.get_session():
                await session.execute(
                    update(SimulationProject)
                    .where(SimulationProject.project_id == project_id)
                    .values(
                        current_round=next_round,
                        status=next_status,
                        updated_at=datetime.now()
                    )
                )
                await session.commit()

            message = f"第 {current_round} 轮执行完成" + eval_message + evolve_message

            elapsed = _time.time() - _round_start_ts
            logger.info(
                f"\n{'='*58}\n"
                f"  项目 {project_id} - 第 {current_round}/{total_rounds} 轮 完成 (耗时 {elapsed:.1f}s)\n"
                f"  主动行为: {len(initiative_records)} | 响应行为: {len(response_records)} | "
                f"秩序: {order_result.order_type.value}\n"
                f"{'='*58}\n"
            )

            return {
                "project_id": project_id,
                "round": current_round,
                "next_round": next_round,
                "total_rounds": total_rounds,
                "status": next_status,
                "initiative_count": len(initiative_records),
                "response_count": len(response_records),
                "message": message
            }

        except Exception as e:
            logger.error(f"第 {current_round} 轮执行失败: {e}", exc_info=True)
            raise

    async def _initialize_simulation_environment(
        self, project_id: int, agents: List[Dict]
    ) -> None:
        """
        初始化仿真环境

        记录初始CINC指数信息。
        注意：战略关系已在项目创建时由 scene_service 初始化。

        Args:
            project_id: 项目ID
            agents: 智能体列表
        """
        for agent in agents:
            agent_id = agent.get('agent_id')
            agent_name = agent.get('agent_name')
            initial_power = agent.get('initial_total_power', 0)

            logger.info(f"正在初始化智能体 {agent_name} (ID: {agent_id})，初始CINC指数: {initial_power:.6f}")

    async def _create_round_record(self, project_id: int, round_num: int) -> int:
        """
        创建轮次记录并返回 round_id

        防御重复写入：若该 (project_id, round_num) 已存在则直接复用。

        Args:
            project_id: 项目ID
            round_num: 轮次号

        Returns:
            轮次ID
        """
        async for session in db_config.get_session():
            # 先检查是否已存在（防止并发/重试导致重复）
            existing = await session.execute(
                select(SimulationRound).where(
                    SimulationRound.project_id == project_id,
                    SimulationRound.round_num == round_num
                ).order_by(SimulationRound.round_id.desc()).limit(1)
            )
            existing_record = existing.scalars().first()
            if existing_record:
                return existing_record.round_id

            round_record = SimulationRound(
                project_id=project_id,
                round_num=round_num,
                total_action_count=0,
                respect_sov_action_count=0,
                respect_sov_ratio=0.0,
                has_leader="false",
                order_type="未判定"
            )
            session.add(round_record)
            await session.commit()
            await session.refresh(round_record)
            return round_record.round_id

    async def _generate_decisions(
        self, project_id: int, agents: List[Dict], round_num: int, round_id: int, phase: str, log_manager=None
    ) -> List[Dict]:
        """
        生成决策

        使用DecisionEngine（LLM驱动）生成决策。

        Args:
            project_id: 项目ID
            agents: 智能体列表
            round_num: 轮次号
            round_id: 轮次ID
            phase: 阶段（"initiative"或"response"）
            log_manager: 日志管理器实例

        Returns:
            决策记录列表
        """
        from app.core.action_manager import get_all_actions
        from app.core.decision_engine import get_decision_engine, AgentInfo, InfoPool, ActionStageEnum
        from app.core.agent_base import AgentBase

        actions = get_all_actions()
        records = []

        async for session in db_config.get_session():
            from ..services.strategic_relationship_service import StrategicRelationshipService
            relationship_service = StrategicRelationshipService(session)
            strategic_relationships = await relationship_service.get_all_agents_relationships(project_id)

            # Debug: 检查战略关系加载情况
            logger.info(f"项目 {project_id} 加载的战略关系: {strategic_relationships}")
            if strategic_relationships:
                for agent_id, relations in strategic_relationships.items():
                    logger.info(f"  智能体 {agent_id} 的关系: {relations}")
            else:
                logger.warning(f"项目 {project_id} 未加载到任何战略关系！")

        # 获取历史数据
        history_action_records = await self._get_action_history(project_id, round_num, phase)
        history_power_data = await self._get_power_history(project_id, round_num)
        last_round_order_info = await self._get_last_round_order(project_id, round_num)

        # 根据阶段筛选行为
        if phase == "initiative":
            phase_actions = [a for a in actions if a.is_initiative]
            action_stage = ActionStageEnum.INITIATIVE
        else:
            phase_actions = [a for a in actions if a.is_response]
            action_stage = ActionStageEnum.RESPONSE

        logger.info(f"阶段 {phase}: 有 {len(phase_actions)} 个行为可用")
        logger.debug(f"phase_actions IDs: {[a.action_id for a in phase_actions]}")

        # 构建InfoPool
        all_agent_info = [
            {
                'agent_id': a.get('agent_id'),
                'agent_name': a.get('agent_name'),
                'region': a.get('region'),
                'initial_total_power': a.get('initial_total_power'),
                'current_total_power': a.get('current_total_power'),
                'power_level': a.get('power_level'),
                'leader_type': a.get('leader_type'),
                'strategic_relationships': strategic_relationships.get(a.get('agent_id'), {})
            }
            for a in agents
        ]

        info_pool = InfoPool(
            all_agent_info=all_agent_info,
            history_action_records=history_action_records,
            history_power_data=history_power_data,
            last_round_order_info=last_round_order_info,
            round_num=round_num
        )

        # 获取决策引擎（带log_manager）
        decision_engine = get_decision_engine(log_manager=log_manager)

        # 读取并发配置
        try:
            from app.services.system_service import get_system_config_service
            sys_cfg_svc = get_system_config_service()
            max_concurrent = int(await sys_cfg_svc.get_config_value("simulation_concurrency", 5) or 5)
        except Exception:
            max_concurrent = 5
        max_concurrent = max(1, min(max_concurrent, 20))

        total_agents = len(agents)
        phase_label = "主动决策" if phase == "initiative" else "响应决策"
        logger.info(
            f"\n========== 第 {round_num} 轮 - {phase_label}阶段开始 "
            f"(共{total_agents}国, 并发度{max_concurrent}) =========="
        )

        semaphore = asyncio.Semaphore(max_concurrent)
        completed_counter = {"n": 0}  # 用dict使闭包可写

        async def _decide_one_agent(agent):
            """并发安全的单agent决策；失败仅记录，不影响其他agent"""
            agent_id = agent.get('agent_id')
            agent_name = agent.get('agent_name')
            local_records = []

            # 构建AgentBase（CINC版字段）
            from app.core.agent_base import AgentBase
            agent_base = AgentBase(**{
                "agent_id": agent.get('agent_id'),
                "agent_name": agent.get('agent_name'),
                "region": agent.get('region'),
                "milex": agent.get('milex', 0),
                "milper": agent.get('milper', 0),
                "irst": agent.get('irst', 0),
                "pec": agent.get('pec', 0),
                "tpop": agent.get('tpop', 0),
                "upop": agent.get('upop', 0),
                "initial_total_power": agent.get('initial_total_power'),
                "current_total_power": agent.get('current_total_power'),
                "power_level": agent.get('power_level'),
                "leader_type": agent.get('leader_type'),
            })

            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_name=agent_name,
                region=agent.get('region'),
                initial_total_power=agent.get('initial_total_power'),
                current_total_power=agent.get('current_total_power'),
                power_level=agent.get('power_level'),
                leader_type=agent.get('leader_type'),
                national_interest=agent_base.national_interest,
                strategic_relationships=strategic_relationships.get(agent_id, {}),
                cinc_year=agent.get('cinc_year'),
                allowed_actions=[{
                    'action_id': a.action_id,
                    'action_name': a.action_name,
                    'action_en_name': a.action_en_name,
                    'action_category': a.action_category,
                    'action_desc': a.action_desc,
                    'respect_sov': a.respect_sov,
                    'initiator_power_change': a.initiator_power_change,
                    'target_power_change': a.target_power_change,
                    'is_initiative': a.is_initiative,
                    'is_response': a.is_response
                } for a in phase_actions]
            )

            async with semaphore:
                try:
                    decision_result = await decision_engine.make_decision(
                        agent_info=agent_info,
                        info_pool=info_pool,
                        action_stage=action_stage
                    )

                    if decision_result.success and decision_result.decision:
                        actions_list = decision_result.decision.get('actions', [])
                        completed_counter["n"] += 1
                        progress = f"[{completed_counter['n']:>2d}/{total_agents}]"
                        action_summary = "; ".join(
                            f"{a.get('action_name','?')}->ID{a.get('target_agent_id','?')}"
                            for a in actions_list[:3]
                        )
                        if len(actions_list) > 3:
                            action_summary += f" ...等{len(actions_list)}个"
                        logger.info(
                            f"  {progress} [OK] R{round_num} {phase_label} | "
                            f"{agent_name}(ID:{agent_id}) → {action_summary}"
                        )

                        for action_data in actions_list:
                            target_id = action_data.get('target_agent_id', 0)
                            action_id = action_data.get('action_id')
                            try:
                                action_id = int(action_id)
                            except (ValueError, TypeError):
                                logger.warning(f"行为ID {action_data.get('action_id')} 格式无效，跳过")
                                continue

                            action_config = next((a for a in phase_actions if a.action_id == action_id), None)
                            if not action_config:
                                logger.warning(f"未找到行为ID {action_id} 的配置，跳过")
                                continue

                            record = {
                                "project_id": project_id,
                                "round_id": round_id,
                                "round_num": round_num,
                                "action_stage": phase,
                                "source_agent_id": agent_id,
                                "target_agent_id": target_id,
                                "action_id": action_id,
                                "action_name": action_config.action_name,
                                "action_category": action_config.action_category,
                                "respect_sov": action_config.respect_sov,
                                "initiator_power_change": action_config.initiator_power_change,
                                "target_power_change": action_config.target_power_change,
                                "decision_detail": action_data.get('cost_benefit_analysis', ''),
                                "action_content": action_data.get('action_content', '')
                            }
                            local_records.append(record)
                    else:
                        completed_counter["n"] += 1
                        progress = f"[{completed_counter['n']:>2d}/{total_agents}]"
                        logger.warning(
                            f"  {progress} [FAIL] R{round_num} {phase_label} | "
                            f"{agent_name}(ID:{agent_id}) LLM决策失败: "
                            f"{decision_result.validation_errors}"
                        )
                except Exception as e:
                    completed_counter["n"] += 1
                    progress = f"[{completed_counter['n']:>2d}/{total_agents}]"
                    logger.error(
                        f"  {progress} [FAIL] R{round_num} {phase_label} | "
                        f"{agent_name}(ID:{agent_id}) 决策异常: {e}"
                    )

            return local_records

        # 并发执行所有agent的决策
        agent_record_lists = await asyncio.gather(
            *[_decide_one_agent(agent) for agent in agents],
            return_exceptions=False
        )
        for sub_records in agent_record_lists:
            records.extend(sub_records)

        logger.info(
            f"========== 第 {round_num} 轮 - {phase_label}阶段完成 "
            f"(产生 {len(records)} 条行为记录) ==========\n"
        )

        # 后处理：行为前置条件硬性过滤（兜底，防止LLM输出不合规行为）
        filtered_records = []
        for record in records:
            action_name = record.get('action_name', '')
            source_id = record.get('source_agent_id')
            target_id = record.get('target_agent_id')

            # 获取source与target的战略关系
            source_rels = strategic_relationships.get(source_id, {})
            rel = source_rels.get(target_id, '无外交关系')

            # 规则1: 交战/使用常规军事武力 仅在冲突/战争关系下允许
            if action_name == '交战/使用常规军事武力' and rel not in ['冲突关系', '战争关系']:
                logger.warning(
                    f"[后处理过滤] 交战行为不合规: 国家{source_id}->{target_id}, "
                    f"关系='{rel}'(需要冲突/战争)，已过滤"
                )
                continue

            # 规则2: 攻击/袭击 仅在冲突/战争关系下允许
            if action_name == '攻击/袭击' and rel not in ['冲突关系', '战争关系']:
                logger.warning(
                    f"[后处理过滤] 攻击行为不合规: 国家{source_id}->{target_id}, "
                    f"关系='{rel}'(需要冲突/战争)，已过滤"
                )
                continue

            # 规则3: 胁迫/强制 需要历史铺垫
            if action_name == '胁迫/强制':
                has_prelude = any(
                    r.get('source_agent_id') == source_id
                    and r.get('target_agent_id') == target_id
                    and r.get('action_name') in ['展示军事姿态', '威胁']
                    for r in history_action_records
                )
                if not has_prelude:
                    logger.warning(
                        f"[后处理过滤] 胁迫行为不合规: 国家{source_id}->{target_id}, "
                        f"缺少展示军事姿态/威胁铺垫，已过滤"
                    )
                    continue

            filtered_records.append(record)

        if len(filtered_records) < len(records):
            logger.info(
                f"[后处理过滤] 原{len(records)}条记录，过滤后{len(filtered_records)}条，"
                f"过滤掉{len(records) - len(filtered_records)}条不合规行为"
            )
        records = filtered_records

        # 保存记录到数据库
        if records:
            async for session in db_config.get_session():
                for record in records:
                    db_record = ActionRecord(**record)
                    session.add(db_record)
                await session.commit()

        # 记录到日志文件
        if log_manager:
            await log_manager.log_interaction(round_num, {
                "project_id": project_id,
                "phase": phase,
                "interactions": records
            })

        return records

    async def _get_action_history(self, project_id: int, round_num: int, phase: str = None) -> List[Dict]:
        """
        获取历史行为记录

        Args:
            project_id: 项目ID
            round_num: 当前轮次
            phase: 当前阶段（"initiative" 或 "response"）

        Returns:
            历史行为记录列表
        """
        async for session in db_config.get_session():
            # 查询之前轮次的记录
            result = await session.execute(
                select(ActionRecord).where(
                    ActionRecord.project_id == project_id,
                    ActionRecord.round_num < round_num
                )
            )
            records = result.scalars().all()

            # 如果是响应阶段，还要包含当前轮次的主动阶段记录
            if phase == "response":
                result = await session.execute(
                    select(ActionRecord).where(
                        ActionRecord.project_id == project_id,
                        ActionRecord.round_num == round_num,
                        ActionRecord.action_stage == "initiative"
                    )
                )
                initiative_records = result.scalars().all()
                records = list(records) + list(initiative_records)

            return [
                {
                    'round_num': r.round_num,
                    'source_agent_id': r.source_agent_id,
                    'target_agent_id': r.target_agent_id,
                    'action_name': r.action_name,
                    'action_category': r.action_category,
                    'respect_sov': r.respect_sov,
                    'initiator_power_change': r.initiator_power_change,
                    'target_power_change': r.target_power_change,
                    'decision_detail': r.decision_detail,
                    'action_content': r.action_content
                }
                for r in records
            ]

    async def _get_power_history(self, project_id: int, round_num: int) -> List[Dict]:
        """
        获取历史CINC数据

        Args:
            project_id: 项目ID
            round_num: 当前轮次

        Returns:
            历史CINC数据列表
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentPowerHistory).where(
                    AgentPowerHistory.project_id == project_id,
                    AgentPowerHistory.round_num < round_num
                )
            )
            records = result.scalars().all()

            return [
                {
                    'round_num': r.round_num,
                    'agent_id': r.agent_id,
                    'round_start_power': r.round_start_power,
                    'round_end_power': r.round_end_power,
                    'round_change_value': r.round_change_value
                }
                for r in records
            ]

    async def _get_last_round_order(self, project_id: int, round_num: int) -> Dict:
        """
        获取上一轮的秩序信息

        Args:
            project_id: 项目ID
            round_num: 当前轮次

        Returns:
            秩序信息字典
        """
        if round_num == 1:
            return {
                'order_type': '未确定',
                'leader_agent_id': None,
                'leader_follower_ratio': 0.0
            }

        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationRound).where(
                    SimulationRound.project_id == project_id,
                    SimulationRound.round_num == round_num - 1
                )
            )
            round_record = result.scalar_one_or_none()

            if round_record:
                return {
                    'order_type': round_record.order_type or '未确定',
                    'leader_agent_id': round_record.leader_agent_id,
                    'leader_follower_ratio': round_record.leader_follower_ratio or 0.0
                }
            else:
                return {
                    'order_type': '未确定',
                    'leader_agent_id': None,
                    'leader_follower_ratio': 0.0
                }

    @staticmethod
    def _get_issue_context(scene_source: str, round_num: int, agents: list = None) -> str:
        """
        从历史地面真值 v2 JSON 中读取当轮的主导议题，并将所有真实国名替换为糊名。

        每轮仿真模拟3个月，历史v2数据为每轮预设了独立的主导议题描述。
        为防止智能体通过议题中的国名推断身份，所有真实国名会被替换为智能体糊名。
        """
        import json, os, re

        # Map scene_source to history file
        history_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "history"
        )
        if "1913" in scene_source or "一战" in scene_source:
            filename = "scene1_prewar_1913.json"
        elif "1938" in scene_source or "二战" in scene_source:
            filename = "scene2_prewar_1938.json"
        elif "1946" in scene_source or "冷战" in scene_source:
            filename = "scene3_prewar_1946.json"
        else:
            return ""

        try:
            filepath = os.path.join(history_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                history = json.load(f)
            rnd = history['rounds'].get(str(round_num), {})
            issue = rnd.get('dominant_issue', '')
            if not issue:
                return ""

            # Build real-name → blind-name substitution map from agents
            # country_code → real English name
            _cc_to_real = [
                (255, "Germany"), (365, "Russia"), (200, "UK"), (220, "France"),
                (300, "Austria-Hungary"), (325, "Italy"), (640, "Ottoman Empire"),
                (355, "Bulgaria"), (230, "Spain"), (211, "Belgium"), (350, "Greece"),
                (380, "Sweden"), (210, "Netherlands"), (360, "Romania"),
                (235, "Portugal"), (390, "Denmark"), (225, "Switzerland"),
                (345, "Serbia"), (385, "Norway"),
                (315, "Czechoslovakia"), (290, "Poland"), (310, "Hungary"),
                (375, "Finland"), (212, "Luxembourg"), (366, "Latvia"),
                (368, "Lithuania"), (205, "Ireland"), (365, "Estonia"),
                (339, "Albania"), (395, "Iceland"),
            ]
            name_map = {}
            if agents:
                for a in agents:
                    cc = a.get('country_code')
                    blind = a.get('agent_name', '')
                    if cc and blind:
                        for ccode, real in _cc_to_real:
                            if cc == ccode:
                                name_map[real] = blind
                                # Also map short/derived forms
                                _extras = {
                                    "UK": ["British", "Britain"],
                                    "Germany": ["German"],
                                    "Russia": ["Russian", "USSR", "Soviet", "Soviet Union"],
                                    "France": ["French"],
                                    "Italy": ["Italian"],
                                    "Ottoman Empire": ["Ottoman", "Turkey"],
                                    "Austria-Hungary": ["A-H"],
                                    "Serbia": ["Yugoslavia"],
                                    "Czechoslovakia": ["Czech"],
                                    "Finland": ["Finnish"],
                                }
                                for extra in _extras.get(real, []):
                                    name_map[extra] = blind
                                # Don't break — same ccode can map to multiple real names
                                # (e.g. ccode 345 → Serbia AND Yugoslavia;
                                #        ccode 640 → Ottoman Empire AND Turkey)

            # Add organization/institution anonymization
            _org_map = [
                ("NATO", "西方军事同盟"),
                ("Warsaw Pact", "东方军事同盟"),
                ("COMECON", "东方经济组织"),
                ("Cominform", "东方政治组织"),
                ("ECSC", "欧洲经济合作组织"),
                ("EEC", "欧洲经济共同体"),
                ("EURATOM", "欧洲原子能组织"),
                ("WEU", "西欧防务组织"),
                ("FRG", "西方阵营德国"),
                ("GDR", "东方阵营德国"),
                ("UN", "国际组织"),
            ]
            for real, blind in _org_map:
                name_map[real] = blind

            # Apply substitutions (longest first)
            issue_anon = issue
            for real_name in sorted(name_map.keys(), key=len, reverse=True):
                issue_anon = issue_anon.replace(real_name, name_map[real_name])

            # Blind faction/camp names
            _faction_map = [
                ("Entente", "协约阵营"),
                ("Allies", "盟军阵营"),
                ("Central Powers", "同盟阵营"),
                ("Axis", "轴心阵营"),
                ("NATO", "西方军事同盟"),
                ("Warsaw Pact", "东方军事同盟"),
                ("Little Entente", "区域性同盟"),
                ("Triple Alliance", "三国军事同盟"),
                ("Franco-Russian Alliance", "双边军事同盟"),
                ("Franco-Russian", "双边军事同盟"),
                ("Anglo-German", "双边"),
                ("Greco-Turkish", "双边"),
                ("Polish-Soviet", "双边"),
                ("Tito-Stalin", "双边"),
                ("Molotov-Ribbentrop", "双边"),
                ("Nazi-Soviet", "双边"),
                ("Anglo-Soviet", "双边"),
                ("Anglo-Polish", "双边"),
            ]
            for real, blind in _faction_map:
                issue_anon = issue_anon.replace(real, blind)

            return (
                "【当前轮次议题背景】\n"
                f"当前为第{round_num}轮（每轮=3个月）。\n"
                f"本轮主导国际议题：{issue_anon}\n"
                "追随某国意味着在这一议题上与该国协调立场，而非结成战略同盟。"
                "你的追随决策应基于你在这轮议题上的国家利益。"
            )
        except Exception:
            pass
        return ""

    async def _build_complete_info_pool(
        self,
        project_id: int,
        agents: List[Dict],
        round_num: int
    ) -> InfoPool:
        """
        构建完整的InfoPool，包含所有历史数据和战略关系

        Args:
            project_id: 项目ID
            agents: 所有智能体列表
            round_num: 当前轮次号

        Returns:
            完整的InfoPool对象
        """

        # 获取战略关系
        async for session in db_config.get_session():
            from ..services.strategic_relationship_service import StrategicRelationshipService
            relationship_service = StrategicRelationshipService(session)
            strategic_relationships = await relationship_service.get_all_agents_relationships(project_id)

        # 获取历史数据
        history_action_records = await self._get_action_history(project_id, round_num, "initiative")
        history_power_data = await self._get_power_history(project_id, round_num)
        last_round_order_info = await self._get_last_round_order(project_id, round_num)

        # 获取当前议题背景
        project = await project_service.get_project(project_id)
        scene_source = project.get('scene_source', '') if project else ''
        current_issue = self._get_issue_context(scene_source, round_num, agents)

        # 构建完整的智能体信息（包含战略关系）
        all_agent_info = [
            {
                'agent_id': a.get('agent_id'),
                'agent_name': a.get('agent_name'),
                'region': a.get('region'),
                'initial_total_power': a.get('initial_total_power'),
                'current_total_power': a.get('current_total_power'),
                'power_level': a.get('power_level'),
                'leader_type': a.get('leader_type'),
                'strategic_relationships': strategic_relationships.get(a.get('agent_id'), {})
            }
            for a in agents
        ]

        # 返回完整的InfoPool
        return InfoPool(
            all_agent_info=all_agent_info,
            history_action_records=history_action_records,
            history_power_data=history_power_data,
            last_round_order_info=last_round_order_info,
            round_num=round_num,
            current_issue=current_issue
        )

    async def _update_power(
        self, project_id: int, agents: List[Dict], records: List[Dict]
    ) -> None:
        """
        更新CINC（使用CINCPowerUpdateEngine）

        基于行为记录更新每个智能体的6项底层指标，
        然后全局重算CINC和层级。

        Args:
            project_id: 项目ID
            agents: 智能体列表（dict列表）
            records: 行为记录列表
        """
        from app.core.cinc_power_update import CINCPowerUpdateEngine, load_scale_factors_from_config

        # 从配置读取可选的自定义 scale factors
        scale_factors = await load_scale_factors_from_config()
        engine = CINCPowerUpdateEngine(scale_factors=scale_factors)

        # agents 是 dict 列表
        agent_dicts = [
            {
                "agent_id": a["agent_id"],
                "agent_name": a["agent_name"],
                "milex": a.get("milex", 0),
                "milper": a.get("milper", 0),
                "irst": a.get("irst", 0),
                "pec": a.get("pec", 0),
                "tpop": a.get("tpop", 0),
                "upop": a.get("upop", 0),
                "cinc": a.get("current_total_power", 0),
                "power_level": a.get("power_level", "小国"),
            }
            for a in agents
        ]
        engine.load_agents(agent_dicts)

        # 获取当前轮次
        current_round = 0
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationProject).where(SimulationProject.project_id == project_id)
            )
            project = result.scalar_one_or_none()
            if project:
                current_round = project.current_round or 0
        engine.set_round(current_round)

        # 转换records为简单dict并更新
        results = engine.update_round(records)

        # 保存engine结果供_save_power_history使用
        self._last_update_results = results

        # 将结果写回数据库（批量更新，减少事务开销）
        async for session in db_config.get_session():
            for r in results:
                state = engine.get_agent_state(r.agent_id)
                await session.execute(
                    update(AgentConfig)
                    .where(AgentConfig.agent_id == r.agent_id)
                    .values(
                        milex=state["milex"], milper=state["milper"], irst=state["irst"],
                        pec=state["pec"], tpop=state["tpop"], upop=state["upop"],
                        current_total_power=r.end_cinc,
                        power_level=r.new_power_level.value if hasattr(r.new_power_level, 'value') else r.new_power_level,
                        updated_at=datetime.now()
                    )
                )
            await session.commit()

        # 更新内存中的agent dict（这样 _save_power_history 能用到新值）
        for r in results:
            state = engine.get_agent_state(r.agent_id)
            for a in agents:
                if a["agent_id"] == r.agent_id:
                    a["milex"] = state["milex"]
                    a["milper"] = state["milper"]
                    a["irst"] = state["irst"]
                    a["pec"] = state["pec"]
                    a["tpop"] = state["tpop"]
                    a["upop"] = state["upop"]
                    a["current_total_power"] = r.end_cinc
                    a["power_level"] = r.new_power_level.value if hasattr(r.new_power_level, 'value') else r.new_power_level

    async def _save_power_history(
        self, project_id: int, round_id: int, round_num: int, agents: List[Dict], log_manager=None
    ) -> None:
        """
        保存CINC历史到 AgentPowerHistory 表

        Args:
            project_id: 项目ID
            round_id: 轮次ID
            round_num: 轮次号
            agents: 智能体列表
            log_manager: 日志管理器实例
        """
        async for session in db_config.get_session():
            # 先获取本轮开始时的CINC（上一轮结束时的CINC）
            if round_num > 1:
                result = await session.execute(
                    select(AgentPowerHistory)
                    .where(AgentPowerHistory.project_id == project_id)
                    .where(AgentPowerHistory.round_num == round_num - 1)
                )
                last_round_histories = result.scalars().all()
                last_round_powers = {h.agent_id: h.round_end_power for h in last_round_histories}
            else:
                # 第一轮使用初始CINC
                last_round_powers = {a['agent_id']: a.get('initial_total_power', 0) for a in agents}

            # 保存本轮CINC历史
            for agent in agents:
                agent_id = agent.get('agent_id')
                start_power = last_round_powers.get(agent_id, 0)
                end_power = agent.get('current_total_power', 0)
                change_value = end_power - start_power
                # 对数变化率（百分点），避免极小起点放大效应
                if start_power > 0 and end_power > 0:
                    change_rate = math.log(end_power / start_power) * 100.0
                else:
                    change_rate = 0.0

                history_record = AgentPowerHistory(
                    project_id=project_id,
                    agent_id=agent_id,
                    round_id=round_id,
                    round_num=round_num,
                    round_start_power=start_power,
                    round_end_power=end_power,
                    round_change_value=change_value,
                    round_change_rate=change_rate
                )
                session.add(history_record)

            await session.commit()

        logger.info(f"第 {round_num} 轮CINC历史已保存，共 {len(agents)} 个智能体")

        # 记录到日志文件（包含indicator_changes和passive_change）
        if log_manager:
            power_changes = []
            for agent in agents:
                agent_id = agent.get('agent_id')
                start_power = last_round_powers.get(agent_id, 0)
                end_power = agent.get('current_total_power', 0)
                change_value = end_power - start_power
                # 对数变化率（百分点），避免极小起点放大效应
                if start_power > 0 and end_power > 0:
                    change_rate = math.log(end_power / start_power) * 100.0
                else:
                    change_rate = 0.0

                # 从engine结果中获取indicator_changes和passive_change
                indicator_changes = None
                passive_change = False
                for r in getattr(self, '_last_update_results', []):
                    if r.agent_id == agent_id:
                        indicator_changes = r.indicator_changes.to_dict() if hasattr(r.indicator_changes, 'to_dict') else r.indicator_changes
                        passive_change = r.passive_change
                        break

                power_changes.append({
                    "agent_id": agent_id,
                    "agent_name": agent.get('agent_name'),
                    "start_power": start_power,
                    "end_power": end_power,
                    "change_value": change_value,
                    "change_rate": change_rate,
                    "indicator_changes": indicator_changes,
                    "passive_change": passive_change
                })
            await log_manager.log_power_change(round_num, {"power_changes": power_changes})

    async def _generate_follower_decisions(
        self, project_id: int, agents: List[Dict], round_id: int, round_num: int, log_manager=None
    ) -> Dict[int, Optional[int]]:
        """
        生成LLM驱动的追随投票决策（并发执行）

        追随机制设计：
        - 追随是被动的：所有国家均可被追随，无需参选
        - 所有国家（包括大国和小国）均可成为被追随者
        - 各国通过LLM决策选择追随谁或保持中立

        Args:
            project_id: 项目ID
            agents: 所有智能体列表
            round_id: 轮次ID
            round_num: 轮次号
            log_manager: 日志管理器实例

        Returns:
            追随关系字典 {follower_id: leader_id}
        """
        from app.services.llm_service import get_llm_service
        from app.core.prompt_templates import PromptTemplates
        from app.core.decision_engine import get_decision_engine

        llm_service = get_llm_service()
        decision_engine = get_decision_engine(log_manager=log_manager)
        max_concurrent = await self._get_max_concurrency()

        # 构建完整的InfoPool（包含战略关系、历史数据等）
        info_pool = await self._build_complete_info_pool(project_id, agents, round_num)

        # 格式化信息池为字符串
        formatted_info_pool = {
            'all_agent_info': decision_engine._format_agents_for_prompt(info_pool.all_agent_info),
            'history_action_records': decision_engine._format_history_for_prompt(info_pool.history_action_records),
            'history_power_data': decision_engine._format_power_data_for_prompt(info_pool.history_power_data),
            'last_round_order_info': info_pool.last_round_order_info
        }

        # 预构建：每个agent的战略关系查表（自我视角的关系总览所需）
        relationships_lookup: Dict[int, Dict[int, str]] = {
            a.get('agent_id'): (a.get('strategic_relationships') or {})
            for a in info_pool.all_agent_info
        }

        def _build_personal_summary_for(agent: Dict) -> str:
            """为单个 agent 构建【你的战略关系总览】块。"""
            return PromptTemplates.build_personal_relations_summary(
                voter_id=agent.get('agent_id'),
                voter_name=agent.get('agent_name', '?'),
                voter_power=agent.get('current_total_power', 0) or 0,
                voter_level=agent.get('power_level', '?'),
                voter_leader_type=agent.get('leader_type'),
                voter_relationships=relationships_lookup.get(agent.get('agent_id'), {}),
                all_agent_info=info_pool.all_agent_info,
            )

        # 所有国家均可被追随（被动追随，无需参选）
        all_targets = agents

        # 构建所有可追随目标的信息字符串
        all_targets_info = "\n".join([
            f"  ID:{a['agent_id']} 名称:{a['agent_name']} "
            f"CINC:{a['current_total_power']:.6f} 层级:{a.get('power_level', '?')}"
            for a in all_targets
        ])

        # ========== 追随投票决策（单阶段，所有国家并发） ==========
        semaphore = asyncio.Semaphore(max_concurrent)
        total_agents = len(agents)
        completed_counter = {"n": 0}

        async def _decide_vote(agent: Dict) -> Tuple[int, Optional[int], str]:
            """返回 (agent_id, follower_id, reason)"""
            agent_name = agent.get('agent_name')
            agent_id = agent.get('agent_id')
            power_level = agent.get('power_level')

            system_prompt = PromptTemplates.build_follower_system_prompt(
                agent_name=agent_name,
                current_total_power=agent.get('current_total_power', 0),
                power_level=power_level,
                leader_type=agent.get('leader_type', '未定义'),
                cinc_year=agent.get('cinc_year'),
                initial_total_power=agent.get('initial_total_power', 0)
            )
            # 所有国家评估（按当前voter视角预先核对战略关系+双向互动）
            voter_relationships = relationships_lookup.get(agent_id, {})
            candidates_evaluation = PromptTemplates.build_candidates_evaluation(
                voter_id=agent_id,
                voter_relationships=voter_relationships,
                candidates=all_targets,
                history_action_records=info_pool.history_action_records,
            )
            user_prompt = PromptTemplates.build_follower_user_prompt(
                info_pool=formatted_info_pool,
                decision_type='vote',
                leader_candidates_info=all_targets_info,
                personal_summary=_build_personal_summary_for(agent),
                candidates_evaluation=candidates_evaluation,
                current_issue=info_pool.current_issue,
            )

            async with semaphore:
                try:
                    response = await llm_service.call_llm_async(
                        user_prompt,
                        system_prompt=system_prompt,
                        log_manager=log_manager,
                        log_category="following",
                        round_num=round_num,
                        agent_id=agent_id,
                        agent_name=agent_name,
                        decision_type="follower_vote"
                    )
                    follower_id = response.get('follower_agent_id')
                    follower_name = response.get('follower_agent_name', '中立')
                    reason = response.get('reason', '')

                    completed_counter["n"] += 1
                    progress = f"[{completed_counter['n']:>2d}/{total_agents}]"

                    # 验证follower_id是否为有效目标（不能追随自己）
                    valid_ids = {a['agent_id'] for a in all_targets}
                    if follower_id and follower_id != agent_id and follower_id in valid_ids:
                        logger.info(
                            f"  {progress} {agent_name}(ID:{agent_id}) -> "
                            f"追随 {follower_name}(ID:{follower_id})"
                        )
                        return agent_id, follower_id, reason
                    else:
                        logger.info(
                            f"  {progress} {agent_name}(ID:{agent_id}) -> 中立"
                        )
                        return agent_id, None, reason
                except Exception as e:
                    completed_counter["n"] += 1
                    progress = f"[{completed_counter['n']:>2d}/{total_agents}]"
                    logger.error(
                        f"  {progress} [FAIL] {agent_name}(ID:{agent_id}): {e}"
                    )
                    return agent_id, None, str(e)

        logger.info(
            f"========== 第 {round_num} 轮 - 追随投票开始 "
            f"(共{total_agents}国, 并发度{max_concurrent}) =========="
        )
        vote_results = await asyncio.gather(
            *[_decide_vote(agent) for agent in agents],
            return_exceptions=True
        )

        follower_decisions = {}
        for result in vote_results:
            if isinstance(result, Exception):
                continue
            agent_id, follower_id, _ = result
            follower_decisions[agent_id] = follower_id

        # ========== 后处理：修复互相追随闭环 ==========
        # 如果A追随B且B追随A，让实力更弱的一方变为中立（强者更有领导资格）
        agent_power_map = {
            a.get('agent_id'): a.get('current_total_power', 0) or 0
            for a in agents
        }
        mutual_pairs = []
        for agent_id, leader_id in list(follower_decisions.items()):
            if leader_id and follower_decisions.get(leader_id) == agent_id:
                pair = tuple(sorted([agent_id, leader_id]))
                if pair not in mutual_pairs:
                    mutual_pairs.append(pair)
                    a_power = agent_power_map.get(agent_id, 0)
                    b_power = agent_power_map.get(leader_id, 0)
                    if a_power >= b_power:
                        # agent_id更强，让leader_id(弱者)变为中立
                        follower_decisions[leader_id] = None
                        logger.warning(
                            f"[追随修复] 解除互相追随: {leader_id} 不再追随 {agent_id} "
                            f"({leader_id}实力更弱/b_power={b_power:.4f})"
                        )
                    else:
                        # leader_id更强，让agent_id(弱者)变为中立
                        follower_decisions[agent_id] = None
                        logger.warning(
                            f"[追随修复] 解除互相追随: {agent_id} 不再追随 {leader_id} "
                            f"({agent_id}实力更弱/a_power={a_power:.4f})"
                        )

        # ========== 后处理：大国/超级大国独立性保障 ==========
        # 大国和超级大国作为体系领导者，应始终保持独立决策，不追随其他国家
        # 这符合国际关系理论中"极"的定义：大国是被追随者，而非追随者
        great_power_count = 0
        for agent in agents:
            agent_id = agent.get('agent_id')
            power_level = agent.get('power_level', '')
            # 大国或超级大国应保持独立
            if power_level in ('大国', '超级大国') and follower_decisions.get(agent_id) is not None:
                old_leader = follower_decisions[agent_id]
                follower_decisions[agent_id] = None
                great_power_count += 1
                logger.info(
                    f"[大国独立] {agent.get('agent_name')}(ID:{agent_id}) "
                    f"实力层级={power_level}, 不应追随, 已强制设为中立"
                )
        if great_power_count > 0:
            logger.warning(f"[大国独立] 本轮共修正 {great_power_count} 个大国的追随决策为中立")

        # 汇总统计
        total_following = sum(1 for v in follower_decisions.values() if v is not None)
        total_neutral = sum(1 for v in follower_decisions.values() if v is None)
        leader_ids = set(v for v in follower_decisions.values() if v is not None)
        leader_names = []
        agent_name_map = {a.get('agent_id'): a.get('agent_name', '?') for a in agents}
        for lid in leader_ids:
            followers_of_lid = sum(1 for v in follower_decisions.values() if v == lid)
            leader_names.append(f"{agent_name_map.get(lid, '?')}(ID:{lid}):{followers_of_lid}追随")

        logger.info(
            f"========== 第 {round_num} 轮 - 追随决策完成 ==========\n"
            f"  追随: {total_following}国 | 中立: {total_neutral}国\n"
            f"  被追随者分布: {leader_names if leader_names else '无'}\n"
            f"====================================================="
        )
        return follower_decisions

    async def _save_follower_relations(
        self,
        project_id: int,
        round_id: int,
        round_num: int,
        follower_decisions: Dict[int, Optional[int]],
        log_manager=None
    ) -> None:
        """
        保存追随关系到数据库

        Args:
            project_id: 项目ID
            round_id: 轮次ID
            round_num: 轮次号
            follower_decisions: 追随决策
            log_manager: 日志管理器实例
        """
        async for session in db_config.get_session():
            for follower_id, leader_id in follower_decisions.items():
                relation = FollowerRelation(
                    project_id=project_id,
                    round_id=round_id,
                    round_num=round_num,
                    follower_agent_id=follower_id,
                    leader_agent_id=leader_id
                )
                session.add(relation)
            await session.commit()

        logger.info(f"已保存 {len(follower_decisions)} 条追随关系")

        # 记录到日志文件
        if log_manager:
            await log_manager.log_follower_relation(round_num, {
                "project_id": project_id,
                "follower_relations": list(follower_decisions.items())
            })

    async def _determine_order(
        self,
        project_id: int,
        round_num: int,
        action_records: List[Dict],
        follower_decisions: Dict[int, Optional[int]],
        log_manager=None
    ):
        """
        确定国际秩序

        Args:
            project_id: 项目ID
            round_num: 轮次号
            action_records: 所有行为记录
            follower_decisions: 追随决策
            log_manager: 日志管理器实例

        Returns:
            秩序判定结果
        """
        from app.core.order_determination import OrderDeterminationEngine
        from app.core.agent_base import PowerLevelEnum

        # 1. 创建OrderDeterminationEngine
        engine = OrderDeterminationEngine()

        # 2. 加载所有智能体到引擎（CINC版字段）
        agents = await agent_service.get_agents(project_id)
        engine_agents = []
        for agent in agents:
            from app.core.agent_base import AgentBase
            engine_agent = AgentBase(
                agent_id=agent.get('agent_id'),
                agent_name=agent.get('agent_name'),
                region=agent.get('region'),
                milex=agent.get('milex', 0),
                milper=agent.get('milper', 0),
                irst=agent.get('irst', 0),
                pec=agent.get('pec', 0),
                tpop=agent.get('tpop', 0),
                upop=agent.get('upop', 0),
                initial_total_power=agent.get('initial_total_power', 0),
                current_total_power=agent.get('current_total_power', 0),
                power_level=agent.get('power_level'),
                leader_type=agent.get('leader_type'),
            )
            engine_agents.append(engine_agent)

        engine.load_agents(engine_agents)
        engine.set_round(round_num)

        # 3. 转换action_records为引擎需要的格式
        engine_action_records = []
        for record in action_records:
            ar = ActionRecord(
                round_num=round_num,
                action_stage=record.get('action_stage'),
                source_agent_id=record.get('source_agent_id'),
                target_agent_id=record.get('target_agent_id'),
                action_id=record.get('action_id'),
                action_category=record.get('action_category'),
                action_name=record.get('action_name'),
                respect_sov=record.get('respect_sov'),
                initiator_power_change=record.get('initiator_power_change', 0),
                target_power_change=record.get('target_power_change', 0)
            )
            engine_action_records.append(ar)

        # 4. 执行秩序判定
        result = engine.determine_order(engine_action_records, follower_decisions)

        logger.info(
            f"秩序判定完成: {result.order_type.value}, "
            f"尊重主权率={result.respect_sov_ratio:.2%}, "
            f"有领导={result.has_leader}"
        )

        # 记录秩序变更到日志文件
        if log_manager:
            await log_manager.log_order_change(round_num, {
                "project_id": project_id,
                "order_type": result.order_type.value,
                "respect_sov_ratio": result.respect_sov_ratio,
                "respect_sov_action_count": result.respect_sov_action_count,
                "has_leader": result.has_leader,
                "leader_agent_id": result.leader_agent_id,
                "leader_follower_ratio": result.leader_follower_ratio
            })

        return result

    async def _update_round_record(
        self,
        project_id: int,
        round_num: int,
        records: List[Dict],
        order_result=None
    ) -> None:
        """
        更新轮次记录的统计信息

        Args:
            project_id: 项目ID
            round_num: 轮次号
            records: 行为记录列表
            order_result: 秩序判定结果
        """
        if order_result:
            # 使用秩序判定结果
            total_actions = len(records)
            respect_sov_count = order_result.respect_sov_action_count
            respect_sov_ratio = order_result.respect_sov_ratio
            has_leader = "true" if order_result.has_leader else "false"
            leader_agent_id = order_result.leader_agent_id
            leader_follower_ratio = order_result.leader_follower_ratio
            order_type = order_result.order_type.value
        else:
            # 回退到默认计算
            total_actions = len(records)
            respect_sov_count = sum(1 for r in records if r.get('respect_sov'))
            respect_sov_ratio = respect_sov_count / total_actions if total_actions > 0 else 0.0
            has_leader = "false"
            leader_agent_id = None
            leader_follower_ratio = 0.0
            order_type = "未判定"

        # 更新轮次记录
        async for session in db_config.get_session():
            await session.execute(
                update(SimulationRound)
                .where(SimulationRound.project_id == project_id)
                .where(SimulationRound.round_num == round_num)
                .values(
                    total_action_count=total_actions,
                    respect_sov_action_count=respect_sov_count,
                    respect_sov_ratio=respect_sov_ratio,
                    has_leader=has_leader,
                    leader_agent_id=leader_agent_id,
                    leader_follower_ratio=leader_follower_ratio,
                    order_type=order_type
                )
            )
            await session.commit()

    async def pause_simulation(self, project_id: int) -> dict:
        """
        暂停仿真

        Args:
            project_id: 项目ID

        Returns:
            暂停结果字典
        """
        logger.info(f"正在暂停项目 {project_id} 仿真")

        # 设置停止标志，让循环自然退出
        self._stop_flags[project_id] = True

        if project_id in self.running_simulations:
            # 取消正在运行的任务
            task = self.running_simulations[project_id]
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=5.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
            if project_id in self.running_simulations:
                del self.running_simulations[project_id]

        # 清理停止标志
        self._stop_flags.pop(project_id, None)

        # 更新状态
        async for session in db_config.get_session():
            await session.execute(
                update(SimulationProject)
                .where(SimulationProject.project_id == project_id)
                .values(status="暂停", updated_at=datetime.now())
            )
            await session.commit()

        return {
            "project_id": project_id,
            "status": "暂停",
            "message": "Simulation paused"
        }

    async def resume_simulation(self, project_id: int) -> dict:
        """
        继续仿真

        Args:
            project_id: 项目ID

        Returns:
            继续结果字典
        """
        logger.info(f"正在继续项目 {project_id} 仿真")

        # 更新状态
        async for session in db_config.get_session():
            await session.execute(
                update(SimulationProject)
                .where(SimulationProject.project_id == project_id)
                .values(status="运行中", updated_at=datetime.now())
            )
            await session.commit()

        # 重新启动后台任务
        if project_id not in self.running_simulations:
            log_manager = SimulationLogManager(project_id)
            task = asyncio.create_task(self._run_simulation_loop(project_id, log_manager))
            self.running_simulations[project_id] = task
            logger.info(f"项目 {project_id} 后台任务已重新启动")

        return {
            "project_id": project_id,
            "status": "运行中",
            "message": "Simulation resumed"
        }

    async def stop_simulation(self, project_id: int) -> dict:
        """
        终止仿真

        Args:
            project_id: 项目ID

        Returns:
            终止结果字典
        """
        logger.info(f"正在停止项目 {project_id} 仿真")

        self._stop_flags[project_id] = True

        if project_id in self.running_simulations:
            task = self.running_simulations[project_id]
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=120.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass

        # 更新状态并记录终止时间
        async for session in db_config.get_session():
            project = await session.get(SimulationProject, project_id)
            project.status = "已终止"
            project.completed_at = datetime.now()
            if project.started_at:
                project.duration_seconds = int(
                    (datetime.now() - project.started_at).total_seconds()
                )
            project.updated_at = datetime.now()
            await session.commit()

        self._stop_flags.pop(project_id, None)

        return {
            "project_id": project_id,
            "status": "已终止",
            "message": "Simulation stopped"
        }

    async def reset_simulation(self, project_id: int) -> dict:
        """
        重置仿真

        将仿真状态重置到初始状态。

        Args:
            project_id: 项目ID

        Returns:
            重置结果字典
        """
        logger.info(f"正在重置项目 {project_id} 仿真")

        # 先停止正在运行的仿真
        if project_id in self.running_simulations:
            self._stop_flags[project_id] = True
            task = self.running_simulations[project_id]
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=120.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass

        # 重置所有智能体的当前CINC到初始值 + 批量清空运行数据
        async for session in db_config.get_session():
            # 重置智能体CINC
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = result.scalars().all()
            for agent in agents:
                agent.current_total_power = agent.initial_total_power
                agent.updated_at = datetime.now()

            # 批量删除运行数据（单条SQL代替逐行SELECT+DELETE）
            await session.execute(delete(ActionRecord).where(ActionRecord.project_id == project_id))
            await session.execute(delete(FollowerRelation).where(FollowerRelation.project_id == project_id))
            await session.execute(delete(AgentPowerHistory).where(AgentPowerHistory.project_id == project_id))
            await session.execute(delete(SimulationRound).where(SimulationRound.project_id == project_id))

        # 注意：不重置战略关系 - 战略关系属于项目配置（用户/场景预设的初始关系），
        # 不属于运行数据。重置仿真只应清除运行数据（轮次/行为/追随关系/国力历史/CINC变化），
        # 保留项目的初始配置以便重新运行。
        # 如果用户需要重置关系，可单独调用 /strategic-relationships/{project_id}/initialize
        logger.info(f"项目 {project_id} 战略关系已保留（reset只清除运行数据）")

        # 更新项目状态并清空时间戳
        async for session in db_config.get_session():
            project = await session.get(SimulationProject, project_id)
            project.status = "未启动"
            project.current_round = 0
            project.started_at = None
            project.completed_at = None
            project.duration_seconds = None
            project.updated_at = datetime.now()
            await session.commit()

        self._stop_flags.pop(project_id, None)

        return {
            "project_id": project_id,
            "status": "未启动",
            "message": "Simulation reset"
        }


# 单例实例
simulation_service = SimulationService()
