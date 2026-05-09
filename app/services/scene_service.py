"""
预置场景管理服务（CINC版）
提供基于CINC真实历史数据的预设国际体系场景配置，支持一键创建仿真项目
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime

from app.services.project_service import project_service
from app.services.agent_service import agent_service, AgentConfigRequest
from app.services.strategic_relationship_service import StrategicRelationshipService
from app.models.strategic_relationship import StrategicRelationshipEnum
from app.config.database import db_config


class SceneService:
    """
    预置场景管理服务（CINC版）

    提供基于CINC真实历史数据的预设国际体系场景配置：
    - 一战前欧洲（1913年，19国）
    - 二战前欧洲（1938年，28国）
    - 冷战前欧洲（1946年，25国）
    """

    async def get_preset_scenes(self) -> List[dict]:
        """
        获取所有预置仿真场景列表

        优先从数据库查询，若数据库无数据则回退到硬编码数据。

        Returns:
            预置场景列表
        """
        from app.models import PresetScene
        from sqlalchemy import select

        # 优先从数据库查询
        async for session in db_config.get_session():
            result = await session.execute(select(PresetScene))
            db_scenes = result.scalars().all()
            if db_scenes:
                return [
                    {
                        "scene_id": s.scene_id,
                        "scene_name": s.scene_name,
                        "scene_desc": s.scene_desc,
                        "total_rounds": s.total_rounds,
                        "agent_config_json": s.agent_config_json,
                        "is_default": s.is_default,
                        "created_at": s.created_at,
                        "updated_at": s.updated_at,
                    }
                    for s in db_scenes
                ]

        # 数据库无数据时回退到硬编码数据
        return [
            {
                "scene_id": 1,
                "scene_name": "一战前欧洲（1913）",
                "scene_desc": "基于1913年CINC真实数据的欧洲国际体系，包含19个国家。德国崛起、英俄结盟、巴尔干危机...",
                "total_rounds": 50,
                "agent_config_json": '{"agents": []}',
                "is_default": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "scene_id": 2,
                "scene_name": "二战前欧洲（1938）",
                "scene_desc": "基于1938年CINC真实数据的欧洲国际体系，包含28个国家。苏德对抗、张伯伦绥靖、轴心国体系...",
                "total_rounds": 50,
                "agent_config_json": '{"agents": []}',
                "is_default": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "scene_id": 3,
                "scene_name": "冷战前欧洲（1946）",
                "scene_desc": "基于1946年CINC真实数据的欧洲国际体系，包含25个国家。苏英对立、铁幕降临、马歇尔计划前夜...",
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
        from app.models import PresetScene
        from sqlalchemy import select

        # 优先从数据库查询
        async for session in db_config.get_session():
            result = await session.execute(
                select(PresetScene).where(PresetScene.scene_id == scene_id)
            )
            db_scene = result.scalar_one_or_none()
            if db_scene:
                return {
                    "scene_id": db_scene.scene_id,
                    "scene_name": db_scene.scene_name,
                    "scene_desc": db_scene.scene_desc,
                    "total_rounds": db_scene.total_rounds,
                    "agent_config_json": db_scene.agent_config_json,
                    "is_default": db_scene.is_default,
                    "created_at": db_scene.created_at,
                    "updated_at": db_scene.updated_at,
                }

        # 数据库无数据时回退到硬编码数据
        scenes = await self.get_preset_scenes()
        for scene in scenes:
            if scene["scene_id"] == scene_id:
                return scene
        return None

    # ------------------------------------------------------------------
    # 场景1：一战前欧洲（1913年，19国）
    # ------------------------------------------------------------------
    async def _create_scene1_agents(self, project_id: int) -> Dict[int, int]:
        """
        创建场景1（一战前欧洲1913）的智能体
        返回 {index: agent_id}
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()
        YEAR = 1913

        countries: List[Tuple[str, str, Optional[str]]] = [
            ("强国甲", "GMY", "霸权型"),
            ("强国乙", "RUS", "强权型"),
            ("强国丙", "UKG", "王道型"),
            ("中等国甲", "FRN", None),
            ("中等国乙", "AUH", None),
            ("中等国丙", "ITA", None),
            ("小国甲", "TUR", None),
            ("小国乙", "BUL", None),
            ("小国丙", "SPN", None),
            ("小国丁", "BEL", None),
            ("小国戊", "GRC", None),
            ("小国己", "SWD", None),
            ("小国庚", "NTH", None),
            ("小国辛", "ROM", None),
            ("小国壬", "POR", None),
            ("小国癸", "DEN", None),
            ("小国子", "SWZ", None),
            ("小国丑", "YUG", None),
            ("小国寅", "NOR", None),
        ]

        return await self._create_agents_from_cinc(project_id, loader, YEAR, countries)

    # ------------------------------------------------------------------
    # 场景2：二战前欧洲（1938年，28国）
    # ------------------------------------------------------------------
    async def _create_scene2_agents(self, project_id: int) -> Dict[int, int]:
        """
        创建场景2（二战前欧洲1938）的智能体
        返回 {index: agent_id}
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()
        YEAR = 1938

        countries: List[Tuple[str, str, Optional[str]]] = [
            ("强国甲", "RUS", "强权型"),
            ("强国乙", "GMY", "霸权型"),
            ("强国丙", "UKG", "王道型"),
            ("中等国甲", "FRN", None),
            ("中等国乙", "ITA", "霸权型"),
            ("中等国丙", "POL", None),
            ("小国甲", "SPN", None),
            ("小国乙", "CZE", None),
            ("小国丙", "BEL", None),
            ("小国丁", "ROM", None),
            ("小国戊", "TUR", None),
            ("小国己", "YUG", None),
            ("小国庚", "SWD", None),
            ("小国辛", "NTH", None),
            ("小国壬", "HUN", None),
            ("小国癸", "GRC", None),
            ("小国子", "POR", None),
            ("小国丑", "LUX", None),
            ("小国寅", "DEN", None),
            ("小国卯", "FIN", None),
            ("小国辰", "SWZ", None),
            ("小国巳", "BUL", None),
            ("小国午", "NOR", None),
            ("小国未", "LAT", None),
            ("小国申", "LIT", None),
            ("小国酉", "IRE", None),
            ("小国戌", "EST", None),
            ("小国亥", "ALB", None),
        ]

        return await self._create_agents_from_cinc(project_id, loader, YEAR, countries)

    # ------------------------------------------------------------------
    # 场景3：冷战前欧洲（1946年，25国）
    # ------------------------------------------------------------------
    async def _create_scene3_agents(self, project_id: int) -> Dict[int, int]:
        """
        创建场景3（冷战前欧洲1946）的智能体
        返回 {index: agent_id}
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()
        YEAR = 1946

        countries: List[Tuple[str, str, Optional[str]]] = [
            ("强国甲", "RUS", "强权型"),
            ("强国乙", "UKG", "王道型"),
            ("中等国甲", "FRN", None),
            ("中等国乙", "ITA", None),
            ("中等国丙", "POL", None),
            ("小国甲", "SPN", None),
            ("小国乙", "TUR", None),
            ("小国丙", "CZE", None),
            ("小国丁", "BEL", None),
            ("小国戊", "NTH", None),
            ("小国己", "SWD", None),
            ("小国庚", "YUG", None),
            ("小国辛", "ROM", None),
            ("小国壬", "HUN", None),
            ("小国癸", "GRC", None),
            ("小国子", "BUL", None),
            ("小国丑", "POR", None),
            ("小国寅", "LUX", None),
            ("小国卯", "DEN", None),
            ("小国辰", "SWZ", None),
            ("小国巳", "NOR", None),
            ("小国午", "FIN", None),
            ("小国未", "IRE", None),
            ("小国申", "ALB", None),
            ("小国酉", "ICE", None),
        ]

        return await self._create_agents_from_cinc(project_id, loader, YEAR, countries)

    # ------------------------------------------------------------------
    # 通用CINC数据创建智能体方法
    # ------------------------------------------------------------------
    async def _create_agents_from_cinc(
        self,
        project_id: int,
        loader,
        year: int,
        countries: List[Tuple[str, str, Optional[str]]]
    ) -> Dict[int, int]:
        """
        从CINC数据创建智能体的通用方法

        Args:
            project_id: 项目ID
            loader: CINC数据加载器
            year: 目标年份
            countries: [(糊名, COW缩写, 领导类型), ...]

        Returns:
            {index: agent_id}
        """
        agent_map: Dict[int, int] = {}
        for idx, (alias, abb, leader) in enumerate(countries, start=1):
            record = loader.get_record_by_abb(abb, year)
            if record is None:
                # 兜底：用最近年份的数据
                for offset in [1, -1, 2, -2, 3, -3]:
                    record = loader.get_record_by_abb(abb, year + offset)
                    if record:
                        break
            if record is None:
                continue

            result = await agent_service.add_agent(
                project_id,
                AgentConfigRequest(
                    agent_name=alias,
                    region="欧洲",
                    milex=record.milex,
                    milper=record.milper,
                    irst=record.irst,
                    pec=record.pec,
                    tpop=record.tpop,
                    upop=record.upop,
                    country_code=record.ccode,
                    cinc_year=year,
                    leader_type=leader,
                ),
            )
            agent_map[idx] = result["agent_id"]

        return agent_map

    # ------------------------------------------------------------------
    # 战略关系设置辅助方法
    # ------------------------------------------------------------------
    async def _set_rel(
        self,
        sr_service: StrategicRelationshipService,
        project_id: int,
        source_id: Optional[int],
        target_id: Optional[int],
        rel: StrategicRelationshipEnum,
    ) -> None:
        """安全设置战略关系（忽略None）"""
        if source_id and target_id:
            await sr_service.set_relationship(project_id, source_id, target_id, rel)

    # ------------------------------------------------------------------
    # 从预置场景创建项目
    # ------------------------------------------------------------------
    async def create_project_from_scene(
        self,
        scene_id: int,
        project_name: Optional[str] = None,
        project_desc: Optional[str] = None,
    ) -> dict:
        """
        从预置场景一键创建仿真项目

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
            scene_source=scene["scene_name"],
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

            # 先初始化所有允许的配对关系
            await sr_service.initialize_relationships(project_id)

            # 根据场景设置特定的战略关系
            if scene_id == 1:
                await self._setup_scene1_relationships(sr_service, project_id, agent_map)
            elif scene_id == 2:
                await self._setup_scene2_relationships(sr_service, project_id, agent_map)
            elif scene_id == 3:
                await self._setup_scene3_relationships(sr_service, project_id, agent_map)

            await session.commit()

        return {
            "project_id": project_id,
            "project_name": project["project_name"],
            "status": project["status"],
        }

    # ------------------------------------------------------------------
    # 场景1战略关系（一战前1913）
    # ------------------------------------------------------------------
    async def _setup_scene1_relationships(
        self,
        sr_service: StrategicRelationshipService,
        project_id: int,
        agent_map: Dict[int, int],
    ) -> None:
        """设置场景1（一战前1913）的战略关系"""
        gp1 = agent_map.get(1)   # 强国甲(德)
        gp2 = agent_map.get(2)   # 强国乙(俄)
        gp3 = agent_map.get(3)   # 强国丙(英)
        mp1 = agent_map.get(4)   # 中等国甲(法)
        mp2 = agent_map.get(5)   # 中等国乙(奥匈)
        mp3 = agent_map.get(6)   # 中等国丙(意)
        s1  = agent_map.get(7)   # 小国甲(奥斯曼)
        s2  = agent_map.get(8)   # 小国乙(保加利亚)
        s3  = agent_map.get(9)   # 小国丙(西班牙)
        s4  = agent_map.get(10)  # 小国丁(比利时)
        s5  = agent_map.get(11)  # 小国戊(希腊)
        s6  = agent_map.get(12)  # 小国己(瑞典)
        s7  = agent_map.get(13)  # 小国庚(荷兰)
        s8  = agent_map.get(14)  # 小国辛(罗马尼亚)
        s9  = agent_map.get(15)  # 小国壬(葡萄牙)
        s10 = agent_map.get(16)  # 小国癸(丹麦)
        s11 = agent_map.get(17)  # 小国子(瑞士)
        s12 = agent_map.get(18)  # 小国丑(塞尔维亚)
        s13 = agent_map.get(19)  # 小国寅(挪威)

        # 强国之间
        await self._set_rel(sr_service, project_id, gp1, gp2, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, gp3, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, gp3, StrategicRelationshipEnum.ALLIANCE)

        # 强国甲(德国) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp1, mp1, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, mp2, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, mp3, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s1,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, s2,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s3,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s4,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s5,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s6,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s7,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s8,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s9,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s10, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s11, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s12, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s13, StrategicRelationshipEnum.PARTNERSHIP)

        # 强国乙(俄国) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp2, mp1, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, mp2, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, mp3, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s1,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s2,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s3,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s4,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s5,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s6,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s7,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s8,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s9,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s10, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s11, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s12, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s13, StrategicRelationshipEnum.PARTNERSHIP)

        # 强国丙(英国) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp3, mp1, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, mp2, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp3, mp3, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s1,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s2,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s3,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s4,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s5,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s6,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s7,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s8,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s9,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s10, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s11, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s12, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s13, StrategicRelationshipEnum.ALLIANCE)

    # ------------------------------------------------------------------
    # 场景2战略关系（二战前1938）
    # ------------------------------------------------------------------
    async def _setup_scene2_relationships(
        self,
        sr_service: StrategicRelationshipService,
        project_id: int,
        agent_map: Dict[int, int],
    ) -> None:
        """设置场景2（二战前1938）的战略关系"""
        gp1 = agent_map.get(1)   # 强国甲(苏)
        gp2 = agent_map.get(2)   # 强国乙(德)
        gp3 = agent_map.get(3)   # 强国丙(英)
        mp1 = agent_map.get(4)   # 中等国甲(法)
        mp2 = agent_map.get(5)   # 中等国乙(意)
        mp3 = agent_map.get(6)   # 中等国丙(波兰)
        s1  = agent_map.get(7)   # 小国甲(西班牙)
        s2  = agent_map.get(8)   # 小国乙(捷克斯洛伐克)
        s3  = agent_map.get(9)   # 小国丙(比利时)
        s4  = agent_map.get(10)  # 小国丁(罗马尼亚)
        s5  = agent_map.get(11)  # 小国戊(土耳其)
        s6  = agent_map.get(12)  # 小国己(南斯拉夫)
        s7  = agent_map.get(13)  # 小国庚(瑞典)
        s8  = agent_map.get(14)  # 小国辛(荷兰)
        s9  = agent_map.get(15)  # 小国壬(匈牙利)
        s10 = agent_map.get(16)  # 小国癸(希腊)
        s11 = agent_map.get(17)  # 小国子(葡萄牙)
        s12 = agent_map.get(18)  # 小国丑(卢森堡)
        s13 = agent_map.get(19)  # 小国寅(丹麦)
        s14 = agent_map.get(20)  # 小国卯(芬兰)
        s15 = agent_map.get(21)  # 小国辰(瑞士)
        s16 = agent_map.get(22)  # 小国巳(保加利亚)
        s17 = agent_map.get(23)  # 小国午(挪威)
        s18 = agent_map.get(24)  # 小国未(拉脱维亚)
        s19 = agent_map.get(25)  # 小国申(立陶宛)
        s20 = agent_map.get(26)  # 小国酉(爱尔兰)
        s21 = agent_map.get(27)  # 小国戌(爱沙尼亚)
        s22 = agent_map.get(28)  # 小国亥(阿尔巴尼亚)

        # 强国之间
        await self._set_rel(sr_service, project_id, gp1, gp2, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, gp3, StrategicRelationshipEnum.NO_DIPLOMACY)
        await self._set_rel(sr_service, project_id, gp2, gp3, StrategicRelationshipEnum.CONFLICT)

        # 强国甲(苏联) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp1, mp1, StrategicRelationshipEnum.NO_DIPLOMACY)
        await self._set_rel(sr_service, project_id, gp1, mp2, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, mp3, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s1,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s2,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s3,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s4,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s5,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s6,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s7,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s8,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s9,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s10, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s11, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s12, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s13, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s14, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s15, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s16, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s17, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s18, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s19, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s20, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s21, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s22, StrategicRelationshipEnum.PARTNERSHIP)

        # 强国乙(德国) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp2, mp1, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, mp2, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, mp3, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s1,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s2,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s3,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s4,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s5,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s6,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s7,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s8,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s9,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s10, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s11, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s12, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s13, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s14, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s15, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s16, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s17, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s18, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s19, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s20, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s21, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s22, StrategicRelationshipEnum.PARTNERSHIP)

        # 强国丙(英国) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp3, mp1, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, mp2, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp3, mp3, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s1,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s2,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s3,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s4,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s5,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s6,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s7,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s8,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s9,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp3, s10, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s11, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s12, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s13, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s14, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s15, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s16, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp3, s17, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp3, s18, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s19, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s20, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp3, s21, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp3, s22, StrategicRelationshipEnum.PARTNERSHIP)

    # ------------------------------------------------------------------
    # 场景3战略关系（冷战前1946）
    # ------------------------------------------------------------------
    async def _setup_scene3_relationships(
        self,
        sr_service: StrategicRelationshipService,
        project_id: int,
        agent_map: Dict[int, int],
    ) -> None:
        """设置场景3（冷战前1946）的战略关系"""
        gp1 = agent_map.get(1)   # 强国甲(苏)
        gp2 = agent_map.get(2)   # 强国乙(英)
        mp1 = agent_map.get(3)   # 中等国甲(法)
        mp2 = agent_map.get(4)   # 中等国乙(意)
        mp3 = agent_map.get(5)   # 中等国丙(波兰)
        s1  = agent_map.get(6)   # 小国甲(西班牙)
        s2  = agent_map.get(7)   # 小国乙(土耳其)
        s3  = agent_map.get(8)   # 小国丙(捷克斯洛伐克)
        s4  = agent_map.get(9)   # 小国丁(比利时)
        s5  = agent_map.get(10)  # 小国戊(荷兰)
        s6  = agent_map.get(11)  # 小国己(瑞典)
        s7  = agent_map.get(12)  # 小国庚(南斯拉夫)
        s8  = agent_map.get(13)  # 小国辛(罗马尼亚)
        s9  = agent_map.get(14)  # 小国壬(匈牙利)
        s10 = agent_map.get(15)  # 小国癸(希腊)
        s11 = agent_map.get(16)  # 小国子(保加利亚)
        s12 = agent_map.get(17)  # 小国丑(葡萄牙)
        s13 = agent_map.get(18)  # 小国寅(卢森堡)
        s14 = agent_map.get(19)  # 小国卯(丹麦)
        s15 = agent_map.get(20)  # 小国辰(瑞士)
        s16 = agent_map.get(21)  # 小国巳(挪威)
        s17 = agent_map.get(22)  # 小国午(芬兰)
        s18 = agent_map.get(23)  # 小国未(爱尔兰)
        s19 = agent_map.get(24)  # 小国申(阿尔巴尼亚)
        s20 = agent_map.get(25)  # 小国酉(冰岛)

        # 强国之间
        await self._set_rel(sr_service, project_id, gp1, gp2, StrategicRelationshipEnum.CONFLICT)

        # 强国甲(苏联) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp1, mp1, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, mp2, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, mp3, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, s1,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s2,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s3,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, s4,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s5,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s6,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s7,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s8,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, s9,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, s10, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s11, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, s12, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s13, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s14, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s15, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s16, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s17, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp1, s18, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp1, s19, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp1, s20, StrategicRelationshipEnum.PARTNERSHIP)

        # 强国乙(英国) ↔ 中小国家
        await self._set_rel(sr_service, project_id, gp2, mp1, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, mp2, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, mp3, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s1,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s2,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s3,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s4,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s5,  StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s6,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s7,  StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s8,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s9,  StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s10, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s11, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s12, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s13, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s14, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s15, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s16, StrategicRelationshipEnum.ALLIANCE)
        await self._set_rel(sr_service, project_id, gp2, s17, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s18, StrategicRelationshipEnum.PARTNERSHIP)
        await self._set_rel(sr_service, project_id, gp2, s19, StrategicRelationshipEnum.CONFLICT)
        await self._set_rel(sr_service, project_id, gp2, s20, StrategicRelationshipEnum.ALLIANCE)


# 单例实例
scene_service = SceneService()
