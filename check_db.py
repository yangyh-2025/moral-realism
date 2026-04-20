import asyncio
from sqlalchemy import select, func
from app.config.database import db_config
from app.models.action_record import ActionRecord

async def check():
    async for session in db_config.get_session():
        result = await session.execute(
            select(func.count()).select_from(ActionRecord).where(
                ActionRecord.project_id == 46,
                ActionRecord.round_num == 1
            )
        )
        count = result.scalar()
        print(f'Action records for project 46, round 1: {count}')

        # Get actual records
        result2 = await session.execute(
            select(ActionRecord).where(
                ActionRecord.project_id == 46,
                ActionRecord.round_num == 1
            )
        )
        records = result2.scalars().all()
        print(f'Number of records fetched: {len(records)}')
        if records:
            for r in records[:3]:
                print(f'  Record: source={r.source_agent_id}, target={r.target_agent_id}, action={r.action.action_name}')

asyncio.run(check())
