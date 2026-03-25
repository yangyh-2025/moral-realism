"""
全局配置模块 - 对应技术方案4.1节配置数据结构

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from pydantic import BaseModel, Field, validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os
from dotenv import load_dotenv

# 加载 .env 文件（必须在导入 BaseSettings 之前调用）
load_dotenv()


# 系统常量
class Constants:
    """系统常量配置"""
    # HTTP客户端相关
    HTTP_TIMEOUT = 60.0  # HTTP请求超时时间（秒）
    HTTP_CLIENT_POOL_SIZE = 100  # 连接池大小

    # 缓存相关
    DECISION_CACHE_MAX_SIZE = 100  # 决策缓存最大条目数
    DECISION_CACHE_TTL = 3600  # 缓存生存时间（秒）
    LEARNING_MAX_OUTCOMES = 1000  # 学习机制最大结果记录数

    # 速率限制相关
    RATE_LIMIT_MAX_REQUESTS = 100  # 每分钟最大请求数
    RATE_LIMIT_WINDOW = 60  # 速率限制窗口（秒）
    RATE_LIMIT_CLEANUP_INTERVAL = 3600  # 清理间隔（秒）

    # 工作流相关
    WORKFLOW_PAUSE_TIMEOUT = 300  # 工作流暂停超时（秒，5分钟）
    WORKFLOW_POLL_INTERVAL = 0.1  # 状态轮询间隔（秒）

    # 验证相关
    MAX_ALLOWED_POWER_CHANGE = 5.0  # 5年累计最大实力变动（%）
    MIN_STRATEGIC_MATCH_SCORE = 0.3  # 最小战略匹配度

    # 数据验证相关
    MAX_AGENT_NAME_LENGTH = 100  # 智能体名称最大长度
    MAX_REGION_LENGTH = 50  # 区域名称最大长度
    MAX_LEADER_TYPE_LENGTH = 20  # 领导类型最大长度
    MIN_LEADER_TERM_ROUNDS = 1  # 最小领导人任期轮次
    MAX_LEADER_TERM_ROUNDS = 20  # 最大领导人任期轮次


class SimulationConfig(BaseSettings):
    """
    仿真配置类 - 对应技术方案4.1.1节 SimulationConfig

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    # 基础参数
    total_rounds: int = Field(default=100, ge=1, le=1000, description="仿真总轮次")
    round_duration_months: int = Field(default=6, ge=1, le=24, description="每轮次持续时间（月）")
    leader_term_rounds: int = Field(default=4, ge=1, description="领导人任期轮次")

    # LLM配置 - 使用SiliconFlow平台的DeepSeek-V3.2模型
    llm_provider: str = Field(default="siliconflow", description="LLM提供者")
    llm_model: str = Field(default="deepseek-ai/DeepSeek-V3.2", description="LLM模型名称")
    llm_api_keys: List[str] = Field(default_factory=list, description="API密钥列表，支持多key并行")
    llm_base_url: str = Field(default="https://api.siliconflow.cn/v1", description="LLM API基础URL")
    llm_temperature: float = Field(default=0.7, ge=0, le=2, description="LLM温度参数")
    llm_max_tokens: int = Field(default=4096, ge=100, le=8000, description="LLM最大token数")

    # 事件配置
    random_event_probability: float = Field(default=0.1, ge=0, le=1, description="随机事件触发概率")
    enable_user_events: bool = Field(default=True, description="是否启用用户自定义事件")

    # 存储配置
    database_path: str = Field(default="data/database.db", description="数据库文件路径")
    auto_save_interval: int = Field(default=5, ge=1, description="自动保存间隔（轮次）")

    model_config = SettingsConfigDict(
        env_prefix="MORAL_REALISM_",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator('llm_api_keys', mode='before')
    def load_api_keys(cls, v):
        """
        加载 API key 列表

        支持从 MORAL_REALISM_LLM_API_KEY（单数）或 MORAL_REALISM_LLM_API_KEYS（复数）加载
        """
        if not v:
            # 尝试从环境变量 MORAL_REALISM_LLM_API_KEY 加载
            api_key = os.getenv("MORAL_REALISM_LLM_API_KEY")
            if api_key:
                return [api_key]
        # 如果传入的是字符串，转换为列表
        if isinstance(v, str):
            return [v]
        return v if v else []


class AgentConfig(BaseModel):
    """
    智能体配置类 - 对应技术方案4.1.1节 AgentConfig

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com

    重要说明：
    - 超级大国、大国必须配置leader_type
    -    中等强国、小国不需要leader_type字段
    - power_metrics使用克莱因方程五要素
    """
    agent_id: str = Field(..., description="智能体唯一标识")
    name: str = Field(..., description="智能体名称")
    region: str = Field(..., description="所属区域")
    leader_type: Optional[str] = Field(None, description="领导类型（可选，仅大国需要）")

    # 克莱因方程五要素实力指标
    power_metrics: dict = Field(..., description="克莱因方程五要素实力指标")
