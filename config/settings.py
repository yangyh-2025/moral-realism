"""
全局配置模块 - 对应技术方案4.1节配置数据结构

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from
 pydantic import BaseModel, Field
from typing import List, Optional


class SimulationConfig(BaseModel):
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

    class Config:
        env_prefix = "MORAL_REALISM_"
        case_sensitive = False


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
