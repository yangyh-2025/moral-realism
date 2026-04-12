# Scene Service
from typing import List, Optional
from datetime import datetime


class SceneService:
    """预置场景管理服务"""

    async def get_preset_scenes(self) -> List[dict]:
        """
        获取所有预置仿真场景列表
        """
        # TODO: Implement actual database operations
        # Return 3 classic preset scenes
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
        """
        scene = await self.get_preset_scene(scene_id)
        if not scene:
            return None

        # TODO: Implement actual project creation with scene configuration
        return {
            "project_id": 1,
            "project_name": project_name or f"Project from {scene['scene_name']}",
            "project_desc": project_desc or scene["scene_desc"],
            "status": "未启动"
        }


# Singleton instance
scene_service = SceneService()
