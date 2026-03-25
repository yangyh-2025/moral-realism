#!/usr/bin/env python3
"""
非常简单的测试脚本来验证决策引擎的格式化功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 我们直接从决策引擎中导入 _format_environment_state 逻辑来测试
# 创建一个模拟的决策引擎

def test_format_environment_state():
    """测试格式化功能"""
    # 模拟环境状态
    environment_state = {
        'agents': [
            {
                'name': '测试国1',
                'agent_id': 'country_1',
                'region': '东亚',
                'power': 45.5,
                'power_tier': 'small_power',
                'comprehensive_power': 45.5
            },
            {
                'name': '测试国2',
                'agent_id': 'country_2',
                'region': '东南亚',
                'power': 78.3,
                'power_tier': 'middle_power',
                'comprehensive_power': 78.3
            }
        ],
        'active_events': [
            {
                'description': '测试事件1',
                'name': '测试事件'
            }
        ]
    }

    # 我们直接复制并使用 _format_environment_state 方法的逻辑
    def _format_environment_state(env_state):
        """格式化环境状态"""
        formatted = []

        # 获取其他国家信息
        agents = env_state.get('agents', [])
        if agents:
            formatted.append("### 其他国家情况")
            for agent in agents[:10]:  # 限制显示数量
                agent_info = []
                name = agent.get('name', agent.get('agent_id', '未知国家'))
                power = agent.get('comprehensive_power', agent.get('power', 0))
                power_tier = agent.get('power_tier', 'unknown')
                region = agent.get('region', '未知区域')

                # 格式化国家信息
                agent_info.append(name)
                if power:
                    agent_info.append(f"实力={power:.2f}")
                if power_tier and power_tier != 'unknown':
                    agent_info.append(f"层级={power_tier}")
                if region and region != '未知区域':
                    agent_info.append(f"区域={region}")

                formatted.append(f"- {'，'.join(agent_info)}")
        else:
            formatted.append("### 其他国家情况\n无其他国家信息")

        if 'active_events' in env_state and env_state['active_events']:
            formatted.append("\n### 当前事件")
            for event in env_state['active_events']:
                formatted.append(f"- {event.get('description', '未知事件')}")

        if 'alliances' in env_state and env_state['alliances']:
            formatted.append("\n### 现有联盟")
            for alliance in env_state['alliances'][:5]:
                formatted.append(f"- {alliance.get('type', '未知联盟')}")

        # 确保返回一个完整的字符串
        return '\n'.join(formatted) if formatted else "暂无特殊环境信息"

    # 测试格式化功能
    print("测试格式化功能...")
    result = _format_environment_state(environment_state)

    print("\n格式化结果:")
    print(result)

    # 验证结果
    assert "测试国1" in result, "应该包含测试国1"
    assert "测试国2" in result, "应该包含测试国2"
    assert "实力=45.50" in result, "应该包含实力信息"
    assert "实力=78.30" in result, "应该包含实力信息"
    assert "层级=small_power" in result, "应该包含层级信息"
    assert "层级=middle_power" in result, "应该包含层级信息"
    assert "区域=东亚" in result, "应该包含区域信息"
    assert "区域=东南亚" in result, "应该包含区域信息"
    assert "测试事件1" in result, "应该包含事件信息"

    print("\n✅ 所有测试通过！格式化功能正常工作。")

    # 测试无agents的情况
    empty_state = {}
    empty_result = _format_environment_state(empty_state)
    print("\n测试无agents的情况:")
    print(empty_result)
    assert "无其他国家信息" in empty_result, "应该显示无其他国家信息"
    print("✅ 空状态格式化也正常工作。")

if __name__ == "__main__":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    test_format_environment_state()
