import asyncio
from sqlalchemy import select
from app.config.database import db_config
from app.models import StrategicRelationship, AgentConfig, SimulationProject


async def check_project_relations():
    """检查项目中的战略关系数据"""

    async for session in db_config.get_session():
        # 获取所有项目
        result = await session.execute(select(SimulationProject))
        projects = result.scalars().all()

        print(f"=== 找到 {len(projects)} 个项目 ===\n")

        for project in projects:
            print(f"项目 ID: {project.project_id}")
            print(f"项目名称: {project.project_name}")
            print(f"当前状态: {project.status}")
            print(f"当前轮次: {project.current_round}")

            # 获取该项目的所有智能体
            agents_result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project.project_id)
            )
            agents = agents_result.scalars().all()
            print(f"智能体数量: {len(agents)}")
            for agent in agents:
                print(f"  - ID:{agent.agent_id} 名称:{agent.agent_name} 层级:{agent.power_level}")

            # 获取该项目的所有战略关系
            relations_result = await session.execute(
                select(StrategicRelationship).where(StrategicRelationship.project_id == project.project_id)
            )
            relations = relations_result.scalars().all()
            print(f"战略关系数量: {len(relations)}")

            if len(relations) == 0:
                print("  [警告] 该项目没有战略关系数据！")
            else:
                for rel in relations:
                    # 获取智能体名称
                    source_agent = await session.execute(
                        select(AgentConfig).where(AgentConfig.agent_id == rel.source_agent_id)
                    )
                    source_name = source_agent.scalar_one_or_none()
                    source_name = source_name.agent_name if source_name else f"ID:{rel.source_agent_id}"

                    target_agent = await session.execute(
                        select(AgentConfig).where(AgentConfig.agent_id == rel.target_agent_id)
                    )
                    target_name = target_agent.scalar_one_or_none()
                    target_name = target_name.agent_name if target_name else f"ID:{rel.target_agent_id}"

                    print(f"  - {source_name} (ID:{rel.source_agent_id}) → {target_name} (ID:{rel.target_agent_id}): {rel.relationship_type}")

            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(check_project_relations())
