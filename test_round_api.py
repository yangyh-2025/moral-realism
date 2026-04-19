#!/usr/bin/env python
"""测试轮次API返回的数据格式"""
import asyncio
import sys
sys.path.insert(0, '.')

import httpx

async def test_round_api():
    """测试轮次API"""
    client = httpx.AsyncClient(base_url="http://localhost:8000/api/v1")

    try:
        # 1. 获取项目列表
        print("=" * 50)
        print("1. 获取项目列表")
        resp = await client.get("/simulation/project/list")
        projects = resp.json()
        print(f"项目数量: {len(projects)}")
        if projects:
            project_id = projects[-1]['project_id']
            print(f"最新项目ID: {project_id}")
            print(f"项目状态: {projects[-1]['status']}")
            print(f"当前轮次: {projects[-1]['current_round']}")
        else:
            print("没有找到项目")
            return

        # 2. 获取项目详情
        print("\n" + "=" * 50)
        print("2. 获取项目详情")
        resp = await client.get(f"/simulation/project/{project_id}")
        project = resp.json()
        print(f"项目ID: {project['project_id']}")
        print(f"项目名称: {project['project_name']}")
        print(f"当前轮次: {project['current_round']}")
        print(f"总轮次: {project['total_rounds']}")

        # 3. 测试轮次详情API
        current_round = project['current_round']
        if current_round > 0:
            print("\n" + "=" * 50)
            print(f"3. 获取第{current_round}轮详情")
            resp = await client.get(f"/simulation/{project_id}/round/{current_round}")
            round_data = resp.json()
            print(f"轮次: {round_data['round_num']}")
            print(f"总行为数: {round_data['total_actions']}")
            print(f"尊重主权行为: {round_data['respect_sov_actions']}")
            print(f"有领导: {round_data['has_leader']}")
            print(f"行动记录数: {len(round_data['actions'])}")
            print(f"追随关系数: {len(round_data['follower_relations'])}")

            if round_data['actions']:
                print("\n前5条行为:")
                for action in round_data['actions'][:5]:
                    print(f"  {action['source_agent_name']} -> {action['action_name']} -> {action['target_agent_name']}")

            if round_data['follower_relations']:
                print("\n前5条追随关系:")
                for relation in round_data['follower_relations'][:5]:
                    leader = relation['leader_agent_name'] or '中立'
                    print(f"  {relation['follower_agent_name']} -> {leader}")
        else:
            print(f"\n当前轮次为0，没有完成的数据")

    except Exception as e:
        print(f"错误测试API: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_round_api())
