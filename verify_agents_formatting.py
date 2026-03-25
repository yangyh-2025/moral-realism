#!/usr/bin/env python3
"""
简单的测试脚本来验证 decision_engine 中 agents 字段的格式化
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from application.decision.decision_engine import DecisionEngine
from domain.environment.environment_engine import EnvironmentEngine
from domain.power.power_metrics import PowerMetrics, PowerTier
from domain.agents.small_power import SmallPowerAgent

# 创建测试智能体
def create_test_agents():
    agents = []

    # 创建国家1 - 小国
    pm1 = PowerMetrics(
        critical_mass=30.0,
        economic_capability=40.0,
        military_capability=20.0,
        strategic_purpose=0.5,
        national_will=0.6
    )
    agent1 = SmallPowerAgent("country_1", "测试国1", "东亚", pm1)
    agent1.power_tier = PowerTier.SMALL_POWER
    agent1.complete_initialization()
    agents.append(agent1)

    # 创建国家2 - 中等国家
    pm2 = PowerMetrics(
        critical_mass=60.0,
        economic_capability=70.0,
        military_capability=50.0,
        strategic_purpose=0.7,
        national_will=0.8
    )
    agent2 = SmallPowerAgent("country_2", "测试国2", "东南亚", pm2)
    agent2.power_tier = PowerTier.MIDDLE_POWER
    agent2.complete_initialization()
    agents.append(agent2)

    return agents

def test_decision_engine_agents_formatting():
    print("测试 decision_engine 中 agents 字段的格式化...")

    # 创建环境引擎
    env = EnvironmentEngine()

    # 创建测试智能体
    agents = create_test_agents()
    print(f"创建了 {len(agents)} 个测试智能体")

    # 设置智能体
    env.set_agents(agents)
    print("已设置智能体到环境引擎")

    # 获取完整状态
    state = env.get_full_state()
    print("获取完整状态成功")

    # 创建决策引擎实例（使用模拟的依赖项）
    class MockLLMEngine:
        def __init__(self, provider, event_pusher, simulation_id):
            pass

    class MockProvider:
        def __init__(self, api_key, base_url, model):
            pass

    class MockValidator:
        def __init__(self):
            pass

    class MockStorage:
        def __init__(self):
            pass

    class MockLogger:
        def __init__(self, log_dir):
            pass

        def log_decision(self, **kwargs):
            pass

    class MockEventPusher:
        class Manager:
            def broadcast_to_simulation(self, simulation_id, message):
                pass

        @property
        def manager(self):
            return self.Manager()

    # 创建决策引擎
    from infrastructure.validation.validator import RuleValidator
    from infrastructure.logging.logger import EnhancedLogger
    from infrastructure.llm.llm_engine import LLMEngine
    from infrastructure.llm.silicon_flow_provider import SiliconFlowProvider

    decision_engine = DecisionEngine(
        llm_engine=MockLLMEngine(None, None, None),
        validator=RuleValidator(),
        storage=MockStorage(),
        logger=MockLogger("logs/test")
    )

    # 测试 _format_environment_state 方法
    print("\n测试 _format_environment_state 方法:")
    formatted_state = decision_engine._format_environment_state(state)
    print("格式化后的状态:")
    print(formatted_state)

    print("\n✅ 格式化方法测试通过！")

    # 验证格式化后的内容
    assert "其他国家情况" in formatted_state
    assert "测试国1" in formatted_state
    assert "测试国2" in formatted_state
    assert "东亚" in formatted_state or "东南亚" in formatted_state  # 可能在详细信息中
    print("✓ 包含所有国家的基本信息")

    # 检查是否有实力信息
    assert "实力=" in formatted_state
    print("✓ 包含实力信息")

    print("\n✅ 所有测试通过！_format_environment_state 方法能够正确格式化 agents 字段。")

if __name__ == "__main__":
    test_decision_engine_agents_formatting()
