"""
测试战略关系API
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.config.database import db_config
from app.services.strategic_relationship_service import StrategicRelationshipService

async def test_get_all_relationships():
    """测试获取所有关系"""
    print("测试1: 获取项目14的所有战略关系...")
    try:
        async for session in db_config.get_session():
            service = StrategicRelationshipService(session)
            result = await service.get_all_agents_relationships(14)
            print(f"成功! 找到 {len(result)} 个智能体的关系")
            for agent_id, relations in result.items():
                print(f"  智能体 {agent_id}: {relations}")
            return result
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_direct_query():
    """测试直接查询"""
    print("\n测试2: 直接查询战略关系表...")
    try:
        from app.models import StrategicRelationship
        async for session in db_config.get_session():
            from sqlalchemy import select
            result = await session.execute(select(StrategicRelationship).where(StrategicRelationship.project_id == 14))
            relationships = result.scalars().all()
            print(f"成功! 找到 {len(relationships)} 条关系")
            for r in relationships:
                print(f"  - {r.source_agent_id} -> {r.target_agent_id}: {r.relationship_type}")
            return relationships
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_initialize():
    """测试初始化"""
    print("\n测试3: 测试初始化战略关系...")
    try:
        from app.models import StrategicRelationship, AgentConfig
        from sqlalchemy import select
        async for session in db_config.get_session():
            # 查看当前智能体
            agents_stmt = select(AgentConfig).where(AgentConfig.project_id == 14)
            agents_result = await session.execute(agents_stmt)
            agents = agents_result.scalars().all()
            print(f"项目14有 {len(agents)} 个智能体:")
            for a in agents:
                print(f"  - ID: {a.agent_id}, 名称: {a.agent_name}, 国力: {a.power_level}")

            # 查看当前关系
            relations_stmt = select(StrategicRelationship).where(StrategicRelationship.project_id == 14)
            relations_result = await session.execute(relations_stmt)
            relations = relations_result.scalars().all()
            print(f"当前有 {len(relations)} 个关系")

            # 初始化
            print("开始初始化...")
            service = StrategicRelationshipService(session)
            await service.initialize_relationships(14)

            # 查看初始化后的关系
            relations_result = await session.execute(relations_stmt)
            relations = relations_result.scalars().all()
            print(f"初始化后有 {len(relations)} 个关系:")
            for r in relations:
                print(f"  - {r.source_agent_id} -> {r.target_agent_id}: {r.relationship_type}")
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("测试：先初始化，然后查看结果")
    print("=" * 50)
    asyncio.run(test_initialize())
    print("\n" + "=" * 50)
    print("测试：查看最终结果")
    print("=" * 50)
    asyncio.run(test_get_all_relationships())
