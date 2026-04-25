"""
重新创建预设场景项目脚本
清理旧数据并创建新的预设场景项目，确保战略关系正确配置
"""
import asyncio
from sqlalchemy import select, delete
from app.config.database import db_config
from app.services.scene_service import scene_service
from app.models import SimulationProject, AgentConfig, StrategicRelationship, ActionRecord, FollowerRelation


async def cleanup_and_recreate():
    """清理旧数据并重新创建预设场景"""

    async for session in db_config.get_session():
        print("=== 开始清理旧数据 ===\n")

        # 获取所有项目ID
        result = await session.execute(select(SimulationProject.project_id))
        project_ids = result.scalars().all()
        print(f"找到 {len(project_ids)} 个项目")

        # 逆序删除（先删除子表数据，再删除项目）
        for project_id in project_ids:
            print(f"\n清理项目 {project_id}...")

            # 删除战略关系
            await session.execute(
                delete(StrategicRelationship).where(StrategicRelationship.project_id == project_id)
            )

            # 删除追随关系
            await session.execute(
                delete(FollowerRelation).where(FollowerRelation.project_id == project_id)
            )

            # 删除行为记录
            await session.execute(
                delete(ActionRecord).where(ActionRecord.project_id == project_id)
            )

            # 删除轮次统计（如果有这个表的话）

            # 删除智能体
            await session.execute(
                delete(AgentConfig).where(AgentConfig.project_id == project_id)
            )

            await session.commit()
            print(f"  已清理项目 {project_id} 的关联数据")

        # 删除所有项目
        await session.execute(delete(SimulationProject))
        await session.commit()
        print("\n所有项目已删除")

    print("\n=== 开始创建预设场景 ===\n")

    # 创建三个预设场景
    for scene_id in [1, 2, 3]:
        scene = await scene_service.get_preset_scene(scene_id)
        print(f"\n创建场景 {scene_id}: {scene['scene_name']}")

        try:
            project = await scene_service.create_project_from_scene(
                scene_id=scene_id,
                project_name=f"{scene['scene_name']}（重新创建）",
                project_desc=scene["scene_desc"]
            )
            print(f"  项目ID: {project['project_id']}")
            print(f"  项目名称: {project['project_name']}")
            print(f"  状态: {project['status']}")
        except Exception as e:
            print(f"  创建失败: {e}")

    print("\n=== 验证战略关系 ===\n")

    # 验证新创建项目的战略关系
    async for session in db_config.get_session():
        result = await session.execute(select(SimulationProject))
        projects = result.scalars().all()

        for project in projects:
            print(f"\n项目 {project.project_id}: {project.project_name}")

            # 获取智能体信息
            agents_result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project.project_id).order_by(AgentConfig.agent_id)
            )
            agents = agents_result.scalars().all()

            # 按层级分组
            by_level = {}
            for agent in agents:
                level = agent.power_level
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(agent)

            print("  智能体分布:")
            for level in ['超级大国', '大国', '中等强国', '小国']:
                if level in by_level:
                    names = [a.agent_name for a in by_level[level]]
                    print(f"    {level}({len(by_level[level])}): {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")

            # 获取战略关系
            rel_result = await session.execute(
                select(StrategicRelationship).where(StrategicRelationship.project_id == project.project_id)
            )
            relations = rel_result.scalars().all()

            print(f"  战略关系总数: {len(relations)}")

            # 按关系类型分组
            by_type = {}
            for rel in relations:
                rel_type = rel.relationship_type
                if rel_type not in by_type:
                    by_type[rel_type] = 0
                by_type[rel_type] += 1

            if by_type:
                print("  关系类型分布:")
                for rel_type, count in sorted(by_type.items()):
                    print(f"    {rel_type}: {count}")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    asyncio.run(cleanup_and_recreate())
