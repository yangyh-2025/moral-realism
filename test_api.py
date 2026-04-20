import asyncio
from sqlalchemy import select
from app.config.database import db_config
from app.models import ActionRecord, AgentConfig as AgentConfigModel

async def check():
    async for session in db_config.get_session():
        # 查询行为记录
        result = await session.execute(
            select(ActionRecord)
            .where(ActionRecord.project_id == 46)
            .where(ActionRecord.round_num == 1)
        )
        records = result.scalars().all()
        print(f'ActionRecord count: {len(records)}')

        # 获取智能体名称映射
        agents_result = await session.execute(
            select(AgentConfigModel).where(AgentConfigModel.project_id == 46)
        )
        agents = agents_result.scalars().all()
        print(f'Agents count: {len(agents)}')
        agent_names = {agent.agent_id: agent.agent_name for agent in agents}

        if records:
            for r in records[:3]:
                print(f'  Record: source={r.source_agent_id}, target={r.target_agent_id}, action={r.action_name}')

asyncio.run(check())
