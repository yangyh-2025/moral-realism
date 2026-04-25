"""测试设置战略关系"""

import asyncio
import sys
sys.path.append(".")

from app.config.database import db_config
from app.services.strategic_relationship_service import StrategicRelationshipService
from app.models.agent_config import AgentConfig, PowerLevelEnum


async def test_set_relation():
    """测试设置关系"""
    project_id = 16  # 最新项目

    async def get_agents_by_id(session, agent_id):
        from sqlalchemy import select
        stmt = select(AgentConfig).where(AgentConfig.agent_id == agent_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async for session in db_config.get_session():
        # 获取所有智能体
        from sqlalchemy import select
        stmt = select(AgentConfig).where(AgentConfig.project_id == project_id)
        result = await session.execute(stmt)
        agents = result.scalars().all()

        print(f"项目 {project_id} 的智能体:")
        for a in agents:
            print(f"  ID: {a.agent_id}, 名称: {a.agent_name}, 国力: {a.power_level}")

        # 找到不同类型的智能体
        superpower = agents[0]
        middle_power = agents[3]
        small_state = agents[8]

        print(f"\n测试设置关系:")
        print(f"  超级大国: {superpower.agent_id} ({superpower.agent_name})")
        print(f"  中等强国: {middle_power.agent_id} ({middle_power.agent_name})")
        print(f"  小国: {small_state.agent_id} ({small_state.agent_name})")

        service = StrategicRelationshipService(session)

        # 测试设置关系
        print(f"\n测试1: 超级大国 -> 中等强国")
        try:
            await service.set_relationship(
                project_id,
                superpower.agent_id,
                middle_power.agent_id,
                "伙伴关系"
            )
            print(f"  成功!")
        except Exception as e:
            print(f"  失败: {e}")

        print(f"\n测试2: 超级大国 -> 小国")
        try:
            await service.set_relationship(
                project_id,
                superpower.agent_id,
                small_state.agent_id,
                "伙伴关系"
            )
            print(f"  成功!")
        except Exception as e:
            print(f"  失败: {e}")

        print(f"\n测试3: 中等强国 -> 小国 (应该失败)")
        try:
            await service.set_relationship(
                project_id,
                middle_power.agent_id,
                small_state.agent_id,
                "伙伴关系"
            )
            print(f"  成功!")
        except Exception as e:
            print(f"  失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_set_relation())
