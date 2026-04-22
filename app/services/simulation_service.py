"""
仿真流程控制服务
负责仿真项目的启动、执行、暂停和重置等操作
"""

from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime
from sqlalchemy import select, update
from loguru import logger

from app.config.database import db_config
from app.models import SimulationProject, AgentConfig, ActionRecord, AgentPowerHistory, SimulationRound, FollowerRelation
from app.services.project_service import project_service
from app.services.agent_service import agent_service
from app.services.simulation_log_manager import SimulationLogManager


class SimulationService:
    """
    仿真流程控制服务

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

        # 更新项目状态为运行中
        async for session in db_config.get_session():
            await session.execute(
                update(SimulationProject)
                .where(SimulationProject.project_id == project_id)
                .values(
                    status="运行中",
                    current_round=1,
                    updated_at=datetime.now()
                )
            )
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
        logger.info(f"开始项目 {project_id} 的仿真循环")

        try:
            while True:
                # 检查项目状态
                project = await project_service.get_project(project_id)
                if not project:
                    logger.error(f"项目 {project_id} 未找到，停止循环")
                    break

                status = project.get('status')
                if status != '运行中':
                    logger.info(f"项目 {project_id} 状态为 '{status}'，停止循环")
                    break

                # 执行一轮仿真
                try:
                    result = await self.step_simulation(project_id, log_manager)
                    logger.info(f"第 {result.get('round')} 轮执行完成: {result.get('message')}")
                except Exception as e:
                    logger.error(f"项目 {project_id} 仿真循环错误: {e}", exc_info=True)
                    # 更新状态为错误
                    async for session in db_config.get_session():
                        await session.execute(
                            update(SimulationProject)
                            .where(SimulationProject.project_id == project_id)
                            .values(status="错误", updated_at=datetime.now())
                        )
                        await session.commit()
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
            # 清理任务引用
            if project_id in self.running_simulations:
                del self.running_simulations[project_id]
            logger.info(f"项目 {project_id} 仿真循环结束")

    async def step_simulation(self, project_id: int, log_manager: SimulationLogManager) -> dict:
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
            log_manager: 日志管理器实例

        Returns:
            执行结果字典
        """
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
                await session.execute(
                    update(SimulationProject)
                    .where(SimulationProject.project_id == project_id)
                    .values(status="已完成", updated_at=datetime.now())
                )
                await session.commit()
            return {
                "project_id": project_id,
                "status": "已完成",
                "message": "仿真已完成所有轮次"
            }

        logger.info(f"正在执行项目 {project_id} 第 {current_round}/{total_rounds} 轮")

        try:
            # 0. 创建轮次记录
            logger.info(f"创建第 {current_round} 轮记录")
            round_id = await self._create_round_record(project_id, current_round)

            # 1. 获取所有智能体
            agents = await agent_service.get_agents(project_id)
            if not agents:
                raise ValueError(f"项目 {project_id} 中没有智能体")

            # 2. 执行决策生成（主动阶段）
            logger.info(f"阶段 1: 生成第 {current_round} 轮主动决策")
            initiative_records = await self._generate_decisions(
                project_id, agents, current_round, round_id, phase="initiative", log_manager=log_manager
            )
            logger.info(f"生成了 {len(initiative_records)} 条主动决策记录")

            # 3. 执行决策生成（响应阶段）
            logger.info(f"阶段 2: 生成第 {current_round} 轮响应决策")
            response_records = await self._generate_decisions(
                project_id, agents, current_round, round_id, phase="response", log_manager=log_manager
            )
            logger.info(f"生成了 {len(response_records)} 条响应决策记录")

            # 4. 更新国力
            logger.info(f"阶段 3: 更新第 {current_round} 轮国力")
            await self._update_power(project_id, agents, initiative_records + response_records)

            # 4.5 保存国力历史
            logger.info(f"阶段 3.5: 保存第 {current_round} 轮国力历史")
            await self._save_power_history(project_id, round_id, current_round, agents, log_manager)

            # 5. 追随投票阶段
            logger.info(f"阶段 4: 生成第 {current_round} 轮追随决策")
            follower_decisions = await self._generate_follower_decisions(
                project_id, agents, round_id, current_round, log_manager
            )
            logger.info(f"生成了 {len(follower_decisions)} 条追随决策")

            # 6. 秩序判定阶段
            logger.info(f"阶段 5: 判定第 {current_round} 轮秩序")
            order_result = await self._determine_order(
                project_id, current_round,
                initiative_records + response_records,
                follower_decisions,
                log_manager
            )
            logger.info(f"秩序类型: {order_result.order_type.value}")

            # 7. 保存追随关系到数据库
            await self._save_follower_relations(project_id, round_id, current_round, follower_decisions, log_manager)

            # 8. 更新轮次记录统计信息
            logger.info(f"阶段 6: 更新第 {current_round} 轮记录")
            await self._update_round_record(project_id, current_round, initiative_records + response_records, order_result)

            # 9. 每10轮触发一次战略目标评估
            eval_message = ""
            if current_round % self.EVALUATION_INTERVAL == 0 and current_round > 0:
                try:
                    from app.services.goal_evaluation_service import get_goal_evaluation_service
                    evaluation_service = get_goal_evaluation_service(log_manager=log_manager)

                    await evaluation_service.evaluate_all_agents(project_id, current_round)
                    logger.info(f"第 {current_round} 轮战略目标评估完成")
                    eval_message = " (含战略目标评估)"
                except Exception as e:
                    logger.error(f"第 {current_round} 轮战略目标评估失败: {e}", exc_info=True)
                    eval_message = " (评估失败)"

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

            message = f"第 {current_round} 轮执行完成" + eval_message

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

        记录初始国力信息，初始化战略关系。

        Args:
            project_id: 项目ID
            agents: 智能体列表
        """
        for agent in agents:
            agent_id = agent.get('agent_id')
            agent_name = agent.get('agent_name')
            initial_power = agent.get('initial_total_power', 0)

            logger.info(f"正在初始化智能体 {agent_name} (ID: {agent_id})，初始国力: {initial_power}")

        async for (session, _) in db_config.get_session():
            from ..services.strategic_relationship_service import StrategicRelationshipService
            relationship_service = StrategicRelationshipService(session)
            await relationship_service.initialize_relationships(project_id)

    async def _create_round_record(self, project_id: int, round_num: int) -> int:
        """
        创建轮次记录并返回 round_id

        Args:
            project_id: 项目ID
            round_num: 轮次号

        Returns:
            轮次ID
        """
        async for session in db_config.get_session():
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

        async for (session, _) in db_config.get_session():
            from ..services.strategic_relationship_service import StrategicRelationshipService
            relationship_service = StrategicRelationshipService(session)
            strategic_relationships = await relationship_service.get_all_agents_relationships(project_id)

        # 获取历史数据
        history_action_records = await self._get_action_history(project_id, round_num)
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

        # 为每个智能体生成决策
        for agent in agents:
            agent_id = agent.get('agent_id')
            agent_name = agent.get('agent_name')

            # 构建AgentInfo
            from app.core.agent_base import AgentBase
            agent_base = AgentBase(**{
                "agent_id": agent.get('agent_id'),
                "agent_name": agent.get('agent_name'),
                "region": agent.get('region'),
                "c_score": agent.get('c_score'),
                "e_score": agent.get('e_score'),
                "m_score": agent.get('m_score'),
                "s_score": agent.get('s_score'),
                "w_score": agent.get('w_score'),
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

            # Debug: log allowed actions
            logger.debug(
                f"[{agent_name}] allowed_actions count: {len(agent_info.allowed_actions)}, "
                f"IDs: {[a['action_id'] for a in agent_info.allowed_actions[:10]]}..."
            )

            # 调用决策引擎
            try:
                decision_result = await decision_engine.make_decision(
                    agent_info=agent_info,
                    info_pool=info_pool,
                    action_stage=action_stage
                )

                if decision_result.success and decision_result.decision:
                    actions_list = decision_result.decision.get('actions', [])
                    logger.info(
                        f"[第 {round_num} 轮] {agent_name} (ID:{agent_id}) LLM决策成功: "
                        f"{len(actions_list)} 个行为"
                    )

                    # 转换为记录格式
                    for action_data in actions_list:
                        target_id = action_data.get('target_agent_id', 0)
                        action_id = action_data.get('action_id')
                        # Convert action_id to int for comparison
                        try:
                            action_id = int(action_id)
                        except (ValueError, TypeError):
                            logger.warning(f"行为ID {action_data.get('action_id')} 格式无效，跳过")
                            continue

                        # 查找行为配置
                        action_config = next((a for a in phase_actions if a.action_id == action_id), None)
                        if not action_config:
                            logger.warning(
                                f"未找到行为ID {action_id} 的配置，跳过。"
                                f"phase_actions中有{len(phase_actions)}个行为，"
                                f"IDs: {[a.action_id for a in phase_actions]}"
                            )
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
                            "decision_detail": action_data.get('cost_benefit_analysis', '')
                        }

                        records.append(record)

                        logger.info(
                            f"[第 {round_num} 轮] {agent_name} 决策: "
                            f"{action_config.action_name} -> 目标 ID:{target_id}"
                        )
                else:
                    logger.warning(
                        f"[第 {round_num} 轮] {agent_name} (ID:{agent_id}) LLM决策失败: "
                        f"{decision_result.validation_errors}"
                    )

            except Exception as e:
                logger.error(
                    f"[第 {round_num} 轮] {agent_name} (ID:{agent_id}) 决策异常: {e}",
                    exc_info=True
                )

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

    async def _get_action_history(self, project_id: int, round_num: int) -> List[Dict]:
        """
        获取历史行为记录

        Args:
            project_id: 项目ID
            round_num: 当前轮次

        Returns:
            历史行为记录列表
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(ActionRecord).where(
                    ActionRecord.project_id == project_id,
                    ActionRecord.round_num < round_num
                )
            )
            records = result.scalars().all()

            return [
                {
                    'round_num': r.round_num,
                    'source_agent_id': r.source_agent_id,
                    'target_agent_id': r.target_agent_id,
                    'action_name': r.action_name,
                    'action_category': r.action_category,
                    'respect_sov': r.respect_sov
                }
                for r in records
            ]

    async def _get_power_history(self, project_id: int, round_num: int) -> List[Dict]:
        """
        获取历史国力数据

        Args:
            project_id: 项目ID
            round_num: 当前轮次

        Returns:
            历史国力数据列表
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

    async def _update_power(
        self, project_id: int, agents: List[Dict], records: List[Dict]
    ) -> None:
        """
        更新国力

        计算每个智能体的国力变化并更新到数据库。

        Args:
            project_id: 项目ID
            agents: 智能体列表
            records: 行为记录列表
        """
        # 计算每个智能体的国力变化
        power_changes = {agent.get('agent_id'): 0 for agent in agents}

        for record in records:
            source_id = record.get('source_agent_id')
            target_id = record.get('target_agent_id')
            initiator_change = record.get('initiator_power_change', 0)
            target_change = record.get('target_power_change', 0)

            # 累计变化
            power_changes[source_id] = power_changes.get(source_id, 0) + initiator_change
            power_changes[target_id] = power_changes.get(target_id, 0) + target_change

        # 更新数据库中的国力
        for agent in agents:
            agent_id = agent.get('agent_id')
            current_power = agent.get('current_total_power', 0)
            change = power_changes.get(agent_id, 0)
            new_power = current_power + change

            logger.debug(
                f"智能体 {agent_id} 国力: {current_power} + {change} = {new_power}"
            )

            async for session in db_config.get_session():
                await session.execute(
                    update(AgentConfig)
                    .where(AgentConfig.agent_id == agent_id)
                    .values(
                        current_total_power=new_power,
                        updated_at=datetime.now()
                    )
                )
                await session.commit()

    async def _save_power_history(
        self, project_id: int, round_id: int, round_num: int, agents: List[Dict], log_manager=None
    ) -> None:
        """
        保存国力历史到 AgentPowerHistory 表

        Args:
            project_id: 项目ID
            round_id: 轮次ID
            round_num: 轮次号
            agents: 智能体列表
            log_manager: 日志管理器实例
        """
        async for session in db_config.get_session():
            # 先获取本轮开始时的国力（上一轮结束时的国力）
            if round_num > 1:
                result = await session.execute(
                    select(AgentPowerHistory)
                    .where(AgentPowerHistory.project_id == project_id)
                    .where(AgentPowerHistory.round_num == round_num - 1)
                )
                last_round_histories = result.scalars().all()
                last_round_powers = {h.agent_id: h.round_end_power for h in last_round_histories}
            else:
                # 第一轮使用初始国力
                last_round_powers = {a['agent_id']: a.get('initial_total_power', 0) for a in agents}

            # 保存本轮国力历史
            for agent in agents:
                agent_id = agent.get('agent_id')
                start_power = last_round_powers.get(agent_id, 0)
                end_power = agent.get('current_total_power', 0)
                change_value = end_power - start_power
                change_rate = (change_value / start_power * 100) if start_power > 0 else 0.0

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

        logger.info(f"第 {round_num} 轮国力历史已保存，共 {len(agents)} 个智能体")

        # 记录到日志文件
        if log_manager:
            power_changes = []
            for agent in agents:
                agent_id = agent.get('agent_id')
                start_power = last_round_powers.get(agent_id, 0)
                end_power = agent.get('current_total_power', 0)
                change_value = end_power - start_power
                change_rate = (change_value / start_power * 100) if start_power > 0 else 0.0
                power_changes.append({
                    "agent_id": agent_id,
                    "agent_name": agent.get('agent_name'),
                    "start_power": start_power,
                    "end_power": end_power,
                    "change_value": change_value,
                    "change_rate": change_rate
                })
            await log_manager.log_power_change(round_num, {"power_changes": power_changes})

    async def _generate_follower_decisions(
        self, project_id: int, agents: List[Dict], round_id: int, round_num: int, log_manager=None
    ) -> Dict[int, Optional[int]]:
        """
        生成LLM驱动的追随投票决策

        学术模型要求：
        阶段1：大模型驱动超级大国与大国决定是否参与领导竞争
        阶段2：大模型驱动所有国家（包括参选者）选择追随对象或中立

        Args:
            project_id: 项目ID
            agents: 所有智能体列表
            round_id: 轮次ID
            round_num: 轮次号
            log_manager: 日志管理器实例

        Returns:
            追随关系字典 {follower_id: leader_id}
        """
        from app.core.agent_base import PowerLevelEnum
        from app.services.llm_service import get_llm_service
        from app.core.prompt_templates import PromptTemplates

        llm_service = get_llm_service()

        # 获取上一轮的秩序信息
        last_order_type = "未判定"
        last_leader_info = "无"
        if round_num > 1:
            try:
                from app.services.statistics_service import statistics_service
                last_round_info = await statistics_service.get_round_detail(project_id, round_num - 1)
                if last_round_info:
                    last_order_type = last_round_info.get('order_type', '未判定')
                    last_leader_info = f"存在领导: {last_round_info.get('has_leader', 'false')}"
            except Exception as e:
                logger.warning(f"获取上轮信息失败: {e}")

        # 构建所有国家信息字符串
        all_agent_info = "\n".join([
            f"  ID:{a['agent_id']} 名称:{a['agent_name']} 国力:{a['current_total_power']:.2f} 层级:{a['power_level']}"
            for a in agents
        ])

        # 阶段1：领导竞争参与决策
        # 只让超级大国和大国决定是否参与
        leader_candidates = []

        for agent in agents:
            if agent.get('power_level') in [
                PowerLevelEnum.SUPERPOWER.value,
                PowerLevelEnum.GREAT_POWER.value
            ]:
                # LLM驱动的参与决策
                prompt = PromptTemplates.LEADERSHIP_PARTICIPATION_TEMPLATE.format(
                    agent_name=agent.get('agent_name'),
                    current_total_power=agent.get('current_total_power', 0),
                    power_level=agent.get('power_level'),
                    all_agent_info=all_agent_info,
                    last_order_type=last_order_type,
                    last_leader_info=last_leader_info
                )

                try:
                    response = await llm_service.call_llm_async(
                        prompt,
                        log_manager=log_manager,
                        log_category="following",
                        round_num=round_num,
                        agent_id=agent.get('agent_id'),
                        agent_name=agent.get('agent_name'),
                        decision_type="leadership_participation"
                    )
                    decision = response.get('decision', '不参与')
                    reason = response.get('reason', '')

                    if decision == '参与':
                        leader_candidates.append(agent)
                        logger.info(f"{agent.get('agent_name')} 决定参与领导竞争: {reason}")
                    else:
                        logger.info(f"{agent.get('agent_name')} 决定不参与: {reason}")

                except Exception as e:
                    logger.error(f"{agent.get('agent_name')} 领导竞争参与决策失败: {e}")
                    # 失败时默认不参与
                    continue

        if not leader_candidates:
            logger.info("无领导候选人 - 所有国家保持中立")
            return {agent.get('agent_id'): None for agent in agents}

        logger.info(f"领导候选人: {[a['agent_name'] for a in leader_candidates]}")

        # 构建参选者信息字符串
        leader_candidates_info = "\n".join([
            f"  ID:{a['agent_id']} 名称:{a['agent_name']} 国力:{a['current_total_power']:.2f}"
            for a in leader_candidates
        ])

        # 阶段2：追随投票决策
        # 所有国家（包括参选者）选择追随对象或中立
        follower_decisions = {}

        for agent in agents:
            # LLM驱动的追随决策
            prompt = PromptTemplates.FOLLOWER_VOTE_TEMPLATE.format(
                agent_name=agent.get('agent_name'),
                current_total_power=agent.get('current_total_power', 0),
                power_level=agent.get('power_level'),
                all_agent_info=all_agent_info,
                last_order_type=last_order_type,
                leader_candidates_info=leader_candidates_info
            )

            try:
                response = await llm_service.call_llm_async(
                    prompt,
                    log_manager=log_manager,
                    log_category="following",
                    round_num=round_num,
                    agent_id=agent.get('agent_id'),
                    agent_name=agent.get('agent_name'),
                    decision_type="follower_vote"
                )
                follower_id = response.get('follower_agent_id')
                follower_name = response.get('follower_agent_name', '中立')
                reason = response.get('reason', '')

                # 验证follower_id是否在参选者中
                if follower_id and any(a['agent_id'] == follower_id for a in leader_candidates):
                    follower_decisions[agent.get('agent_id')] = follower_id
                    logger.info(f"{agent.get('agent_name')} 追随 {follower_name} (ID:{follower_id}): {reason}")
                else:
                    follower_decisions[agent.get('agent_id')] = None
                    logger.info(f"{agent.get('agent_name')} 保持中立: {reason}")

            except Exception as e:
                logger.error(f"{agent.get('agent_name')} 追随投票失败: {e}")
                # 失败时默认中立
                follower_decisions[agent.get('agent_id')] = None

        logger.info(f"追随决策生成完成: {len(follower_decisions)} 个智能体")
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

        # 2. 加载所有智能体到引擎
        agents = await agent_service.get_agents(project_id)
        engine_agents = []
        for agent in agents:
            from app.core.agent_base import AgentBase
            engine_agent = AgentBase(
                agent_id=agent.get('agent_id'),
                agent_name=agent.get('agent_name'),
                region=agent.get('region'),
                c_score=agent.get('c_score', 0),
                e_score=agent.get('e_score', 0),
                m_score=agent.get('m_score', 0),
                s_score=agent.get('s_score', 0),
                w_score=agent.get('w_score', 0)
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

        if project_id in self.running_simulations:
            # 取消正在运行的任务
            self.running_simulations[project_id].cancel()
            del self.running_simulations[project_id]

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
            task = asyncio.create_task(self._run_simulation_loop(project_id))
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

        if project_id in self.running_simulations:
            self.running_simulations[project_id].cancel()
            del self.running_simulations[project_id]

        # 更新状态
        async for session in db_config.get_session():
            await session.execute(
                update(SimulationProject)
                .where(SimulationProject.project_id == project_id)
                .values(status="已终止", updated_at=datetime.now())
            )
            await session.commit()

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

        # 重置所有智能体的当前国力到初始值
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = result.scalars().all()

            for agent in agents:
                agent.current_total_power = agent.initial_total_power
                agent.updated_at = datetime.now()

            await session.commit()

        # 清空行为记录
        async for session in db_config.get_session():
            result = await session.execute(
                select(ActionRecord).where(ActionRecord.project_id == project_id)
            )
            records = result.scalars().all()

            for record in records:
                await session.delete(record)

            await session.commit()

        # 清空轮次记录
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationRound).where(SimulationRound.project_id == project_id)
            )
            rounds = result.scalars().all()

            for round_record in rounds:
                await session.delete(round_record)

            await session.commit()

        # 清空国力历史记录
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentPowerHistory).where(AgentPowerHistory.project_id == project_id)
            )
            histories = result.scalars().all()

            for history in histories:
                await session.delete(history)

            await session.commit()

        # 清空追随关系
        async for session in db_config.get_session():
            result = await session.execute(
                select(FollowerRelation).where(FollowerRelation.project_id == project_id)
            )
            relations = result.scalars().all()

            for relation in relations:
                await session.delete(relation)

            await session.commit()

        # 更新项目状态
        async for session in db_config.get_session():
            await session.execute(
                update(SimulationProject)
                .where(SimulationProject.project_id == project_id)
                .values(
                    status="未启动",
                    current_round=0,
                    updated_at=datetime.now()
                )
            )
            await session.commit()

        return {
            "project_id": project_id,
            "status": "未启动",
            "message": "Simulation reset"
        }


# 单例实例
simulation_service = SimulationService()
