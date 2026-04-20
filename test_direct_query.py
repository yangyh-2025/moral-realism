import asyncio
from sqlalchemy import select
from app.config.database import db_config
from app.models import ActionRecord

async def test():
    # 模拟API endpoint的查询方式
    async for session in db_config.get_session():
        result = await session.execute(
            select(ActionRecord)
            .where(ActionRecord.project_id == 46)
            .where(ActionRecord.round_num == 1)
        )
        records = result.scalars().all()
        print(f'Inside async-for: {len(records)} records')

    # 测试另一种查询方式 - 先打开session再循环
    async with db_config.async_session_factory() as session:
        result = await session.execute(
            select(ActionRecord)
            .where(ActionRecord.project_id == 46)
            .where(ActionRecord.round_num == 1)
        )
        records = result.scalars().all()
        print(f'Second query (async with): {len(records)} records')

asyncio.run(test())
