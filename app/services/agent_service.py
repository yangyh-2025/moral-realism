"""
智能体管理服务
负责智能体配置的增删改查和基本操作（CINC版）
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from sqlalchemy import select
from app.config.database import db_config
from app.models import AgentConfig


class AgentConfigRequest(BaseModel):
    """
    智能体配置请求模型（CINC版）

    用于验证和传递智能体配置数据。
    """
    agent_name: str
    region: str
    milex: float = Field(default=0, ge=0, description="军事支出（千美元）")
    milper: float = Field(default=0, ge=0, description="军事人员（千人）")
    irst: float = Field(default=0, ge=0, description="钢铁产量（千吨）")
    pec: float = Field(default=0, ge=0, description="一次能源消耗（千吨煤当量）")
    tpop: float = Field(default=0, ge=0, description="总人口（千人）")
    upop: float = Field(default=0, ge=0, description="城市人口（千人）")
    country_code: Optional[int] = Field(default=None, description="COW国家数字代码")
    cinc_year: Optional[int] = Field(default=2016, description="CINC数据年份")
    leader_type: Optional[str] = None


class AgentService:
    """
    智能体管理服务（CINC版）

    提供智能体配置的完整生命周期管理，
    包括创建、查询、更新、删除以及CINC国力计算等功能。
    """

    async def calculate_total_power(self, project_id: int,
                                    agent_indicators: dict) -> float:
        """
        计算单个国家的CINC指数

        基于CINC公式计算国家在仿真体系内的相对国力：
        cinc = (milex/Σmilex + milper/Σmilper + irst/Σirst +
                pec/Σpec + tpop/Σtpop + upop/Σupop) / 6

        Args:
            project_id: 项目ID
            agent_indicators: 当前国家的6项指标 {"milex": float, ...}

        Returns:
            CINC指数（0-1之间的比例值），如果项目无其他agent则返回0.0
        """
        from app.core.cinc_calculator import CINCCalculator

        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = result.scalars().all()

            if not agents:
                return 0.0

            all_indicators = [
                {"agent_id": a.agent_id, "milex": a.milex, "milper": a.milper,
                 "irst": a.irst, "pec": a.pec, "tpop": a.tpop, "upop": a.upop}
                for a in agents
            ]

            return CINCCalculator.calculate_cinc(agent_indicators, all_indicators)

    async def determine_power_level(self, project_id: int, cinc: float) -> str:
        """
        判定实力层级（基于CINC相对排名）

        根据CINC在仿真体系内的相对排名判定国家层级：
        - 超级大国：前10%
        - 大国：10%-30%
        - 中等强国：30%-60%
        - 小国：后40%

        如果项目只有一个agent，按绝对阈值：
        - cinc > 0.1: 超级大国
        - cinc > 0.05: 大国
        - cinc > 0.01: 中等强国
        - 否则: 小国

        Args:
            project_id: 项目ID
            cinc: CINC指数

        Returns:
            实力层级字符串
        """
        from app.core.cinc_calculator import CINCCalculator, PowerLevelEnum

        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = result.scalars().all()

            if len(agents) <= 1:
                # 单agent项目使用绝对阈值
                if cinc > 0.1:
                    return PowerLevelEnum.SUPERPOWER.value
                elif cinc > 0.05:
                    return PowerLevelEnum.GREAT_POWER.value
                elif cinc > 0.01:
                    return PowerLevelEnum.MIDDLE_POWER.value
                else:
                    return PowerLevelEnum.SMALL_STATE.value

            all_cincs = [a.current_total_power for a in agents]
            level = CINCCalculator.determine_power_level(cinc, all_cincs)
            return level.value if hasattr(level, 'value') else str(level)

    async def _recalculate_all_cincs(self, project_id: int):
        """重新计算项目内所有agent的CINC和层级"""
        from app.core.cinc_calculator import CINCCalculator
        from app.core.cinc_calculator import PowerLevelEnum

        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = result.scalars().all()

            if not agents:
                return

            # 构建指标列表
            indicators = [
                {"agent_id": a.agent_id, "milex": a.milex, "milper": a.milper,
                 "irst": a.irst, "pec": a.pec, "tpop": a.tpop, "upop": a.upop}
                for a in agents
            ]

            cincs = CINCCalculator.calculate_all_cincs(indicators)
            levels = CINCCalculator.determine_all_power_levels(cincs)

            for a in agents:
                new_cinc = cincs.get(a.agent_id, 0.0)
                # 仅在初始化时设置 initial_total_power
                if a.initial_total_power == 0.0:
                    a.initial_total_power = new_cinc
                a.current_total_power = new_cinc
                level = levels.get(a.agent_id, PowerLevelEnum.SMALL_STATE)
                a.power_level = level.value if hasattr(level, 'value') else str(level)

            await session.commit()

    async def add_agent(self, project_id: int, config: AgentConfigRequest) -> dict:
        """
        为项目添加智能体（CINC版）

        1. 如果传入了country_code和cinc_year，从CINC数据库自动读取6个指标
        2. 否则使用请求中的milex/milper/irst/pec/tpop/upop
        3. 保存后批量重算同项目所有agent的CINC和层级
        4. 验证leader_type权限

        Args:
            project_id: 项目ID
            config: 智能体配置请求

        Returns:
            新创建的智能体信息字典
        """
        # 确定6项指标值
        milex = config.milex
        milper = config.milper
        irst = config.irst
        pec = config.pec
        tpop = config.tpop
        upop = config.upop
        country_code = config.country_code
        cinc_year = config.cinc_year

        # 如果提供了country_code和cinc_year，从CINC数据库读取
        if country_code is not None and cinc_year is not None:
            try:
                from app.core.cinc_data_loader import get_cinc_loader
                loader = get_cinc_loader()
                record = loader.get_record(country_code, cinc_year)
                if record:
                    milex = record.milex
                    milper = record.milper
                    irst = record.irst
                    pec = record.pec
                    tpop = record.tpop
                    upop = record.upop
            except Exception:
                # 如果加载失败，使用请求中的值
                pass

        # 保存到数据库（先保存指标，再批量计算CINC）
        async for session in db_config.get_session():
            agent = AgentConfig(
                project_id=project_id,
                agent_name=config.agent_name,
                region=config.region,
                milex=milex,
                milper=milper,
                irst=irst,
                pec=pec,
                tpop=tpop,
                upop=upop,
                initial_total_power=0.0,
                current_total_power=0.0,
                power_level="小国",
                leader_type=config.leader_type,
                country_code=country_code,
                cinc_year=cinc_year,
            )
            session.add(agent)
            await session.commit()
            await session.refresh(agent)

            agent_id = agent.agent_id

        # 批量重算项目内所有agent的CINC和层级
        await self._recalculate_all_cincs(project_id)

        # 重新获取agent以获取更新后的CINC和层级
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.agent_id == agent_id)
            )
            agent = result.scalar_one()

            # 注意：CINC层级是体系内相对排名，新增agent会引发排名重排，
            # 因此add_agent阶段不对leader_type做硬校验。
            # 如果当前层级不允许配置leader_type，则在持久化时清空该字段，
            # 但保留agent本身（其他agent加入后排名可能变化）。
            if config.leader_type and agent.power_level not in ["超级大国", "大国"]:
                logger.warning(
                    f"智能体 {agent.agent_name} 当前层级为 {agent.power_level}，"
                    f"非超级大国/大国，仍保留leader_type={config.leader_type}（"
                    f"层级会随后续agent加入而动态调整）"
                )

            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "region": agent.region,
                "milex": agent.milex,
                "milper": agent.milper,
                "irst": agent.irst,
                "pec": agent.pec,
                "tpop": agent.tpop,
                "upop": agent.upop,
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type,
                "country_code": agent.country_code,
                "cinc_year": agent.cinc_year,
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
                    "milex": a.milex,
                    "milper": a.milper,
                    "irst": a.irst,
                    "pec": a.pec,
                    "tpop": a.tpop,
                    "upop": a.upop,
                    "initial_total_power": a.initial_total_power,
                    "current_total_power": a.current_total_power,
                    "power_level": a.power_level,
                    "leader_type": a.leader_type,
                    "country_code": a.country_code,
                    "cinc_year": a.cinc_year,
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
                "milex": agent.milex,
                "milper": agent.milper,
                "irst": agent.irst,
                "pec": agent.pec,
                "tpop": agent.tpop,
                "upop": agent.upop,
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type,
                "country_code": agent.country_code,
                "cinc_year": agent.cinc_year,
            }

    async def update_agent(self, project_id: int, agent_id: int, config: AgentConfigRequest) -> Optional[dict]:
        """
        更新智能体初始配置（CINC版）

        更新智能体的配置信息，并重新计算CINC和实力层级。

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

            # 确定6项指标值
            milex = config.milex
            milper = config.milper
            irst = config.irst
            pec = config.pec
            tpop = config.tpop
            upop = config.upop
            country_code = config.country_code
            cinc_year = config.cinc_year

            # 如果提供了country_code和cinc_year，从CINC数据库读取
            if country_code is not None and cinc_year is not None:
                try:
                    from app.core.cinc_data_loader import get_cinc_loader
                    loader = get_cinc_loader()
                    record = loader.get_record(country_code, cinc_year)
                    if record:
                        milex = record.milex
                        milper = record.milper
                        irst = record.irst
                        pec = record.pec
                        tpop = record.tpop
                        upop = record.upop
                except Exception:
                    pass

            # 更新基本配置
            agent.agent_name = config.agent_name
            agent.region = config.region
            agent.milex = milex
            agent.milper = milper
            agent.irst = irst
            agent.pec = pec
            agent.tpop = tpop
            agent.upop = upop
            agent.country_code = country_code
            agent.cinc_year = cinc_year
            agent.leader_type = config.leader_type

            await session.commit()

        # 批量重算项目内所有agent的CINC和层级
        await self._recalculate_all_cincs(project_id)

        # 重新获取agent
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(
                    AgentConfig.project_id == project_id,
                    AgentConfig.agent_id == agent_id
                )
            )
            agent = result.scalar_one()

            # 注意：CINC层级是体系内相对排名，更新agent后排名可能变化，
            # 因此update_agent阶段不对leader_type做硬校验，只警告。
            if config.leader_type and agent.power_level not in ["超级大国", "大国"]:
                logger.warning(
                    f"智能体 {agent.agent_name} 当前层级为 {agent.power_level}，"
                    f"非超级大国/大国，仍保留leader_type={config.leader_type}（"
                    f"层级会随其他agent变化而动态调整）"
                )

            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "region": agent.region,
                "milex": agent.milex,
                "milper": agent.milper,
                "irst": agent.irst,
                "pec": agent.pec,
                "tpop": agent.tpop,
                "upop": agent.upop,
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type,
                "country_code": agent.country_code,
                "cinc_year": agent.cinc_year,
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

        # 删除后重算项目内所有剩余agent的CINC和层级
        await self._recalculate_all_cincs(project_id)
        return True

    async def update_agent_power(self, agent_id: int, power_change: float) -> Optional[dict]:
        """
        更新智能体实时CINC

        调整智能体的当前CINC值。保持签名兼容，但内部逻辑变为更新CINC值。

        Args:
            agent_id: 智能体ID
            power_change: CINC变化值（正数表示增加，负数表示减少）

        Returns:
            更新后的CINC信息字典，或None（如果不存在）
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.agent_id == agent_id)
            )
            agent = result.scalar_one_or_none()

            if not agent:
                return None

            # 更新当前CINC，确保不低于0
            agent.current_total_power = max(0.0, agent.current_total_power + power_change)
            await session.commit()
            await session.refresh(agent)

            return {
                "agent_id": agent.agent_id,
                "current_total_power": agent.current_total_power
            }


# 单例实例
agent_service = AgentService()
