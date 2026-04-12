# Agent Service
from typing import List, Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """智能体配置模型"""
    agent_name: str
    region: str
    c_score: float = Field(ge=0, le=100, description="基本实体得分 0-100")
    e_score: float = Field(ge=0, le=200, description="经济实力 0-200")
    m_score: float = Field(ge=0, le=200, description="军事实力 0-200")
    s_score: float = Field(ge=0, le=2, description="战略目的系数 0-2")
    w_score: float = Field(ge=0, le=2, description="战略意志系数 0-2")
    leader_type: Optional[str] = None


class AgentService:
    """智能体管理服务"""

    def calculate_total_power(self, c_score: float, e_score: float, m_score: float,
                           s_score: float, w_score: float) -> float:
        """
        计算综合国力（克莱因方程）
        Pp = (C + E + M) × (S + W)
        """
        return (c_score + e_score + m_score) * (s_score + w_score)

    def determine_power_level(self, total_power: float) -> str:
        """
        判定实力层级
        """
        if total_power >= 500:
            return "超级大国"
        elif 200 <= total_power < 500:
            return "大国"
        elif 100 <= total_power < 200:
            return "中等强国"
        else:
            return "小国"

    async def add_agent(self, project_id: int, config: AgentConfig) -> dict:
        """
        为项目添加智能体
        """
        # Calculate initial power and level
        initial_power = self.calculate_total_power(
            config.c_score, config.e_score, config.m_score,
            config.s_score, config.w_score
        )
        power_level = self.determine_power_level(initial_power)

        # Validate leader type (only for superpowers and great powers)
        if config.leader_type and power_level not in ["超级大国", "大国"]:
            raise ValueError("仅超级大国与大国可配置领导集体类型")

        # TODO: Implement actual database operations
        return {
            "agent_id": 1,
            "agent_name": config.agent_name,
            "region": config.region,
            "c_score": config.c_score,
            "e_score": config.e_score,
            "m_score": config.m_score,
            "s_score": config.s_score,
            "w_score": config.w_score,
            "initial_total_power": initial_power,
            "current_total_power": initial_power,
            "power_level": power_level,
            "leader_type": config.leader_type
        }

    async def get_agents(self, project_id: int, power_level_filter: Optional[str] = None,
                       region_filter: Optional[str] = None) -> List[dict]:
        """
        获取项目智能体列表
        """
        # TODO: Implement actual database operations
        return []

    async def get_agent(self, project_id: int, agent_id: int) -> Optional[dict]:
        """
        获取智能体详情
        """
        # TODO: Implement actual database operations
        return None

    async def update_agent(self, project_id: int, agent_id: int, config: AgentConfig) -> Optional[dict]:
        """
        更新智能体初始配置
        """
        # TODO: Implement actual database operations
        return None

    async def delete_agent(self, project_id: int, agent_id: int) -> bool:
        """
        删除智能体
        """
        # TODO: Implement actual database operations
        return True

    async def update_agent_power(self, agent_id: int, power_change: float) -> Optional[dict]:
        """
        更新智能体实时国力
        """
        # TODO: Implement actual database operations
        # Validate power change constraint: |change| <= 10
        if abs(power_change) > 10:
            raise ValueError("单次行为国力变动绝对值不能超过10分")

        return None


# Singleton instance
agent_service = AgentService()
