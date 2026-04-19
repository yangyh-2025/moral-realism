"""
预置场景管理服务
提供预设的国际体系场景配置，支持一键创建仿真项目
"""

from typing import List, Optional
from datetime import datetime

from app.services.project_service import project_service
from app.services.agent_service import agent_service, AgentConfigRequest


class SceneService:
    """
    预置场景管理服务

    提供预设的国际体系场景配置，支持：
    - 单极霸权体系
    - 两极对抗体系
    - 多极平衡体系
    """

    async def get_preset_scenes(self) -> List[dict]:
        """
        获取所有预置仿真场景列表

        Returns:
            预置场景列表
        """
        return [
            {
                "scene_id": 1,
                "scene_name": "单极霸权体系",
                "scene_desc": "模拟单极体系下超级大国霸权维持与新兴大国挑战的动态博弈",
                "total_rounds": 50,
                "agent_config_json": '{"agents": []}',
                "is_default": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "scene_id": 2,
                "scene_name": "两极对抗体系",
                "scene_desc": "模拟两极体系下超级大国间的战略竞争与盟友追随动态",
                "total_rounds": 50,
                "agent_config_json": '{"agents": []}',
                "is_default": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "scene_id": 3,
                "scene_name": "多极平衡体系",
                "scene_desc": "模拟多极体系下大国间的复杂博弈与中小国家的摇摆行为",
                "total_rounds": 50,
                "agent_config_json": '{"agents": []}',
                "is_default": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]

    async def get_preset_scene(self, scene_id: int) -> Optional[dict]:
        """
        获取单个场景详情

        Args:
            scene_id: 场景ID

        Returns:
            场景详情字典，或None（如果不存在）
        """
        scenes = await self.get_preset_scenes()
        for scene in scenes:
            if scene["scene_id"] == scene_id:
                return scene
        return None

    async def create_project_from_scene(self, scene_id: int, project_name: Optional[str] = None,
                                     project_desc: Optional[str] = None) -> dict:
        """
        从预置场景一键创建仿真项目

        根据选择的场景类型创建项目并自动配置智能体：
        - 单极霸权体系：1霸权+1王道+1大国+4中等强国+13小国
        - 两极对抗体系：1霸权+1强权+2大国+4中等强国+12小国
        - 多极平衡体系：3大国+5中等强国+12小国

        Args:
            scene_id: 场景ID
            project_name: 项目名称（可选，默认从场景生成）
            project_desc: 项目描述（可选，默认从场景生成）

        Returns:
            创建的项目信息字典
        """
        scene = await self.get_preset_scene(scene_id)
        if not scene:
            return None

        # 创建项目
        project = await project_service.create_project(
            project_name=project_name or f"Project from {scene['scene_name']}",
            project_desc=project_desc or scene["scene_desc"],
            total_rounds=scene["total_rounds"],
            scene_source=scene["scene_name"]
        )

        project_id = project["project_id"]

        # 根据场景ID添加不同配置的智能体
        if scene_id == 1:
            # 单极霸权体系：1霸权+1王道+1大国+4中等强国+13小国
            await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name="国家1-霸权国",
                region="美洲",
                c_score=100,
                e_score=200,
                m_score=200,
                s_score=1.0,
                w_score=1.0,
                leader_type="霸权型"
            ))
            await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name="国家2-王道国",
                region="亚洲",
                c_score=95,
                e_score=180,
                m_score=170,
                s_score=0.9,
                w_score=0.9,
                leader_type="王道型"
            ))
            await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name="国家3-大国",
                region="欧洲",
                c_score=80,
                e_score=150,
                m_score=120,
                s_score=0.7,
                w_score=0.6,
                leader_type="强权型"
            ))
            # 4个中等强国 - 调整到100-200国力范围
            for i in range(4):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+4}-中等强国",
                    region="美洲" if i % 2 == 0 else "欧洲",
                    c_score=30 + i * 2,
                    e_score=50 + i * 5,
                    m_score=40 + i * 3,
                    s_score=0.5,
                    w_score=0.5,
                    leader_type=None
                ))
            # 13个小国
            regions = ["亚洲", "欧洲", "美洲", "非洲", "大洋洲"]
            for i in range(13):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+8}-小国",
                    region=regions[i % 5],
                    c_score=15 + (i % 3) * 3,
                    e_score=20 + (i % 4) * 3,
                    m_score=15 + (i % 2) * 3,
                    s_score=0.2 + (i % 3) * 0.1,
                    w_score=0.2 + (i % 3) * 0.1,
                    leader_type=None
                ))

        elif scene_id == 2:
            # 两极对抗体系：1霸权+1强权+2大国+4中等强国+12小国
            await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name="国家1-霸权国",
                region="美洲",
                c_score=95,
                e_score=190,
                m_score=190,
                s_score=1.0,
                w_score=0.9,
                leader_type="霸权型"
            ))
            await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name="国家2-强权国",
                region="欧洲",
                c_score=90,
                e_score=180,
                m_score=185,
                s_score=1.0,
                w_score=0.9,
                leader_type="强权型"
            ))
            # 2个大国
            for i in range(2):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+3}-大国",
                    region="亚洲" if i == 0 else "欧洲",
                    c_score=75 - i * 5,
                    e_score=140 - i * 10,
                    m_score=130 - i * 10,
                    s_score=0.7,
                    w_score=0.7,
                    leader_type="王道型" if i == 0 else "强权型"
                ))
            # 4个中等强国 - 调整到100-200国力范围
            for i in range(4):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+5}-中等强国",
                    region="亚洲" if i % 2 == 0 else "欧洲",
                    c_score=28 + i * 2,
                    e_score=45 + i * 5,
                    m_score=35 + i * 3,
                    s_score=0.5,
                    w_score=0.5,
                    leader_type=None
                ))
            # 12个小国
            regions = ["亚洲", "欧洲", "美洲", "非洲", "大洋洲"]
            for i in range(12):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+9}-小国",
                    region=regions[i % 5],
                    c_score=12 + (i % 3) * 3,
                    e_score=18 + (i % 4) * 3,
                    m_score=14 + (i % 2) * 3,
                    s_score=0.2 + (i % 3) * 0.1,
                    w_score=0.2 + (i % 3) * 0.1,
                    leader_type=None
                ))

        elif scene_id == 3:
            # 多极平衡体系：3大国+5中等强国+12小国
            # 3个大国
            for i, (region, lt, c, e, m) in enumerate([
                ("美洲", "霸权型", 90, 180, 180),
                ("亚洲", "王道型", 90, 175, 170),
                ("欧洲", "强权型", 75, 140, 130)
            ]):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+1}-大国",
                    region=region,
                    c_score=c,
                    e_score=e,
                    m_score=m,
                    s_score=0.9 if i < 2 else 0.7,
                    w_score=0.9 if i < 2 else 0.7,
                    leader_type=lt
                ))
            # 5个中等强国 - 调整到100-200国力范围
            for i in range(5):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+4}-中等强国",
                    region=["欧洲", "亚洲", "美洲", "亚洲", "欧洲"][i],
                    c_score=32 - i * 2,
                    e_score=50 - i * 3,
                    m_score=40 - i * 3,
                    s_score=0.5,
                    w_score=0.5,
                    leader_type=None
                ))
            # 12个小国
            regions = ["亚洲", "欧洲", "美洲", "非洲", "大洋洲"]
            for i in range(12):
                await agent_service.add_agent(project_id, AgentConfigRequest(
                    agent_name=f"国家{i+9}-小国",
                    region=regions[i % 5],
                    c_score=18 + (i % 3) * 3,
                    e_score=25 + (i % 4) * 3,
                    m_score=20 + (i % 2) * 3,
                    s_score=0.3 + (i % 3) * 0.05,
                    w_score=0.3 + (i % 3) * 0.05,
                    leader_type=None
                ))

        return {
            "project_id": project_id,
            "project_name": project["project_name"],
            "status": project["status"]
        }


# 单例实例
scene_service = SceneService()
