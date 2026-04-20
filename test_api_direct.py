"""
直接模拟API endpoint的查询
"""
import asyncio
from sqlalchemy import select
from app.config.database import db_config
from app.models import ActionRecord, AgentConfig as AgentConfigModel, FollowerRelation

async def get_round_detail(project_id=46, round_num=1):
    """模拟 get_round_detail API endpoint"""
    async for session in db_config.get_session():
        # 查询行为记录
        result = await session.execute(
            select(ActionRecord)
            .where(ActionRecord.project_id == project_id)
            .where(ActionRecord.round_num == round_num)
        )
        records = result.scalars().all()
        print(f'Query 1: {len(records)} records')

        # 获取智能体名称映射
        agents_result = await session.execute(
            select(AgentConfigModel).where(AgentConfigModel.project_id == project_id)
        )
        agents = agents_result.scalars().all()
        print(f'Query 2: {len(agents)} agents')

        # 获取追随者关系
        follower_relations_result = await session.execute(
            select(FollowerRelation)
            .where(FollowerRelation.project_id == project_id)
            .where(FollowerRelation.round_num == round_num)
        )
        follower_relations = follower_relations_result.scalars().all()
        print(f'Query 3: {len(follower_relations)} follower relations')

        print(f'Returning total_actions={len(records)}')
        return {
            "total_actions": len(records),
            "round_num": round_num
        }

asyncio.run(get_round_detail())
