"""
测试 .env 配置加载是否正确
"""
import os
import sys
from dotenv import load_dotenv

# Windows console encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加载 .env 文件
load_dotenv()

print("=" * 60)
print("环境变量配置测试")
print("=" * 60)

# 测试关键配置项
configs = [
    ("MORAL_REALISM_LLM_API_KEY", "LLM API 密钥"),
    ("MORAL_REALISM_LLM_PROVIDER", "LLM 提供者"),
    ("MORAL_REALISM_LLM_MODEL", "LLM 模型"),
    ("MORAL_REALISM_LLM_BASE_URL", "LLM API 基础 URL"),
    ("MORAL_REALISM_LLM_TEMPERATURE", "LLM 温度参数"),
    ("MORAL_REALISM_LLM_MAX_TOKENS", "LLM 最大 token 数"),
    ("MORAL_REALISM_TOTAL_ROUNDS", "仿真总轮次"),
    ("MORAL_REALISM_ROUND_DURATION_MONTHS", "每轮持续时间（月）"),
    ("MORAL_REALISM_LEADER_TERM_ROUNDS", "领导人任期轮次"),
    ("MORAL_REALISM_LOG_LEVEL", "日志级别"),
    ("MORAL_REALISM_LOG_FILE", "日志文件路径"),
    ("APP_ENV", "应用环境"),
    ("API_HOST", "API 主机地址"),
    ("API_PORT", "API 端口"),
]

all_ok = True
for env_var, desc in configs:
    value = os.getenv(env_var)
    if value:
        # 脱敏敏感信息
        display_value = value if "KEY" not in env_var and "PASSWORD" not in env_var else f"{value[:10]}...{value[-4:]}"
        print(f"✅ {desc:30s} | {env_var:40s} = {display_value}")
    else:
        print(f"❌ {desc:30s} | {env_var:40s} = (未设置)")
        all_ok = False

print("=" * 60)

# 测试 Pydantic Settings 加载
print("\n测试 Pydantic Settings 配置加载:")
print("-" * 60)

try:
    from config.settings import SimulationConfig

    # 从环境变量创建配置
    config = SimulationConfig()

    print(f"✅ total_rounds = {config.total_rounds}")
    print(f"✅ round_duration_months = {config.round_duration_months}")
    print(f"✅ leader_term_rounds = {config.leader_term_rounds}")
    print(f"✅ llm_provider = {config.llm_provider}")
    print(f"✅ llm_model = {config.llm_model}")
    print(f"✅ llm_base_url = {config.llm_base_url}")
    print(f"✅ llm_temperature = {config.llm_temperature}")
    print(f"✅ llm_max_tokens = {config.llm_max_tokens}")
    print(f"✅ llm_api_keys (数量) = {len(config.llm_api_keys)}")
    if config.llm_api_keys:
        print(f"   - 第一个 key: {config.llm_api_keys[0][:10]}...{config.llm_api_keys[0][-4:]}")
    print(f"✅ random_event_probability = {config.random_event_probability}")
    print(f"✅ database_path = {config.database_path}")
    print(f"✅ auto_save_interval = {config.auto_save_interval}")

except Exception as e:
    print(f"❌ 加载 Pydantic Settings 失败: {e}")
    all_ok = False

print("=" * 60)

if all_ok:
    print("\n✅ 所有配置项加载成功！")
else:
    print("\n❌ 部分配置项加载失败，请检查 .env 文件")
