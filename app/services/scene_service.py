"""
预置场景管理服务
提供预设的国际体系场景配置，支持一键创建仿真项目
"""

from typing import List, Optional, Dict
from datetime import datetime

from app.services.project_service import project_service
from app.services.agent_service import agent_service, AgentConfigRequest
from app.services.strategic_relationship_service import StrategicRelationshipService
from app.models.strategic_relationship import StrategicRelationshipEnum
from app.config.database import db_config


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

    async def _create_scene1_agents(self, project_id: int) -> Dict[int, int]:
        """
        创建场景1（单极霸权体系）的智能体
        返回agent_id到到索引的映射：{index: agent_id}

        Returns:
            字典 {index: agent_id}
        """
        agent_map = {}

        # 1霸权国
        hegemon = await agent_service.add_agent(project_id, AgentConfigRequest(
            agent_name="国家1-霸权国",
            region="美洲",
            c_score=100,
            e_score=200,
            m_score=200,
            s_score=1.0,
            w_score=1.0,
            leader_type="霸权型"
        ))
        agent_map[1] = hegemon["agent_id"]

        # 1王道国
        wangdao = await agent_service.add_agent(project_id, AgentConfigRequest(
            agent_name="国家2-王道国",
            region="亚洲",
            c_score=95,
            e_score=180,
            m_score=170,
            s_score=0.9,
            w_score=0.9,
            leader_type="王道型"
        ))
        agent_map[2] = wangdao["agent_id"]

        # 1大国
        great_power = await agent_service.add_agent(project_id, AgentConfigRequest(
            agent_name="国家3-大国",
            region="欧洲",
            c_score=80,
            e_score=150,
            m_score=120,
            s_score=0.7,
            w_score=0.6,
            leader_type="强权型"
        ))
        agent_map[3] = great_power["agent_id"]

        # 4个中等强国
        for i in range(4):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+4}-中等强国",
                region="美洲" if i % 2 == 0 else "欧洲",
                c_score=30 + i * 2,
                e_score=50 + i * 5,
                m_score=40 + i * 3,
                s_score=0.5,
                w_score=0.5,
                leader_type=None
            ))
            agent_map[i+4] = agent["agent_id"]

        # 13个小国
        regions = ["亚洲", "欧洲", "美洲", "非洲", "大洋洲"]
        for i in range(13):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+8}-小国",
                region=regions[i % 5],
                c_score=15 + (i % 3) * 3,
                e_score=20 + (i % 4) * 3,
                m_score=15 + (i % 2) * 3,
                s_score=0.2 + (i % 3) * 0.1,
                w_score=0.2 + (i % 3) * 0.1,
                leader_type=None
            ))
            agent_map[i+8] = agent["agent_id"]

        return agent_map

    async def _create_scene2_agents(self, project_id: int) -> Dict[int, int]:
        """
        创建场景2（两极对抗体系）的智能体

        Returns:
            字典 {index: agent_id}
        """
        agent_map = {}

        # 1霸权国
        hegemon = await agent_service.add_agent(project_id, AgentConfigRequest(
            agent_name="国家1-霸权国",
            region="美洲",
            c_score=95,
            e_score=190,
            m_score=190,
            s_score=1.0,
            w_score=0.9,
            leader_type="霸权型"
        ))
        agent_map[1] = hegemon["agent_id"]

        # 1强权国
        strong_power = await agent_service.add_agent(project_id, AgentConfigRequest(
            agent_name="国家2-强权国",
            region="欧洲",
            c_score=90,
            e_score=180,
            m_score=185,
            s_score=1.0,
            w_score=0.9,
            leader_type="强权型"
        ))
        agent_map[2] = strong_power["agent_id"]

        # 2个大国
        for i in range(2):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+3}-大国",
                region="亚洲" if i == 0 else "欧洲",
                c_score=75 - i * 5,
                e_score=140 - i * 10,
                m_score=130 - i * 10,
                s_score=0.7,
                w_score=0.7,
                leader_type="王道型" if i == 0 else "强权型"
            ))
            agent_map[i+3] = agent["agent_id"]

        # 4个中等强国
        for i in range(4):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+5}-中等强国",
                region="亚洲" if i % 2 == 0 else "欧洲",
                c_score=28 + i * 2,
                e_score=45 + i * 5,
                m_score=35 + i * 3,
                s_score=0.5,
                w_score=0.5,
                leader_type=None
            ))
            agent_map[i+5] = agent["agent_id"]

        # 12个小国
        regions = ["亚洲", "欧洲", "美洲", "非洲", "大洋洲"]
        for i in range(12):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+9}-小国",
                region=regions[i % 5],
                c_score=12 + (i % 3) * 3,
                e_score=18 + (i % 4) * 3,
                m_score=14 + (i % 2) * 3,
                s_score=0.2 + (i % 3) * 0.1,
                w_score=0.2 + (i % 3) * 0.1,
                leader_type=None
            ))
            agent_map[i+9] = agent["agent_id"]

        return agent_map

    async def _create_scene3_agents(self, project_id: int) -> Dict[int, int]:
        """
        创建场景3（多极平衡体系）的智能体

        Returns:
            字典 {index: agent_id}
        """
        agent_map = {}

        # 3个大国
        for i, (region, lt, c, e, m) in enumerate([
            ("美洲", "霸权型", 90, 180, 180),
            ("亚洲", "王道型", 90, 175, 170),
            ("欧洲", "强权型", 75, 140, 130)
        ]):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+1}-大国",
                region=region,
                c_score=c,
                e_score=e,
                m_score=m,
                s_score=0.9 if i < 2 else 0.7,
                w_score=0.9 if i < 2 else 0.7,
                leader_type=lt
            ))
            agent_map[i+1] = agent["agent_id"]

        # 5个中等强国
        for i in range(5):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+4}-中等强国",
                region=["欧洲", "亚洲", "美洲", "亚洲", "欧洲"][i],
                c_score=32 - i * 2,
                e_score=50 - i * 3,
                m_score=40 - i * 3,
                s_score=0.5,
                w_score=0.5,
                leader_type=None
            ))
            agent_map[i+4] = agent["agent_id"]

        # 12个小国
        regions = ["亚洲", "欧洲", "美洲", "非洲", "大洋洲"]
        for i in range(12):
            agent = await agent_service.add_agent(project_id, AgentConfigRequest(
                agent_name=f"国家{i+9}-小国",
                region=regions[i % 5],
                c_score=18 + (i % 3) * 3,
                e_score=25 + (i % 4) * 3,
                m_score=20 + (i % 2) * 3,
                s_score=0.3 + (i % 3) * 0.05,
                w_score=0.3 + (i % 3) * 0.05,
                leader_type=None
            ))
            agent_map[i+9] = agent["agent_id"]

        return agent_map

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

        # 根据场景ID创建智能体并获取索引到agent_id的映射
        if scene_id == 1:
            agent_map = await self._create_scene1_agents(project_id)
        elif scene_id == 2:
            agent_map = await self._create_scene2_agents(project_id)
        elif scene_id == 3:
            agent_map = await self._create_scene3_agents(project_id)
        else:
            agent_map = {}

        # 初始化战略关系
        async for session in db_config.get_session():
            sr_service = StrategicRelationshipService(session)

            # 先初始化所有允许的配对关系（大国/超级大国 × 中小国家）
            await sr_service.initialize_relationships(project_id)

            # 根据场景设置特定的战略关系
            if scene_id == 1:
                # 单极霸权体系 - 1霸权国(1) + 1王道国(2) + 1大国(3) + 4中等强国(4-7) + 13小国(8-20)
                hegemon = agent_map.get(1)    # 霸权国
                wangdao = agent_map.get(2)    # 王道国
                great_power = agent_map.get(3)  # 大国
                middle_powers = [agent_map.get(i) for i in range(4, 8)]   # 4个中等强国
                small_states = [agent_map.get(i) for i in range(8, 21)]   # 13个小国

                # 大国之间的关系
                if hegemon and wangdao:
                    await sr_service.set_relationship(project_id, hegemon, wangdao, StrategicRelationshipEnum.CONFLICT)
                if hegemon and great_power:
                    await sr_service.set_relationship(project_id, hegemon, great_power, StrategicRelationshipEnum.CONFLICT)
                if wangdao and great_power:
                    await sr_service.set_relationship(project_id, wangdao, great_power, StrategicRelationshipEnum.PARTNERSHIP)

                # 霸权国与中小国家：部分盟友，部分冲突
                for i, mid_id in enumerate(middle_powers):
                    if mid_id:
                        rel = StrategicRelationshipEnum.ALLIANCE if i < 2 else StrategicRelationshipEnum.CONFLICT
                        await sr_service.set_relationship(project_id, hegemon, mid_id, rel)
                for i, small_id in enumerate(small_states):
                    if small_id:
                        rel = StrategicRelationshipEnum.PARTNERSHIP if i < 5 else StrategicRelationshipEnum.NO_DIPLOMACY
                        await sr_service.set_relationship(project_id, hegemon, small_id, rel)

                # 王道国与中小国家：主要是伙伴关系
                for mid_id in middle_powers:
                    if mid_id:
                        await sr_service.set_relationship(project_id, wangdao, mid_id, StrategicRelationshipEnum.PARTNERSHIP)
                for i, small_id in enumerate(small_states):
                    if small_id:
                        rel = StrategicRelationshipEnum.PARTNERSHIP if i < 8 else StrategicRelationshipEnum.NO_DIPLOMACY
                        await sr_service.set_relationship(project_id, wangdao, small_id, rel)

                # 大国与中小国家：混合关系
                for i, mid_id in enumerate(middle_powers):
                    if mid_id:
                        rel = StrategicRelationshipEnum.CONFLICT if i < 2 else StrategicRelationshipEnum.PARTNERSHIP
                        await sr_service.set_relationship(project_id, great_power, mid_id, rel)
                for i, small_id in enumerate(small_states):
                    if small_id:
                        rel = StrategicRelationshipEnum.NO_DIPLOMACY if i < 6 else StrategicRelationshipEnum.PARTNERSHIP
                        await sr_service.set_relationship(project_id, great_power, small_id, rel)

            elif scene_id == 2:
                # 两极对抗体系 - 1霸权国(1) + 1强权国(2) + 2大国(3-4) + 4中等强国(5-8) + 12小国(9-20)
                hegemon = agent_map.get(1)    # 霸权国
                strong_power = agent_map.get(2)  # 强权国
                great_powers = [agent_map.get(i) for i in range(3, 5)]   # 2个大国
                middle_powers = [agent_map.get(i) for i in range(5, 9)]   # 4个中等强国
                small_states = [agent_map.get(i) for i in range(9, 21)]  # 12个小国

                # 大国之间的关系：阵营对抗
                if hegemon and strong_power:
                    await sr_service.set_relationship(project_id, hegemon, strong_power, StrategicRelationshipEnum.WAR)
                if hegemon and great_powers[0]:
                    await sr_service.set_relationship(project_id, hegemon, great_powers[0], StrategicRelationshipEnum.ALLIANCE)
                if hegemon and great_powers[1]:
                    await sr_service.set_relationship(project_id, hegemon, great_powers[1], StrategicRelationshipEnum.CONFLICT)
                if strong_power and great_powers[0]:
                    await sr_service.set_relationship(project_id, strong_power, great_powers[0], StrategicRelationshipEnum.CONFLICT)
                if strong_power and great_powers[1]:
                    await sr_service.set_relationship(project_id, strong_power, great_powers[1], StrategicRelationshipEnum.ALLIANCE)
                if great_powers[0] and great_powers[1]:
                    await sr_service.set_relationship(project_id, great_powers[0], great_powers[1], StrategicRelationshipEnum.NO_DIPLOMACY)

                # 霸权国阵营与中小国家：盟友关系为主
                for mid_id in middle_powers:
                    if mid_id:
                        await sr_service.set_relationship(project_id, hegemon, mid_id, StrategicRelationshipEnum.ALLIANCE)
                for small_id in small_states:
                    if small_id:
                        await sr_service.set_relationship(project_id, hegemon, small_id, StrategicRelationshipEnum.PARTNERSHIP)

                # 强权国阵营与中小国家：盟友关系为主
                for i, mid_id in enumerate(middle_powers):
                    if mid_id:
                        rel = StrategicRelationshipEnum.ALLIANCE if i < 3 else StrategicRelationshipEnum.CONFLICT
                        await sr_service.set_relationship(project_id, strong_power, mid_id, rel)
                for i, small_id in enumerate(small_states):
                    if small_id:
                        rel = StrategicRelationshipEnum.PARTNERSHIP if i < 8 else StrategicRelationshipEnum.CONFLICT
                        await sr_service.set_relationship(project_id, strong_power, small_id, rel)

                # 两极各自阵营的盟友关系
                for gp_id in great_powers:
                    for i, mid_id in enumerate(middle_powers):
                        if gp_id and mid_id:
                            rel = StrategicRelationshipEnum.ALLIANCE if i < 2 else StrategicRelationshipEnum.NO_DIPLOMACY
                            await sr_service.set_relationship(project_id, gp_id, mid_id, rel)

            elif scene_id == 3:
                # 多极平衡体系 - 3大国(1-3) + 5中等强国(4-8) + 12小国(9-20)
                great_powers = [agent_map.get(i) for i in range(1, 4)]   # 3个大国
                middle_powers = [agent_map.get(i) for i in range(4, 9)]   # 5个中等强国
                small_states = [agent_map.get(i) for i in range(9, 21)]  # 12个小国

                # 大国之间的关系：伙伴与冲突交织
                if great_powers[0] and great_powers[1]:
                    await sr_service.set_relationship(project_id, great_powers[0], great_powers[1], StrategicRelationshipEnum.PARTNERSHIP)
                if great_powers[0] and great_powers[2]:
                    await sr_service.set_relationship(project_id, great_powers[0], great_powers[2], StrategicRelationshipEnum.CONFLICT)
                if great_powers[1] and great_powers[2]:
                    await sr_service.set_relationship(project_id, great_powers[1], great_powers[2], StrategicRelationshipEnum.PARTNERSHIP)

                # 大国与中小国家：多元化的战略关系
                for i, gp_id in enumerate(great_powers):
                    for j, mid_id in enumerate(middle_powers):
                        if gp_id and mid_id:
                            # 交替设置关系：盟友、伙伴、冲突、无外交
                            rel_types = [StrategicRelationshipEnum.ALLIANCE, StrategicRelationshipEnum.PARTNERSHIP,
                                         StrategicRelationshipEnum.CONFLICT, StrategicRelationshipEnum.NO_DIPLOMACY]
                            await sr_service.set_relationship(project_id, gp_id, mid_id, rel_types[(i + j) % 4])

                    for j, small_id in enumerate(small_states):
                        if gp_id and small_id:
                            # 交替设置关系：伙伴、无外交
                            rel = StrategicRelationshipEnum.PARTNERSHIP if (i + j) % 2 == 0 else StrategicRelationshipEnum.NO_DIPLOMACY
                            await sr_service.set_relationship(project_id, gp_id, small_id, rel)

        return {
            "project_id": project_id,
            "project_name": project["project_name"],
            "status": project["status"]
        }


# 单例实例
scene_service = SceneService()
