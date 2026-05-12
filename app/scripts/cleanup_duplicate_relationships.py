"""
cleanup_duplicate_relationships.py
对 strategic_relationship 表执行一次性去重:
- 对每个 (project_id, source_agent_id, target_agent_id) 仅保留 relation_id 最大的一行;
- 在去重后, 如果 sqlite_master 中尚无 uq_strategic_rel 唯一索引则创建之。

直接以脚本方式运行:
    python -m app.scripts.cleanup_duplicate_relationships

也可在交互式上下文中 await main()。
"""

import asyncio
from loguru import logger
from sqlalchemy import text

from app.config.database import db_config


async def main() -> None:
    async with db_config.engine.begin() as conn:
        # 0) 表是否存在
        tbl_check = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='strategic_relationship'"
        ))
        if not tbl_check.first():
            logger.info("strategic_relationship 表不存在, 跳过去重")
            return

        # 1) 统计冗余记录数
        dup_count_res = await conn.execute(text(
            "SELECT COUNT(*) FROM strategic_relationship sr "
            "WHERE sr.relation_id < ("
            "  SELECT MAX(sr2.relation_id) FROM strategic_relationship sr2 "
            "  WHERE sr2.project_id = sr.project_id "
            "    AND sr2.source_agent_id = sr.source_agent_id "
            "    AND sr2.target_agent_id = sr.target_agent_id"
            ")"
        ))
        dup_count = dup_count_res.scalar() or 0
        logger.info(f"检测到冗余战略关系记录 {dup_count} 条")

        # 2) 删除冗余
        if dup_count > 0:
            await conn.execute(text(
                "DELETE FROM strategic_relationship "
                "WHERE relation_id NOT IN ("
                "  SELECT MAX(relation_id) FROM strategic_relationship "
                "  GROUP BY project_id, source_agent_id, target_agent_id"
                ")"
            ))
            logger.info(f"已删除 {dup_count} 条冗余记录")

        # 3) 验证: 项目15 的去重结果
        verify_res = await conn.execute(text(
            "SELECT project_id, source_agent_id, target_agent_id, COUNT(*) c "
            "FROM strategic_relationship "
            "WHERE project_id = 15 "
            "GROUP BY project_id, source_agent_id, target_agent_id "
            "HAVING c > 1"
        ))
        remaining = verify_res.all()
        if remaining:
            logger.error(f"项目15 仍存在重复: {remaining}")
        else:
            logger.info("项目15 已无重复 (project_id, source, target) 记录")

        # 4) 若无唯一索引则创建
        idx_check = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='uq_strategic_rel'"
        ))
        if not idx_check.first():
            try:
                await conn.execute(text(
                    "CREATE UNIQUE INDEX uq_strategic_rel "
                    "ON strategic_relationship(project_id, source_agent_id, target_agent_id)"
                ))
                logger.info("已创建 uq_strategic_rel 唯一索引")
            except Exception as e:
                logger.warning(f"创建 uq_strategic_rel 失败: {e}")
        else:
            logger.info("uq_strategic_rel 唯一索引已存在")


if __name__ == "__main__":
    asyncio.run(main())
