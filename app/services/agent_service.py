"""
智能体管理服务
负责智能体配置的增删改查和基本操作
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from sqlalchemy import select
from app.config.database import db_config
from app.models import AgentConfig


class AgentConfigRequest(BaseModel):
    """
    智能体配置请求模型

    用于验证和传递智能体配置数据。
    """
    agent_name: str
    region: str
    c_score: float = Field(ge=0, le=100, description="基本实体得分 0-100")
    e_score: float = Field(ge=0, le=200, description="经济实力 0-200")
    m_score: float = Field(ge=0, le=200, description="军事实力 0-200")
    s_score: float = Field(ge=0, le=2, description="战略目的系数 0-2")
    w_score: float = Field(ge=0, le=2, description="战略意志系数 0-2")
    leader_type: Optional[str] = None


class AgentService:
    """
    智能体管理服务

    提供智能体配置的完整生命周期管理，
    包括创建、查询、更新、删除以及国力计算等功能。
    """

    def calculate_total_power(self, c_score: float, e_score: float, m_score: float,
                           s_score: float, w_score: float) -> float:
        """
        计算综合国力（克莱因方程）

        使用克莱因综合国力方程计算国家的综合实力：
        Pp = (C + E + M) × (S + W)

        其中：
        - C: 基本实体得分（人口+领土）
        - E: 经济实力
        - M: 军事实力
        - S: 战略目的系数
        - W: 战略意志系数

        Args:
            c_score: 基本实体得分
            e_score: 经济实力
            m_score: 军事实力
            s_score: 战略目的系数
            w_score: 战略意志系数

        Returns:
            综合国力得分
        """
        return (c_score + e_score + m_score) * (s_score + w_score)

    def determine_power_level(self, total_power: float) -> str:
        """
        判定实力层级

        根据综合国力得分判定国家的实力层级：
        - 超级大国：≥500
        - 大国：200-499
        - 中等强国：100-199
        - 小国：<100

        Args:
            total_power: 综合国力得分

        Returns:
            实力层级字符串
        """
        if total_power >= 500:
            return "超级大国"
        elif 200 <= total_power < 500:
            return "大国"
        elif 100 <= total_power < 200:
            return "中等强国"
        else:
            return "小国"

    async def add_agent(self, project_id: int, config: AgentConfigRequest) -> dict:
        """
        为项目添加智能体

        计算智能体的综合国力和实力层级，
        并保存到数据库中。

        Args:
            project_id: 项目ID
            config: 智能体配置请求

        Returns:
            新创建的智能体信息字典
        """
        # 计算综合国力和实力层级
        initial_power = self.calculate_total_power(
            config.c_score, config.e_score, config.m_score,
            config.s_score, config.w_score
        )
        power_level = self.determine_power_level(initial_power)

        # 验证领导类型配置（只有超级大国和大国可以配置领导类型）
        if config.leader_type and power_level not in ["超级大国", "大国"]:
            raise ValueError("仅超级大国与大国可配置领导集体类型")

        # 保存到数据库
        async for session in db_config.get_session():
            agent = AgentConfig(
                project_id=project_id,
                agent_name=config.agent_name,
                region=config.region,
                c_score=config.c_score,
                e_score=config.e_score,
                m_score=config.m_score,
                s_score=config.s_score,
                w_score=config.w_score,
                initial_total_power=initial_power,
                current_total_power=initial_power,
                power_level=power_level,
                leader_type=config.leader_type
            )
            session.add(agent)
            await session.commit()
            await session.refresh(agent)

            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "region": agent.region,
                "c_score": agent.c_score,
                "e_score": agent.e_score,
                "m_score": agent.m_score,
                "s_score": agent.s_score,
                "w_score": agent.w_score,
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type
            }

    async def get_agents(self, project_id: int, power_level_filter: Optional[str] = None,
                       region_filter: Optional[str] = None) -> List[dict]:
        """
        获取项目智能体列表

        支持按实力层级和区域进行筛选。

        Args:
            project_id: 项目ID
            power_level_filter: 实力层级筛选条件
            region_filter: 区域筛选条件

        Returns:
            智能体列表
        """
        async for session in db_config.get_session():
            query = select(AgentConfig).where(AgentConfig.project_id == project_id)
            # 应用实力层级筛选
            if power_level_filter:
                query = query.where(AgentConfig.power_level == power_level_filter)
            # 应用区域筛选
            if region_filter:
                query = query.where(AgentConfig.region == region_filter)
            result = await session.execute(query)
            agents = result.scalars().all()

            return [
                {
                    "agent_id": a.agent_id,
                    "agent_name": a.agent_name,
                    "region": a.region,
                    "c_score": a.c_score,
                    "e_score": a.e_score,
                    "m_score": a.m_score,
                    "s_score": a.s_score,
                    "w_score": a.w_score,
                    "initial_total_power": a.initial_total_power,
                    "current_total_power": a.current_total_power,
                    "power_level": a.power_level,
                    "leader_type": a.leader_type
                }
                for a in agents
            ]

    async def get_agent(self, project_id: int, agent_id: int) -> Optional[dict]:
        """
        获取智能体详情

        Args:
            project_id: 项目ID
            agent_id: 智能体ID

        Returns:
            智能体详情字典，或None（如果不存在）
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(
                    AgentConfig.project_id == project_id,
                    AgentConfig.agent_id == agent_id
                )
            )
            agent = result.scalar_one_or_none()

            if not agent:
                return None

            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "region": agent.region,
                "c_score": agent.c_score,
                "e_score": agent.e_score,
                "m_score": agent.m_score,
                "s_score": agent.s_score,
                "w_score": agent.w_score,
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type
            }

    async def update_agent(self, project_id: int, agent_id: int, config: AgentConfigRequest) -> Optional[dict]:
        """
        更新智能体初始配置

        更新智能体的配置信息，并重新计算综合国力和实力层级。

        Args:
            project_id: 项目ID
            agent_id: 智能体ID
            config: 新的智能体配置

        Returns:
            更新后的智能体信息字典，或None（如果不存在）
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(
                    AgentConfig.project_id == project_id,
                    AgentConfig.agent_id == agent_id
                )
            )
            agent = result.scalar_one_or_none()

            if not agent:
                return None

            # 更新基本配置
            agent.agent_name = config.agent_name
            agent.region = config.region
            agent.c_score = config.c_score
            agent.e_score = config.e_score
            agent.m_score = config.m_score
            agent.s_score = config.s_score
            agent.w_score = config.w_score
            # 重新计算综合国力和实力层级
            agent.initial_total_power = self.calculate_total_power(
                config.c_score, config.e_score, config.m_score,
                config.s_score, config.w_score
            )
            agent.current_total_power = agent.initial_total_power
            agent.power_level = self.determine_power_level(agent.initial_total_power)
            agent.leader_type = config.leader_type

            await session.commit()
            await session.refresh(agent)

            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "region": agent.region,
                "c_score": agent.c_score,
                "e_score": agent.e_score,
                "m_score": agent.m_score,
                "s_score": agent.s_score,
                "w_score": agent.w_score,
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type
            }

    async def delete_agent(self, project_id: int, agent_id: int) -> bool:
        """
        删除智能体

        Args:
            project_id: 项目ID
            agent_id: 智能体ID

        Returns:
            删除是否成功
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(
                    AgentConfig.project_id == project_id,
                    AgentConfig.agent_id == agent_id
                )
            )
            agent = result.scalar_one_or_none()

            if not agent:
                return False

            await session.delete(agent)
            await session.commit()
            return True

    async def update_agent_power(self, agent_id: int, power_change: float) -> Optional[dict]:
        """
        更新智能体实时国力

        调整智能体的当前国力值。

        Args:
            agent_id: 智能体ID
            power_change: 国力变化值（正数表示增加，负数表示减少）

        Returns:
            更新后的国力信息字典，或None（如果不存在）
        """
        # 验证国力变动范围（单次行为变动绝对值不超过1分）
        if abs(power_change) > 1:
            raise ValueError("单次行为国力变动绝对值不能超过1分")

        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.agent_id == agent_id)
            )
            agent = result.scalar_one_or_none()

            if not agent:
                return None

            # 更新当前国力，确保不低于0
            agent.current_total_power = max(0, agent.current_total_power + power_change)
            await session.commit()
            await session.refresh(agent)

            return {
                "agent_id": agent.agent_id,
                "current_total_power": agent.current_total_power
            }


# 单例实例
agent_service = AgentService()
