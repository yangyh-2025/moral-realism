"""
预置场景管理服务（CINC版）
提供基于CINC真实历史数据的预设国际体系场景配置，支持一键创建仿真项目
"""

from typing import List, Optional, Dict, Tuple
from datetime import datetime, timezone
from loguru import logger

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

        # 优先从数据库查询，合并硬编码回退（确保新场景在未seeded时也可见）
        async for session in db_config.get_session():
            result = await session.execute(select(PresetScene))
            db_scenes = result.scalars().all()

            # 硬编码回退数据（新场景可能在DB尚未seeded）
            hardcoded = [
                {
                    "scene_id": 1,
                    "scene_name": "一战前欧洲（1913）",
                    "scene_desc": "基于1913年CINC真实数据的欧洲国际体系，包含19个国家。德国崛起、英俄结盟、巴尔干危机...",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": True,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 2,
                    "scene_name": "二战前欧洲（1938）",
                    "scene_desc": "基于1938年CINC真实数据的欧洲国际体系，包含28个国家。苏德对抗、张伯伦绥靖、轴心国体系...",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 3,
                    "scene_name": "冷战前欧洲（1946）",
                    "scene_desc": "基于1946年CINC真实数据的欧洲国际体系，包含25个国家。苏英对立、铁幕降临、马歇尔计划前夜...",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 4,
                    "scene_name": "全球体系（2012）",
                    "scene_desc": "基于2012年CINC真实数据的全球国际体系，包含195个国家。美国单极霸权后撤、中国快速崛起、金砖合作深化、中东动荡...",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 5,
                    "scene_name": "全球体系（2012·美国王道型）",
                    "scene_desc": "2012年全球体系变体——美国改为王道型（多边合作/规则倡导者），其余195国领导类型、国力数据、战略关系均与场景4一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 6,
                    "scene_name": "全球体系（2012·美国强权型）",
                    "scene_desc": "2012年全球体系变体——美国改为强权型（军事实力优先/单边干预），其余195国领导类型、国力数据、战略关系均与场景4一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 7,
                    "scene_name": "全球体系（2012·美国昏庸型）",
                    "scene_desc": "2012年全球体系变体——美国改为昏庸型（决策非理性/国内政治极化），其余195国领导类型、国力数据、战略关系均与场景4一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 8,
                    "scene_name": "一战前欧洲（1913·奥匈昏庸型）",
                    "scene_desc": "1913年欧洲体系变体——奥匈帝国改为昏庸型领导（Conrad von Hötzendorf校准），其余18国领导类型、国力数据、战略关系均与场景1一致。用于验证历史昏庸型领导者的预防性战争冲动、多线作战偏误、盟友意图误判和敌人能力低估等行为模式。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 9,
                    "scene_name": "全球体系（2012·美国王道型·威尔逊道德国际主义）",
                    "scene_desc": "2012年全球体系变体——美国改为王道型并加载伍德罗·威尔逊总统的历史行为心理学档案（长老会圣约神学、文明等级过滤器、公共道义呼吁替代精英妥协、中风后代理决策模式），用于验证王道型道德国际主义领导者的独特决策偏误。其余195国领导类型、国力数据、战略关系均与场景4一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                # ═══════════════════════════════════════════════════════════
                # 场景10-18：场景1变体（1913欧洲 — 单变量领导类型实验）
                # ═══════════════════════════════════════════════════════════
                {
                    "scene_id": 10,
                    "scene_name": "S1-G1（GMY强权→王道）",
                    "scene_desc": "1913年欧洲体系变体——德国由强权型改为王道型（遵守国际规范/制度构建者）。若德国1913年受道义约束，七月危机能否避免？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 11,
                    "scene_name": "S1-G2（GMY强权→霸权）",
                    "scene_desc": "1913年欧洲体系变体——德国由强权型改为霸权型（工具性道义/双重标准）。若德国以规则构建和制度工具主义操作国际关系，追随格局是否不同？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 12,
                    "scene_name": "S1-G3（GMY强权→昏庸）",
                    "scene_desc": "1913年欧洲体系变体——德国由强权型改为昏庸型（决策非理性/战略紊乱）。若德国决策系统瘫痪，多极均势如何瓦解？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 13,
                    "scene_name": "S1-R1（RUS强权→王道）",
                    "scene_desc": "1913年欧洲体系变体——俄国由强权型改为王道型（遵守国际规范/道义约束）。若俄国受道义约束且不诉诸军事动员，巴尔干危机能否通过外交降级？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 14,
                    "scene_name": "S1-R2（RUS强权→霸权）",
                    "scene_desc": "1913年欧洲体系变体——俄国由强权型改为霸权型（双重标准/规则主导权）。若俄国以制度工具主义替代军事强制为核心手段，同盟关系如何重组？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 15,
                    "scene_name": "S1-R3（RUS强权→昏庸）",
                    "scene_desc": "1913年欧洲体系变体——俄国由强权型改为昏庸型（决策非理性加剧）。若俄国决策系统全面失能，追随流失路径与体系解体时序如何？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 16,
                    "scene_name": "S1-U1（UKG王道→强权）",
                    "scene_desc": "1913年欧洲体系变体——英国由王道型改为强权型（军事强制/忽视道义）。若英国放弃道义约束以军力手段维持均势和帝国，秩序类型如何变化？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 17,
                    "scene_name": "S1-U2（UKG王道→霸权）",
                    "scene_desc": "1913年欧洲体系变体——英国由王道型改为霸权型（双重标准/利益最大化）。若英国在殖民地以霸权逻辑在欧洲以道义话语并行操作，追随格局是否受影响？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 18,
                    "scene_name": "S1-U3（UKG王道→昏庸）",
                    "scene_desc": "1913年欧洲体系变体——英国由王道型改为昏庸型（决策瘫痪/战略紊乱）。若体系内唯一的王道型领导者决策失灵，体系领导者真空的后果是什么？其余18国领导类型、国力数据、战略关系均与场景1一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                # ═══════════════════════════════════════════════════════════
                # 场景19-27：场景2变体（1938欧洲 — 单变量领导类型实验）
                # ═══════════════════════════════════════════════════════════
                {
                    "scene_id": 19,
                    "scene_name": "S2-R1（RUS霸权→王道）",
                    "scene_desc": "1938年欧洲体系变体——苏联由霸权型改为王道型（遵守国际规范/道义约束集体安全）。若斯大林受道义约束而不追求势力范围，东欧缓冲区政策如何改变？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 20,
                    "scene_name": "S2-R2（RUS霸权→强权）",
                    "scene_desc": "1938年欧洲体系变体——苏联由霸权型改为强权型（军事强制核心/忽视道义）。若苏联以纯军事逻辑行动——扩张依靠武力而非制度形式，冷战格局是否提前固化？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 21,
                    "scene_name": "S2-R3（RUS霸权→昏庸）",
                    "scene_desc": "1938年欧洲体系变体——苏联由霸权型改为昏庸型（决策非理性/战略判断失能）。若苏联决策系统紊乱——无法计算性地利用德苏条约和军事缓冲，对德战争转折？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 22,
                    "scene_name": "S2-G1（GMY强权→王道）",
                    "scene_desc": "1938年欧洲体系变体——德国由强权型改为王道型（遵守国际规范/通过制度追求修正）。若希特勒受道义约束——修正凡尔赛条约通过外交谈判而非军事威胁，是否存在谈判和平？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 23,
                    "scene_name": "S2-G2（GMY强权→霸权）",
                    "scene_desc": "1938年欧洲体系变体——德国由强权型改为霸权型（工具性道义/双重标准）。若纳粹以规则话语和制度工具主义包装扩张——对大国用道义话语对小国用强制，绥靖是否延续更久？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 24,
                    "scene_name": "S2-G3（GMY强权→昏庸）",
                    "scene_desc": "1938年欧洲体系变体——德国由强权型改为昏庸型（决策非理性/战略紊乱）。若纳粹决策系统紊乱——同时多线挑衅且无法完成战略规划，战争进程如何偏离历史轨道？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 25,
                    "scene_name": "S2-U1（UKG王道→强权）",
                    "scene_desc": "1938年欧洲体系变体——英国由王道型改为强权型（军事强制/忽视道义）。若无绥靖而强硬对抗——英国以军事手段回应德国的每一步扩张，1938年即开战？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 26,
                    "scene_name": "S2-U2（UKG王道→霸权）",
                    "scene_desc": "1938年欧洲体系变体——英国由王道型改为霸权型（双重标准/以绥靖为霸权工具）。若张伯伦式霸权逻辑——牺牲小国以换取时间——成为整个时期的制度性策略而非一次性误判，结果如何？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 27,
                    "scene_name": "S2-U3（UKG王道→昏庸）",
                    "scene_desc": "1938年欧洲体系变体——英国由王道型改为昏庸型（决策瘫痪/战略失能）。若英国决策系统失灵——无法形成连贯的对德政策，欧洲是否会因缺乏抗衡力量而全线沦陷？其余27国领导类型、国力数据、战略关系均与场景2一致。",
                    "total_rounds": 32,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                # ═══════════════════════════════════════════════════════════
                # 场景28-33：场景3变体（1946欧洲 — 单变量领导类型实验）
                # ═══════════════════════════════════════════════════════════
                {
                    "scene_id": 28,
                    "scene_name": "S3-R1（RUS强权→王道）",
                    "scene_desc": "1946年欧洲体系变体——苏联由强权型改为王道型（遵守国际规范/道义约束势力范围）。若斯大林受道义约束——东欧非军事强制而通过多边制度安排，冷战能否避免或形态不同？其余24国领导类型、国力数据、战略关系均与场景3一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 29,
                    "scene_name": "S3-R2（RUS强权→霸权）",
                    "scene_desc": "1946年欧洲体系变体——苏联由强权型改为霸权型（双重标准/制度工具主义）。若苏联以规则构建和灵活标准化替代纯军事强制管理势力范围，阵营稳定性如何变化？其余24国领导类型、国力数据、战略关系均与场景3一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 30,
                    "scene_name": "S3-R3（RUS强权→昏庸）",
                    "scene_desc": "1946年欧洲体系变体——苏联由强权型改为昏庸型（决策非理性/战略失能）。若苏联决策系统紊乱——继承斗争扩大化、对外行为不稳定，东欧阵营的凝聚力如何变化？其余24国领导类型、国力数据、战略关系均与场景3一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 31,
                    "scene_name": "S3-U1（UKG王道→强权）",
                    "scene_desc": "1946年欧洲体系变体——英国由王道型改为强权型（军事力量维持帝国/强制手段优先）。若英国拒绝去殖民化且以军事手段维持全球存在，西方阵营的性质如何变化？其余24国领导类型、国力数据、战略关系均与场景3一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 32,
                    "scene_name": "S3-U2（UKG王道→霸权）",
                    "scene_desc": "1946年欧洲体系变体——英国由王道型改为霸权型（双重标准/帝国保护主义）。若英国以霸权型逻辑运作——公开主张道义但私下维护帝国特权（苏伊士模式贯穿全期），西方阵营团结度如何？其余24国领导类型、国力数据、战略关系均与场景3一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
                {
                    "scene_id": 33,
                    "scene_name": "S3-U3（UKG王道→昏庸）",
                    "scene_desc": "1946年欧洲体系变体——英国由王道型改为昏庸型（决策失灵/战略紊乱）。若英国决策系统瘫痪——无法推动北约筹建、欧洲一体化或有序去殖民化，西欧领导真空由谁填补？其余24国领导类型、国力数据、战略关系均与场景3一致。",
                    "total_rounds": 50,
                    "agent_config_json": '{"agents": []}',
                    "is_default": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                },
            ]

            if not db_scenes:
                return hardcoded

            # DB有数据时，合并硬编码中DB不存在的场景
            db_ids = {s.scene_id for s in db_scenes}
            result_list = []
            for s in db_scenes:
                result_list.append({
                    "scene_id": s.scene_id,
                    "scene_name": s.scene_name,
                    "scene_desc": s.scene_desc,
                    "total_rounds": s.total_rounds,
                    "agent_config_json": s.agent_config_json,
                    "is_default": s.is_default,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                })
            for hc in hardcoded:
                if hc["scene_id"] not in db_ids:
                    result_list.append(hc)
            return result_list

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

        # 数据库无该场景时，回退到硬编码数据
        scenes = await self.get_preset_scenes()
        for scene in scenes:
            if scene["scene_id"] == scene_id:
                return scene
        return None

    # ------------------------------------------------------------------
    # 场景1：一战前欧洲（1913年，19国）
    # ------------------------------------------------------------------
    async def _create_scene1_agents(self, project_id: int) -> Dict[int, int]:
        """场景1基线：GMY=强权, RUS=强权, UKG=王道, FRN=霸权, AUH=昏庸"""
        return await self._create_scene1_variant(project_id)

    async def _create_scene1_variant(
        self,
        project_id: int,
        gmy_leader: str = "强权型",
        rus_leader: str = "强权型",
        ukg_leader: str = "王道型",
        frn_leader: str = "霸权型",
        auh_leader: str = "昏庸型",
    ) -> Dict[int, int]:
        """
        场景1变体（参数化大国领导类型）。

        参数均为可选，None表示不分配领导类型（仅按profile注入决策特征）。
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()
        YEAR = 1913

        countries: List[Tuple[str, str, Optional[str]]] = [
            ("强国甲", "GMY", gmy_leader),
            ("强国乙", "RUS", rus_leader),
            ("强国丙", "UKG", ukg_leader),
            ("强国丁", "FRN", frn_leader),
            ("中等国甲", "AUH", auh_leader),
            ("中等国乙", "ITA", None),
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
        """场景2基线：RUS=霸权, GMY=强权, UKG=王道"""
        return await self._create_scene2_variant(project_id)

    async def _create_scene2_variant(
        self,
        project_id: int,
        rus_leader: str = "霸权型",
        gmy_leader: str = "强权型",
        ukg_leader: str = "王道型",
    ) -> Dict[int, int]:
        """
        场景2变体（参数化大国领导类型）。
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()
        YEAR = 1938

        countries: List[Tuple[str, str, Optional[str]]] = [
            ("强国甲", "RUS", rus_leader),
            ("强国乙", "GMY", gmy_leader),
            ("强国丙", "UKG", ukg_leader),
            ("中等国甲", "FRN", None),
            ("中等国乙", "ITA", None),
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
        """场景3基线：RUS=强权, UKG=王道"""
        return await self._create_scene3_variant(project_id)

    async def _create_scene3_variant(
        self,
        project_id: int,
        rus_leader: str = "强权型",
        ukg_leader: str = "王道型",
    ) -> Dict[int, int]:
        """
        场景3变体（参数化大国领导类型）。
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()
        YEAR = 1946

        countries: List[Tuple[str, str, Optional[str]]] = [
            ("强国甲", "RUS", rus_leader),
            ("强国乙", "UKG", ukg_leader),
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
    # 场景4-7：全球体系（2012年，195国）— USA领导类型变体实验
    # ------------------------------------------------------------------
    async def _create_2012_agents(self, project_id: int, usa_leader: str) -> Dict[int, int]:
        """
        创建2012年全球体系智能体（场景4-7的共享实现）

        Args:
            project_id: 项目ID
            usa_leader: USA的领导类型（霸权型/王道型/强权型/昏庸型）

        其他国家领导类型：
        - 王道型: CHN, UKG, FRN, GMY, JPN
        - 强权型: RUS, IRN, PRK, VEN
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()
        YEAR = 2012

        _LEADER_MAP = {
            "USA": usa_leader,
            "CHN": "王道型", "UKG": "王道型", "FRN": "王道型",
            "GMY": "王道型", "JPN": "王道型",
            "RUS": "强权型", "IRN": "强权型", "PRK": "强权型", "VEN": "强权型",
        }

        countries_2012 = loader.get_countries_by_year(YEAR)
        country_list: List[Tuple[str, str, Optional[str]]] = []
        for c in countries_2012:
            if c["cinc"] <= 0:
                continue
            abb = c["stateabb"]
            name = c["name"]
            leader = _LEADER_MAP.get(abb)
            country_list.append((name, abb, leader))

        return await self._create_agents_from_cinc(project_id, loader, YEAR, country_list)

    async def _create_scene4_agents(self, project_id: int) -> Dict[int, int]:
        """场景4：USA=霸权型"""
        return await self._create_2012_agents(project_id, "霸权型")

    async def _create_scene5_agents(self, project_id: int) -> Dict[int, int]:
        """场景5：USA=王道型"""
        return await self._create_2012_agents(project_id, "王道型")

    async def _create_scene6_agents(self, project_id: int) -> Dict[int, int]:
        """场景6：USA=强权型"""
        return await self._create_2012_agents(project_id, "强权型")

    async def _create_scene7_agents(self, project_id: int) -> Dict[int, int]:
        """场景7：USA=昏庸型"""
        return await self._create_2012_agents(project_id, "昏庸型")

    async def _create_scene8_agents(self, project_id: int) -> Dict[int, int]:
        """场景8：AUH=昏庸型（Conrad校准），其余与场景1相同。显式实验对照。"""
        return await self._create_scene1_agents(project_id)

    async def _create_scene9_agents(self, project_id: int) -> Dict[int, int]:
        """场景9：USA=王道型+Wilson档案，其余与场景4相同。威尔逊道德国际主义实验。"""
        return await self._create_2012_agents(project_id, "王道型")

    # ------------------------------------------------------------------
    # 场景10-18：场景1变体实验（1913欧洲 — 单变量领导类型操作）
    # 每个实验仅改变一个大国的领导类型，其余与基线一致。
    # 缩写：S1-G1=场景1-GMY→王道, S1-G2=GMY→霸权, S1-G3=GMY→昏庸
    #       S1-R1=RUS→王道, S1-R2=RUS→霸权, S1-R3=RUS→昏庸
    #       S1-U1=UKG→强权, S1-U2=UKG→霸权, S1-U3=UKG→昏庸
    # ------------------------------------------------------------------
    async def _create_scene10_agents(self, project_id: int) -> Dict[int, int]:
        """S1-G1: GMY 强权→王道。若德国1913年遵守国际规范，追随格局与秩序类型如何变化？"""
        return await self._create_scene1_variant(project_id, gmy_leader="王道型")

    async def _create_scene11_agents(self, project_id: int) -> Dict[int, int]:
        """S1-G2: GMY 强权→霸权。若德国工具性使用道义（双重标准），追随格局是否不同？"""
        return await self._create_scene1_variant(project_id, gmy_leader="霸权型")

    async def _create_scene12_agents(self, project_id: int) -> Dict[int, int]:
        """S1-G3: GMY 强权→昏庸。若德国决策非理性化，多极均势如何瓦解？"""
        return await self._create_scene1_variant(project_id, gmy_leader="昏庸型")

    async def _create_scene13_agents(self, project_id: int) -> Dict[int, int]:
        """S1-R1: RUS 强权→王道。若俄国受道义约束，巴尔干危机会否降级？"""
        return await self._create_scene1_variant(project_id, rus_leader="王道型")

    async def _create_scene14_agents(self, project_id: int) -> Dict[int, int]:
        """S1-R2: RUS 强权→霸权。若俄国双重标准操作，同盟关系如何重组？"""
        return await self._create_scene1_variant(project_id, rus_leader="霸权型")

    async def _create_scene15_agents(self, project_id: int) -> Dict[int, int]:
        """S1-R3: RUS 强权→昏庸。若尼古拉二世昏庸加剧，追随流失路径？"""
        return await self._create_scene1_variant(project_id, rus_leader="昏庸型")

    async def _create_scene16_agents(self, project_id: int) -> Dict[int, int]:
        """S1-U1: UKG 王道→强权。若英国放弃道义以军力主导，秩序类型？"""
        return await self._create_scene1_variant(project_id, ukg_leader="强权型")

    async def _create_scene17_agents(self, project_id: int) -> Dict[int, int]:
        """S1-U2: UKG 王道→霸权。若英国双重标准操作（如殖民地），影响？"""
        return await self._create_scene1_variant(project_id, ukg_leader="霸权型")

    async def _create_scene18_agents(self, project_id: int) -> Dict[int, int]:
        """S1-U3: UKG 王道→昏庸。若英国决策瘫痪，体系领导者真空后果？"""
        return await self._create_scene1_variant(project_id, ukg_leader="昏庸型")

    # ------------------------------------------------------------------
    # 场景19-27：场景2变体实验（1938欧洲 — 单变量领导类型操作）
    # 缩写：S2-R1=RUS→王道, S2-R2=RUS→强权, S2-R3=RUS→昏庸
    #       S2-G1=GMY→王道, S2-G2=GMY→霸权, S2-G3=GMY→昏庸
    #       S2-U1=UKG→强权, S2-U2=UKG→霸权, S2-U3=UKG→昏庸
    # ------------------------------------------------------------------
    async def _create_scene19_agents(self, project_id: int) -> Dict[int, int]:
        """S2-R1: RUS 霸权→王道。若斯大林受道义约束，东欧缓冲区政策？"""
        return await self._create_scene2_variant(project_id, rus_leader="王道型")

    async def _create_scene20_agents(self, project_id: int) -> Dict[int, int]:
        """S2-R2: RUS 霸权→强权。若苏联纯军事逻辑，冷战格局是否提前？"""
        return await self._create_scene2_variant(project_id, rus_leader="强权型")

    async def _create_scene21_agents(self, project_id: int) -> Dict[int, int]:
        """S2-R3: RUS 霸权→昏庸。若苏联决策非理性，对德战争的转折？"""
        return await self._create_scene2_variant(project_id, rus_leader="昏庸型")

    async def _create_scene22_agents(self, project_id: int) -> Dict[int, int]:
        """S2-G1: GMY 强权→王道。若希特勒受道义约束，能否存在谈判和平？"""
        return await self._create_scene2_variant(project_id, gmy_leader="王道型")

    async def _create_scene23_agents(self, project_id: int) -> Dict[int, int]:
        """S2-G2: GMY 强权→霸权。若纳粹工具性使用规范，绥靖是否延续？"""
        return await self._create_scene2_variant(project_id, gmy_leader="霸权型")

    async def _create_scene24_agents(self, project_id: int) -> Dict[int, int]:
        """S2-G3: GMY 强权→昏庸。若德国决策紊乱，战争进程如何偏离？"""
        return await self._create_scene2_variant(project_id, gmy_leader="昏庸型")

    async def _create_scene25_agents(self, project_id: int) -> Dict[int, int]:
        """S2-U1: UKG 王道→强权。若无绥靖而强硬对抗，1938年即开战？"""
        return await self._create_scene2_variant(project_id, ukg_leader="强权型")

    async def _create_scene26_agents(self, project_id: int) -> Dict[int, int]:
        """S2-U2: UKG 王道→霸权。若张伯伦式霸权逻辑延续全期？"""
        return await self._create_scene2_variant(project_id, ukg_leader="霸权型")

    async def _create_scene27_agents(self, project_id: int) -> Dict[int, int]:
        """S2-U3: UKG 王道→昏庸。若英国决策瘫痪，欧洲是否会全线沦陷？"""
        return await self._create_scene2_variant(project_id, ukg_leader="昏庸型")

    # ------------------------------------------------------------------
    # 场景28-33：场景3变体实验（1946欧洲 — 单变量领导类型操作）
    # 缩写：S3-R1=RUS→王道, S3-R2=RUS→霸权, S3-R3=RUS→昏庸
    #       S3-U1=UKG→强权, S3-U2=UKG→霸权, S3-U3=UKG→昏庸
    # ------------------------------------------------------------------
    async def _create_scene28_agents(self, project_id: int) -> Dict[int, int]:
        """S3-R1: RUS 强权→王道。若斯大林受道义约束，冷战能否避免？"""
        return await self._create_scene3_variant(project_id, rus_leader="王道型")

    async def _create_scene29_agents(self, project_id: int) -> Dict[int, int]:
        """S3-R2: RUS 强权→霸权。若苏联霸权型（双重标准），阵营稳定性？"""
        return await self._create_scene3_variant(project_id, rus_leader="霸权型")

    async def _create_scene30_agents(self, project_id: int) -> Dict[int, int]:
        """S3-R3: RUS 强权→昏庸。若苏联决策非理性，阵营稳定性？"""
        return await self._create_scene3_variant(project_id, rus_leader="昏庸型")

    async def _create_scene31_agents(self, project_id: int) -> Dict[int, int]:
        """S3-U1: UKG 王道→强权。若英国以军力维持帝国，去殖民化路径？"""
        return await self._create_scene3_variant(project_id, ukg_leader="强权型")

    async def _create_scene32_agents(self, project_id: int) -> Dict[int, int]:
        """S3-U2: UKG 王道→霸权。若英国霸权型（苏伊士逻辑主导），影响？"""
        return await self._create_scene3_variant(project_id, ukg_leader="霸权型")

    async def _create_scene33_agents(self, project_id: int) -> Dict[int, int]:
        """S3-U3: UKG 王道→昏庸。若英国决策失灵，西欧领导真空由谁填补？"""
        return await self._create_scene3_variant(project_id, ukg_leader="昏庸型")

    # ------------------------------------------------------------------
    # 场景4战略关系（2012全球体系 — 条约集团/bloc-based）
    # ------------------------------------------------------------------
    async def _setup_scene4_relationships(
        self,
        sr_service: StrategicRelationshipService,
        project_id: int,
        agent_map: Dict[int, int],
    ) -> None:
        """
        2012年全球战略关系 — 程序化条约集团分配。

        195国产生约4000对有效配对，逐对硬编码不可行。采用 bloc 分组：
        先收集所有要设置的关系为 (idx1, idx2, rel) 三元组，
        然后批量 await _set_rel。

        2012年真实条约集团:

        [NATO 28] ALB,BEL,BUL,CAN,CRO,CZR,DEN,EST,FRN,GMY,GRC,HUN,
          ICE,ITA,LAT,LIT,LUX,NTH,NOR,POL,POR,ROM,SLV,SLO,SPN,TUR,UKG,USA
        [CSTO 6] RUS,BLR,ARM,KZK,KYR,TAJ
        [美日韩澳] JPN,ROK,AUL,NEW
        [上合 SCO] CHN,RUS,KZK,KYR,TAJ,UZB
        [GCC 6] SAU,UAE,OMN,KUW,BAH,QAT
        [BRICS 5] CHN,RUS,IND,BRA,SAF
        [反美轴心] IRN,SYR,PRK,VEN,CUB,BOL,ECU,NIC,ZIM
        [中国紧密伙伴] PAK,CAM,LAO,MYA
        [中东亲美] ISR,EGY,JOR,IRQ
        """
        from app.core.cinc_data_loader import get_cinc_loader
        loader = get_cinc_loader()

        # 按 CINC 排序获取 2012 国家列表 → idx_stateabb
        countries_sorted = [c for c in loader.get_countries_by_year(2012) if c["cinc"] > 0]
        idx_stateabb: Dict[int, str] = {}
        abb_to_idx: Dict[str, int] = {}
        for i, c in enumerate(countries_sorted, start=1):
            if i in agent_map:
                abb = c["stateabb"]
                idx_stateabb[i] = abb
                abb_to_idx[abb] = i

        def _idx(abb: str) -> Optional[int]:
            return abb_to_idx.get(abb.upper())

        # 条约集团（COW三字母缩写，仅限2012年真实成员）
        # NATO (28国,2012): 不含芬兰(2023入)、瑞典(2024入)、波黑
        _nato = {"USA","CAN","UKG","FRN","GMY","ITA","SPN","NTH","BEL","LUX",
                 "DEN","NOR","ICE","POL","CZR","SLO","SLV","HUN","ROM","BUL",
                 "CRO","ALB","EST","LAT","LIT","TUR","POR","GRC"}
        _csto = {"RUS","BLR","ARM","KZK","KYR","TAJ"}
        _us_east_asia = {"JPN","ROK","TAW"}
        _anzus = {"AUL","NEW"}
        _sco = {"CHN","RUS","KZK","KYR","TAJ","UZB"}
        _gcc = {"SAU","UAE","OMN","KUW","BAH","QAT"}
        _brics = {"CHN","RUS","IND","BRA","SAF"}
        _anti_us = {"IRN","SYR","PRK","VEN","CUB","BOL","ECU","NIC","ZIM"}
        _cn_close = {"PAK","CAM","LAO","MYA","SUD"}
        _eu_neutral = {"SWZ","MLD","UKR","GRG","AZE"}
        _cn_nato_partners = {"UKG","FRN","GMY","ITA","SPN","NTH","CAN","AUL"}

        # 收集所有关系对 (src_idx, tgt_idx, rel)
        pairs: List[Tuple[int, int, StrategicRelationshipEnum]] = []
        R = StrategicRelationshipEnum  # 缩写

        # ---- 集团内部 ALLIANCE ----
        for bloc in [_nato, _csto, _gcc, _anzus]:
            members = sorted([_idx(a) for a in bloc if _idx(a)])
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    pairs.append((members[i], members[j], R.ALLIANCE))

        # 集团内部 PARTNERSHIP
        for bloc in [_brics, _sco, _eu_neutral, _cn_close, _us_east_asia]:
            members = sorted([_idx(a) for a in bloc if _idx(a)])
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    pairs.append((members[i], members[j], R.PARTNERSHIP))

        # 反美轴心内部 PARTNERSHIP
        _au_members = sorted([_idx(a) for a in _anti_us if _idx(a)])
        for i in range(len(_au_members)):
            for j in range(i + 1, len(_au_members)):
                pairs.append((_au_members[i], _au_members[j], R.PARTNERSHIP))

        # ---- 集团间真实关系 ----
        # NATO × CSTO: CONFLICT
        for na in _nato:
            for cs in _csto:
                if _idx(na) and _idx(cs):
                    pairs.append((_idx(na), _idx(cs), R.CONFLICT))

        # NATO × _anti_us: CONFLICT
        for na in _nato:
            for au in _anti_us:
                if _idx(na) and _idx(au):
                    pairs.append((_idx(na), _idx(au), R.CONFLICT))

        # USA × CHN: CONFLICT
        if _idx("USA") and _idx("CHN"):
            pairs.append((_idx("USA"), _idx("CHN"), R.CONFLICT))
        # USA × RUS: CONFLICT
        if _idx("USA") and _idx("RUS"):
            pairs.append((_idx("USA"), _idx("RUS"), R.CONFLICT))

        # CHN × RUS: PARTNERSHIP
        if _idx("CHN") and _idx("RUS"):
            pairs.append((_idx("CHN"), _idx("RUS"), R.PARTNERSHIP))

        # 中国独特关系
        for a, b, r in [
            ("CHN","IRN",R.PARTNERSHIP), ("CHN","PRK",R.ALLIANCE),
            ("CHN","PAK",R.ALLIANCE),     ("CHN","IND",R.CONFLICT),
            ("JPN","CHN",R.CONFLICT),     ("USA","ISR",R.ALLIANCE),
            ("USA","SAU",R.PARTNERSHIP),  ("PAK","IND",R.CONFLICT),
            ("UKG","ARG",R.CONFLICT),     ("RUS","UKR",R.CONFLICT),
            ("RUS","GRG",R.CONFLICT),     ("ISR","IRN",R.CONFLICT),
            ("SAU","IRN",R.CONFLICT),     ("JPN","ROK",R.PARTNERSHIP),
            ("JPN","PRK",R.CONFLICT),     ("ROK","PRK",R.CONFLICT),
            ("TUR","GRC",R.CONFLICT),     ("TUR","ARM",R.CONFLICT),
            ("TUR","IRN",R.PARTNERSHIP),  ("SAU","PAK",R.ALLIANCE),
            ("VEN","IRN",R.ALLIANCE),     ("IND","RUS",R.PARTNERSHIP),
            ("CHN","SUD",R.PARTNERSHIP),  ("RUS","SYR",R.ALLIANCE),
            ("IRN","SYR",R.ALLIANCE),
        ]:
            if _idx(a) and _idx(b):
                pairs.append((_idx(a), _idx(b), r))

        # CN × NATO partners
        for cn_p in _cn_nato_partners:
            if _idx(cn_p) and _idx("CHN"):
                pairs.append((_idx(cn_p), _idx("CHN"), R.PARTNERSHIP))

        # US × JPN/ROK: ALLIANCE
        for ea in ["JPN","ROK"]:
            if _idx("USA") and _idx(ea):
                pairs.append((_idx("USA"), _idx(ea), R.ALLIANCE))
        # US × AUL: ALLIANCE
        if _idx("USA") and _idx("AUL"):
            pairs.append((_idx("USA"), _idx("AUL"), R.ALLIANCE))

        # GCC × USA/UKG/FRN: PARTNERSHIP
        for gc in _gcc:
            for w in ["USA","UKG","FRN"]:
                if _idx(gc) and _idx(w):
                    pairs.append((_idx(gc), _idx(w), R.PARTNERSHIP))

        # ISR/EGY/JOR × USA: PARTNERSHIP
        for me in ["ISR","EGY","JOR","IRQ"]:
            if _idx(me) and _idx("USA"):
                pairs.append((_idx(me), _idx("USA"), R.PARTNERSHIP))

        # ---- 批量执行（将 index 转为 agent_id 后调用 _ensure_relationship 跳过等级验证） ----
        # 使用 _ensure_relationship 而非 set_relationship 是因为195国体系中
        # RUS/UKR等国家对可能都是中等强国，set_relationship 会拒绝同等级配对。
        for si, ti, rel in pairs:
            src_id = agent_map.get(si)
            tgt_id = agent_map.get(ti)
            if src_id and tgt_id:
                await sr_service._ensure_relationship(project_id, src_id, tgt_id, rel)

        logger.info(
            f"场景4：2012全球体系战略关系设置完成，共 {len(pairs)} 对显式关系"
        )
        # 注：未显式设置的高×低/高×高配对保留 initialize_relationships 的
        # NO_DIPLOMACY 默认值（已在 create_project_from_scene 中先调用
        # initialize_relationships 再调用本方法覆盖已有关系）。

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

        修复：先批量保存所有agent的6项指标（不触发CINC重算），
        待所有agent入库后再统一计算CINC，确保所有agent的initial_total_power
        基于相同规模的完整体系统一计算。

        Args:
            project_id: 项目ID
            loader: CINC数据加载器
            year: 目标年份
            countries: [(糊名, COW缩写, 领导类型), ...]

        Returns:
            {index: agent_id}
        """
        from app.models import AgentConfig
        from app.config.database import db_config

        agent_map: Dict[int, int] = {}
        raw_records: List[Tuple[int, str, Optional[str], Any]] = []

        # 第一步：收集所有CINC原始数据
        for idx, (alias, abb, leader) in enumerate(countries, start=1):
            record = loader.get_record_by_abb(abb, year)
            if record is None:
                for offset in [1, -1, 2, -2, 3, -3]:
                    record = loader.get_record_by_abb(abb, year + offset)
                    if record:
                        break
            if record is None:
                continue
            raw_records.append((idx, alias, leader, record))

        if not raw_records:
            return agent_map

        # 第二步：批量保存所有agent（不计算CINC，initial/current均设为0）
        async for session in db_config.get_session():
            for idx, alias, leader, record in raw_records:
                agent = AgentConfig(
                    project_id=project_id,
                    agent_name=alias,
                    region="欧洲",
                    milex=record.milex,
                    milper=record.milper,
                    irst=record.irst,
                    pec=record.pec,
                    tpop=record.tpop,
                    upop=record.upop,
                    initial_total_power=0.0,
                    current_total_power=0.0,
                    power_level="小国",
                    country_code=record.ccode,
                    cinc_year=year,
                    leader_type=leader,
                )
                session.add(agent)
            await session.commit()

            # 刷新以获取agent_id
            for idx, alias, leader, record in raw_records:
                # 通过名称和项目ID查询刚添加的agent
                from sqlalchemy import select
                result = await session.execute(
                    select(AgentConfig).where(
                        AgentConfig.project_id == project_id,
                        AgentConfig.agent_name == alias,
                    )
                )
                agent = result.scalar_one_or_none()
                if agent:
                    agent_map[idx] = agent.agent_id

        # 第三步：所有agent入库后，统一计算CINC（force_update_initial=True）
        await agent_service._recalculate_all_cincs(
            project_id, force_update_initial=True
        )

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
        elif scene_id == 4:
            agent_map = await self._create_scene4_agents(project_id)
        elif scene_id == 5:
            agent_map = await self._create_scene5_agents(project_id)
        elif scene_id == 6:
            agent_map = await self._create_scene6_agents(project_id)
        elif scene_id == 7:
            agent_map = await self._create_scene7_agents(project_id)
        elif scene_id == 8:
            agent_map = await self._create_scene8_agents(project_id)
        elif scene_id == 9:
            agent_map = await self._create_scene9_agents(project_id)
        # 场景10-18：场景1变体（1913 — 单变量领导类型实验）
        elif scene_id == 10:
            agent_map = await self._create_scene10_agents(project_id)
        elif scene_id == 11:
            agent_map = await self._create_scene11_agents(project_id)
        elif scene_id == 12:
            agent_map = await self._create_scene12_agents(project_id)
        elif scene_id == 13:
            agent_map = await self._create_scene13_agents(project_id)
        elif scene_id == 14:
            agent_map = await self._create_scene14_agents(project_id)
        elif scene_id == 15:
            agent_map = await self._create_scene15_agents(project_id)
        elif scene_id == 16:
            agent_map = await self._create_scene16_agents(project_id)
        elif scene_id == 17:
            agent_map = await self._create_scene17_agents(project_id)
        elif scene_id == 18:
            agent_map = await self._create_scene18_agents(project_id)
        # 场景19-27：场景2变体（1938 — 单变量领导类型实验）
        elif scene_id == 19:
            agent_map = await self._create_scene19_agents(project_id)
        elif scene_id == 20:
            agent_map = await self._create_scene20_agents(project_id)
        elif scene_id == 21:
            agent_map = await self._create_scene21_agents(project_id)
        elif scene_id == 22:
            agent_map = await self._create_scene22_agents(project_id)
        elif scene_id == 23:
            agent_map = await self._create_scene23_agents(project_id)
        elif scene_id == 24:
            agent_map = await self._create_scene24_agents(project_id)
        elif scene_id == 25:
            agent_map = await self._create_scene25_agents(project_id)
        elif scene_id == 26:
            agent_map = await self._create_scene26_agents(project_id)
        elif scene_id == 27:
            agent_map = await self._create_scene27_agents(project_id)
        # 场景28-33：场景3变体（1946 — 单变量领导类型实验）
        elif scene_id == 28:
            agent_map = await self._create_scene28_agents(project_id)
        elif scene_id == 29:
            agent_map = await self._create_scene29_agents(project_id)
        elif scene_id == 30:
            agent_map = await self._create_scene30_agents(project_id)
        elif scene_id == 31:
            agent_map = await self._create_scene31_agents(project_id)
        elif scene_id == 32:
            agent_map = await self._create_scene32_agents(project_id)
        elif scene_id == 33:
            agent_map = await self._create_scene33_agents(project_id)
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
            elif scene_id in (4, 5, 6, 7, 9):
                await self._setup_scene4_relationships(sr_service, project_id, agent_map)
            elif scene_id in (8, 10, 11, 12, 13, 14, 15, 16, 17, 18):
                await self._setup_scene1_relationships(sr_service, project_id, agent_map)
            elif scene_id in (19, 20, 21, 22, 23, 24, 25, 26, 27):
                await self._setup_scene2_relationships(sr_service, project_id, agent_map)
            elif scene_id in (28, 29, 30, 31, 32, 33):
                await self._setup_scene3_relationships(sr_service, project_id, agent_map)

            await session.commit()

        # 初始化邻接关系
        # 用 try/except 包裹 import 以兼容 W3 尚未完成的情况
        try:
            from app.core.geography_data import get_default_neighbors_for_scene
        except ImportError:
            def get_default_neighbors_for_scene(year, agent_map):
                return set()

        from app.services.agent_neighbor_service import AgentNeighborService

        # 场景 ID → 年份 映射 (与 _create_sceneN_agents 中的 YEAR 同步)
        scene_year_map = {1: 1913, 2: 1938, 3: 1946, 4: 2012, 5: 2012, 6: 2012, 7: 2012, 8: 1913, 9: 2012,
                          10: 1913, 11: 1913, 12: 1913, 13: 1913, 14: 1913, 15: 1913,
                          16: 1913, 17: 1913, 18: 1913,
                          19: 1938, 20: 1938, 21: 1938, 22: 1938, 23: 1938, 24: 1938,
                          25: 1938, 26: 1938, 27: 1938,
                          28: 1946, 29: 1946, 30: 1946, 31: 1946, 32: 1946, 33: 1946}
        scene_year = scene_year_map.get(scene_id)

        async for session in db_config.get_session():
            nb_service = AgentNeighborService(session)
            if scene_year is not None:
                default_pairs = get_default_neighbors_for_scene(
                    year=scene_year, agent_map=agent_map
                )
            else:
                default_pairs = set()
            await nb_service.initialize_neighbors(project_id, default_pairs)
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
        await self._set_rel(sr_service, project_id, gp1, mp3, StrategicRelationshipEnum.ALLIANCE)
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
        await self._set_rel(sr_service, project_id, gp3, s1,  StrategicRelationshipEnum.PARTNERSHIP)
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

        # ------------------------------------------------------------
        # 中等国之间（3对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp1, mp2, StrategicRelationshipEnum.CONFLICT)      # 法↔奥匈：法俄盟友，反德反奥
        await self._set_rel(sr_service, project_id, mp1, mp3, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔意：1902法意秘密协定
        await self._set_rel(sr_service, project_id, mp2, mp3, StrategicRelationshipEnum.CONFLICT)      # 奥匈↔意：意大利北部领土纠纷★

        # ------------------------------------------------------------
        # 中等国甲（法国）↔ 小国（13对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp1, s1,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔奥斯曼
        await self._set_rel(sr_service, project_id, mp1, s2,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔保加利亚
        await self._set_rel(sr_service, project_id, mp1, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔西班牙
        await self._set_rel(sr_service, project_id, mp1, s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔比利时：保护中立国
        await self._set_rel(sr_service, project_id, mp1, s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔希腊
        await self._set_rel(sr_service, project_id, mp1, s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔瑞典
        await self._set_rel(sr_service, project_id, mp1, s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔荷兰
        await self._set_rel(sr_service, project_id, mp1, s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔罗马尼亚
        await self._set_rel(sr_service, project_id, mp1, s9,  StrategicRelationshipEnum.ALLIANCE)      # 法↔葡萄牙：传统盟友
        await self._set_rel(sr_service, project_id, mp1, s10, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔丹麦
        await self._set_rel(sr_service, project_id, mp1, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔瑞士
        await self._set_rel(sr_service, project_id, mp1, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔塞尔维亚：反奥匈
        await self._set_rel(sr_service, project_id, mp1, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔挪威

        # ------------------------------------------------------------
        # 中等国乙（奥匈）↔ 小国（13对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp2, s1,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔奥斯曼：反俄反塞
        await self._set_rel(sr_service, project_id, mp2, s2,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔保加利亚：反塞
        await self._set_rel(sr_service, project_id, mp2, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔西班牙
        await self._set_rel(sr_service, project_id, mp2, s4,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 奥匈↔比利时
        await self._set_rel(sr_service, project_id, mp2, s5,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 奥匈↔希腊
        await self._set_rel(sr_service, project_id, mp2, s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔瑞典
        await self._set_rel(sr_service, project_id, mp2, s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔荷兰
        await self._set_rel(sr_service, project_id, mp2, s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔罗马尼亚：传统盟友，1913开始疏远
        await self._set_rel(sr_service, project_id, mp2, s9,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 奥匈↔葡萄牙
        await self._set_rel(sr_service, project_id, mp2, s10, StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔丹麦
        await self._set_rel(sr_service, project_id, mp2, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 奥匈↔瑞士
        await self._set_rel(sr_service, project_id, mp2, s12, StrategicRelationshipEnum.CONFLICT)      # 奥匈↔塞尔维亚★：萨拉热窝导火索
        await self._set_rel(sr_service, project_id, mp2, s13, StrategicRelationshipEnum.NO_DIPLOMACY)  # 奥匈↔挪威

        # ------------------------------------------------------------
        # 中等国丙（意大利）↔ 小国（13对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp3, s1,  StrategicRelationshipEnum.CONFLICT)      # 意↔奥斯曼：1911意土战争★
        await self._set_rel(sr_service, project_id, mp3, s2,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔保加利亚
        await self._set_rel(sr_service, project_id, mp3, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔西班牙
        await self._set_rel(sr_service, project_id, mp3, s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔比利时
        await self._set_rel(sr_service, project_id, mp3, s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔希腊
        await self._set_rel(sr_service, project_id, mp3, s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔瑞典
        await self._set_rel(sr_service, project_id, mp3, s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔荷兰
        await self._set_rel(sr_service, project_id, mp3, s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔罗马尼亚
        await self._set_rel(sr_service, project_id, mp3, s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔葡萄牙
        await self._set_rel(sr_service, project_id, mp3, s10, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔丹麦
        await self._set_rel(sr_service, project_id, mp3, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔瑞士
        await self._set_rel(sr_service, project_id, mp3, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔塞尔维亚
        await self._set_rel(sr_service, project_id, mp3, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔挪威

        # ------------------------------------------------------------
        # 小国之间 - 关键史实冲突（巴尔干战争系列）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, s1,  s2,  StrategicRelationshipEnum.CONFLICT)      # 奥斯曼↔保加利亚★：巴尔干战争
        await self._set_rel(sr_service, project_id, s1,  s5,  StrategicRelationshipEnum.CONFLICT)      # 奥斯曼↔希腊★：巴尔干战争
        await self._set_rel(sr_service, project_id, s1,  s12, StrategicRelationshipEnum.CONFLICT)      # 奥斯曼↔塞尔维亚★：巴尔干战争
        await self._set_rel(sr_service, project_id, s2,  s5,  StrategicRelationshipEnum.CONFLICT)      # 保↔希：马其顿问题
        await self._set_rel(sr_service, project_id, s2,  s8,  StrategicRelationshipEnum.CONFLICT)      # 保↔罗：多布罗加问题
        await self._set_rel(sr_service, project_id, s2,  s12, StrategicRelationshipEnum.CONFLICT)      # 保↔塞★：第二次巴尔干战争
        await self._set_rel(sr_service, project_id, s5,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔塞：反奥斯曼
        await self._set_rel(sr_service, project_id, s8,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔塞：反奥匈

        # ------------------------------------------------------------
        # 小国之间 - 中立国/伊比利亚/北欧（其余对子，默认 PARTNERSHIP）
        # 共 78 对，已显式 8 对，剩余 70 对全部 PARTNERSHIP
        # ------------------------------------------------------------
        # s1(奥斯曼) ↔ 其余（除 s2,s5,s12）
        await self._set_rel(sr_service, project_id, s1,  s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔西班牙
        await self._set_rel(sr_service, project_id, s1,  s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔比利时
        await self._set_rel(sr_service, project_id, s1,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔瑞典
        await self._set_rel(sr_service, project_id, s1,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔荷兰
        await self._set_rel(sr_service, project_id, s1,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔罗马尼亚
        await self._set_rel(sr_service, project_id, s1,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔葡萄牙
        await self._set_rel(sr_service, project_id, s1,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔丹麦
        await self._set_rel(sr_service, project_id, s1,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔瑞士
        await self._set_rel(sr_service, project_id, s1,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 奥斯曼↔挪威

        # s2(保) ↔ 其余（除 s1,s5,s8,s12）
        await self._set_rel(sr_service, project_id, s2,  s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 保↔西班牙
        await self._set_rel(sr_service, project_id, s2,  s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 保↔比利时
        await self._set_rel(sr_service, project_id, s2,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 保↔瑞典
        await self._set_rel(sr_service, project_id, s2,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 保↔荷兰
        await self._set_rel(sr_service, project_id, s2,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 保↔葡萄牙
        await self._set_rel(sr_service, project_id, s2,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔丹麦
        await self._set_rel(sr_service, project_id, s2,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔瑞士
        await self._set_rel(sr_service, project_id, s2,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔挪威

        # s3(西班牙) ↔ 其余
        await self._set_rel(sr_service, project_id, s3,  s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔比利时
        await self._set_rel(sr_service, project_id, s3,  s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔希腊
        await self._set_rel(sr_service, project_id, s3,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔瑞典
        await self._set_rel(sr_service, project_id, s3,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔荷兰
        await self._set_rel(sr_service, project_id, s3,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔罗马尼亚
        await self._set_rel(sr_service, project_id, s3,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔葡萄牙：伊比利亚兄弟
        await self._set_rel(sr_service, project_id, s3,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔丹麦
        await self._set_rel(sr_service, project_id, s3,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔瑞士
        await self._set_rel(sr_service, project_id, s3,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔塞尔维亚
        await self._set_rel(sr_service, project_id, s3,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔挪威

        # s4(比利时) ↔ 其余
        await self._set_rel(sr_service, project_id, s4,  s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔希腊
        await self._set_rel(sr_service, project_id, s4,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔瑞典
        await self._set_rel(sr_service, project_id, s4,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔荷兰
        await self._set_rel(sr_service, project_id, s4,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔罗马尼亚
        await self._set_rel(sr_service, project_id, s4,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔葡萄牙
        await self._set_rel(sr_service, project_id, s4,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔丹麦
        await self._set_rel(sr_service, project_id, s4,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔瑞士
        await self._set_rel(sr_service, project_id, s4,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔塞尔维亚
        await self._set_rel(sr_service, project_id, s4,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔挪威

        # s5(希腊) ↔ 其余（除 s1,s2,s12）
        await self._set_rel(sr_service, project_id, s5,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 希↔瑞典
        await self._set_rel(sr_service, project_id, s5,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 希↔荷兰
        await self._set_rel(sr_service, project_id, s5,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 希↔罗马尼亚
        await self._set_rel(sr_service, project_id, s5,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 希↔葡萄牙
        await self._set_rel(sr_service, project_id, s5,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔丹麦
        await self._set_rel(sr_service, project_id, s5,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔瑞士
        await self._set_rel(sr_service, project_id, s5,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔挪威

        # s6(瑞典) ↔ 其余
        await self._set_rel(sr_service, project_id, s6,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔荷兰
        await self._set_rel(sr_service, project_id, s6,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔罗马尼亚
        await self._set_rel(sr_service, project_id, s6,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔葡萄牙
        await self._set_rel(sr_service, project_id, s6,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔丹麦：北欧兄弟
        await self._set_rel(sr_service, project_id, s6,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔瑞士
        await self._set_rel(sr_service, project_id, s6,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔塞尔维亚
        await self._set_rel(sr_service, project_id, s6,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔挪威：1905独立后和平

        # s7(荷兰) ↔ 其余
        await self._set_rel(sr_service, project_id, s7,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔罗马尼亚
        await self._set_rel(sr_service, project_id, s7,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔葡萄牙
        await self._set_rel(sr_service, project_id, s7,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔丹麦
        await self._set_rel(sr_service, project_id, s7,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔瑞士
        await self._set_rel(sr_service, project_id, s7,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔塞尔维亚
        await self._set_rel(sr_service, project_id, s7,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔挪威

        # s8(罗马尼亚) ↔ 其余（除 s2,s12）
        await self._set_rel(sr_service, project_id, s8,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔葡萄牙
        await self._set_rel(sr_service, project_id, s8,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔丹麦
        await self._set_rel(sr_service, project_id, s8,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔瑞士
        await self._set_rel(sr_service, project_id, s8,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔挪威

        # s9(葡萄牙) ↔ 其余
        await self._set_rel(sr_service, project_id, s9,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔丹麦
        await self._set_rel(sr_service, project_id, s9,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔瑞士
        await self._set_rel(sr_service, project_id, s9,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔塞尔维亚
        await self._set_rel(sr_service, project_id, s9,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔挪威

        # s10(丹麦) ↔ 其余
        await self._set_rel(sr_service, project_id, s10, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔瑞士
        await self._set_rel(sr_service, project_id, s10, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔塞尔维亚
        await self._set_rel(sr_service, project_id, s10, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔挪威：北欧兄弟

        # s11(瑞士) ↔ 其余
        await self._set_rel(sr_service, project_id, s11, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔塞尔维亚
        await self._set_rel(sr_service, project_id, s11, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔挪威

        # s12(塞尔维亚) ↔ s13(挪威)
        await self._set_rel(sr_service, project_id, s12, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 塞↔挪威

        # 总关系对数: 171, 已显式定义: 171对, NO_DIPLOMACY: 4对
        # CONFLICT: 14对（含原有强国部分）, ALLIANCE: 19对, PARTNERSHIP: 134对
        # 详细分布：强强(3) + 强中小(48) + 中中(3) + 中小(39) + 小小(78) = 171

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

        # ------------------------------------------------------------
        # 中等国之间（3对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp1, mp2, StrategicRelationshipEnum.CONFLICT)      # 法↔意：地中海竞争，意对突尼斯/科西嘉有诉求
        await self._set_rel(sr_service, project_id, mp1, mp3, StrategicRelationshipEnum.ALLIANCE)      # 法↔波★：1921法波同盟
        await self._set_rel(sr_service, project_id, mp2, mp3, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔波：友好但非盟友

        # ------------------------------------------------------------
        # 中等国甲（法国 mp1）↔ 小国（22对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp1, s1,  StrategicRelationshipEnum.CONFLICT)      # 法↔西：佛朗哥胜利在即，法支持共和派
        await self._set_rel(sr_service, project_id, mp1, s2,  StrategicRelationshipEnum.ALLIANCE)      # 法↔捷★：1924法捷同盟
        await self._set_rel(sr_service, project_id, mp1, s3,  StrategicRelationshipEnum.ALLIANCE)      # 法↔比★：1920法比军事协定
        await self._set_rel(sr_service, project_id, mp1, s4,  StrategicRelationshipEnum.ALLIANCE)      # 法↔罗★：小协约后台
        await self._set_rel(sr_service, project_id, mp1, s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔土：友好
        await self._set_rel(sr_service, project_id, mp1, s6,  StrategicRelationshipEnum.ALLIANCE)      # 法↔南★：小协约后台
        await self._set_rel(sr_service, project_id, mp1, s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔瑞典
        await self._set_rel(sr_service, project_id, mp1, s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔荷：友好（荷中立）
        await self._set_rel(sr_service, project_id, mp1, s9,  StrategicRelationshipEnum.CONFLICT)      # 法↔匈：匈牙利修约主义敌视小协约
        await self._set_rel(sr_service, project_id, mp1, s10, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔希
        await self._set_rel(sr_service, project_id, mp1, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔葡
        await self._set_rel(sr_service, project_id, mp1, s12, StrategicRelationshipEnum.ALLIANCE)      # 法↔卢★：1867伦敦条约担保中立
        await self._set_rel(sr_service, project_id, mp1, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔丹
        await self._set_rel(sr_service, project_id, mp1, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔芬
        await self._set_rel(sr_service, project_id, mp1, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔瑞士
        await self._set_rel(sr_service, project_id, mp1, s16, StrategicRelationshipEnum.CONFLICT)      # 法↔保：保加利亚修约主义反小协约
        await self._set_rel(sr_service, project_id, mp1, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔挪
        await self._set_rel(sr_service, project_id, mp1, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔拉
        await self._set_rel(sr_service, project_id, mp1, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔立
        await self._set_rel(sr_service, project_id, mp1, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔爱尔兰
        await self._set_rel(sr_service, project_id, mp1, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔爱沙
        await self._set_rel(sr_service, project_id, mp1, s22, StrategicRelationshipEnum.CONFLICT)      # 法↔阿：阿尔巴尼亚是意大利保护国

        # ------------------------------------------------------------
        # 中等国乙（意大利 mp2）↔ 小国（22对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp2, s1,  StrategicRelationshipEnum.ALLIANCE)      # 意↔西★：意军支援佛朗哥
        await self._set_rel(sr_service, project_id, mp2, s2,  StrategicRelationshipEnum.CONFLICT)      # 意↔捷：反小协约（意拒承认捷克）
        await self._set_rel(sr_service, project_id, mp2, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔比
        await self._set_rel(sr_service, project_id, mp2, s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔罗：友好但属法系小协约
        await self._set_rel(sr_service, project_id, mp2, s5,  StrategicRelationshipEnum.CONFLICT)      # 意↔土：意占多德卡尼斯，地中海竞争
        await self._set_rel(sr_service, project_id, mp2, s6,  StrategicRelationshipEnum.CONFLICT)      # 意↔南：亚得里亚海/达尔马提亚之争
        await self._set_rel(sr_service, project_id, mp2, s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔瑞典
        await self._set_rel(sr_service, project_id, mp2, s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔荷
        await self._set_rel(sr_service, project_id, mp2, s9,  StrategicRelationshipEnum.ALLIANCE)      # 意↔匈★：1927意匈条约，修约主义伙伴
        await self._set_rel(sr_service, project_id, mp2, s10, StrategicRelationshipEnum.CONFLICT)      # 意↔希：科孚事件遗留+爱琴海竞争
        await self._set_rel(sr_service, project_id, mp2, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔葡
        await self._set_rel(sr_service, project_id, mp2, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔卢
        await self._set_rel(sr_service, project_id, mp2, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔丹
        await self._set_rel(sr_service, project_id, mp2, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔芬
        await self._set_rel(sr_service, project_id, mp2, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔瑞士
        await self._set_rel(sr_service, project_id, mp2, s16, StrategicRelationshipEnum.ALLIANCE)      # 意↔保★：修约主义同盟
        await self._set_rel(sr_service, project_id, mp2, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔挪
        await self._set_rel(sr_service, project_id, mp2, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔拉
        await self._set_rel(sr_service, project_id, mp2, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔立
        await self._set_rel(sr_service, project_id, mp2, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔爱尔兰
        await self._set_rel(sr_service, project_id, mp2, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔爱沙
        await self._set_rel(sr_service, project_id, mp2, s22, StrategicRelationshipEnum.ALLIANCE)      # 意↔阿★：实际保护国，1939吞并

        # ------------------------------------------------------------
        # 中等国丙（波兰 mp3）↔ 小国（22对）
        # ------------------------------------------------------------
        await self._set_rel(sr_service, project_id, mp3, s1,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔西
        await self._set_rel(sr_service, project_id, mp3, s2,  StrategicRelationshipEnum.CONFLICT)      # 波↔捷★：特申/Teschen之争
        await self._set_rel(sr_service, project_id, mp3, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔比
        await self._set_rel(sr_service, project_id, mp3, s4,  StrategicRelationshipEnum.ALLIANCE)      # 波↔罗★：1921波罗同盟（反苏）
        await self._set_rel(sr_service, project_id, mp3, s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔土
        await self._set_rel(sr_service, project_id, mp3, s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔南
        await self._set_rel(sr_service, project_id, mp3, s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔瑞典
        await self._set_rel(sr_service, project_id, mp3, s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔荷
        await self._set_rel(sr_service, project_id, mp3, s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔匈：友好（共同反捷）
        await self._set_rel(sr_service, project_id, mp3, s10, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔希
        await self._set_rel(sr_service, project_id, mp3, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔葡
        await self._set_rel(sr_service, project_id, mp3, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔卢
        await self._set_rel(sr_service, project_id, mp3, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔丹
        await self._set_rel(sr_service, project_id, mp3, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔芬：共同反苏
        await self._set_rel(sr_service, project_id, mp3, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔瑞士
        await self._set_rel(sr_service, project_id, mp3, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔保
        await self._set_rel(sr_service, project_id, mp3, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔挪
        await self._set_rel(sr_service, project_id, mp3, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔拉
        await self._set_rel(sr_service, project_id, mp3, s19, StrategicRelationshipEnum.CONFLICT)      # 波↔立★：维尔纽斯/Vilna之争
        await self._set_rel(sr_service, project_id, mp3, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔爱尔兰
        await self._set_rel(sr_service, project_id, mp3, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔爱沙
        await self._set_rel(sr_service, project_id, mp3, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔阿

        # ------------------------------------------------------------
        # 小国之间（231对，C(22,2)）
        # ------------------------------------------------------------
        # s1(西班牙) ↔ 其余21国
        await self._set_rel(sr_service, project_id, s1,  s2,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔捷
        await self._set_rel(sr_service, project_id, s1,  s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔比
        await self._set_rel(sr_service, project_id, s1,  s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔罗
        await self._set_rel(sr_service, project_id, s1,  s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔土
        await self._set_rel(sr_service, project_id, s1,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔南
        await self._set_rel(sr_service, project_id, s1,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔瑞典
        await self._set_rel(sr_service, project_id, s1,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔荷
        await self._set_rel(sr_service, project_id, s1,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 西↔匈
        await self._set_rel(sr_service, project_id, s1,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔希
        await self._set_rel(sr_service, project_id, s1,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔葡★：伊比利亚兄弟，萨拉查支持佛朗哥
        await self._set_rel(sr_service, project_id, s1,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔卢
        await self._set_rel(sr_service, project_id, s1,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔丹
        await self._set_rel(sr_service, project_id, s1,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔芬
        await self._set_rel(sr_service, project_id, s1,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔瑞士
        await self._set_rel(sr_service, project_id, s1,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔保
        await self._set_rel(sr_service, project_id, s1,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔挪
        await self._set_rel(sr_service, project_id, s1,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔拉
        await self._set_rel(sr_service, project_id, s1,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔立
        await self._set_rel(sr_service, project_id, s1,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔爱尔兰
        await self._set_rel(sr_service, project_id, s1,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔爱沙
        await self._set_rel(sr_service, project_id, s1,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔阿

        # s2(捷克斯洛伐克) ↔ 其余20国
        await self._set_rel(sr_service, project_id, s2,  s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔比
        await self._set_rel(sr_service, project_id, s2,  s4,  StrategicRelationshipEnum.ALLIANCE)      # 捷↔罗★：小协约
        await self._set_rel(sr_service, project_id, s2,  s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔土
        await self._set_rel(sr_service, project_id, s2,  s6,  StrategicRelationshipEnum.ALLIANCE)      # 捷↔南★：小协约
        await self._set_rel(sr_service, project_id, s2,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔瑞典
        await self._set_rel(sr_service, project_id, s2,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔荷
        await self._set_rel(sr_service, project_id, s2,  s9,  StrategicRelationshipEnum.CONFLICT)      # 捷↔匈★：领土争议（斯洛伐克/卢西尼亚）
        await self._set_rel(sr_service, project_id, s2,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔希
        await self._set_rel(sr_service, project_id, s2,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔葡
        await self._set_rel(sr_service, project_id, s2,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔卢
        await self._set_rel(sr_service, project_id, s2,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔丹
        await self._set_rel(sr_service, project_id, s2,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔芬
        await self._set_rel(sr_service, project_id, s2,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔瑞士
        await self._set_rel(sr_service, project_id, s2,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔保
        await self._set_rel(sr_service, project_id, s2,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔挪
        await self._set_rel(sr_service, project_id, s2,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔拉
        await self._set_rel(sr_service, project_id, s2,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔立
        await self._set_rel(sr_service, project_id, s2,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔爱尔兰
        await self._set_rel(sr_service, project_id, s2,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔爱沙
        await self._set_rel(sr_service, project_id, s2,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔阿

        # s3(比利时) ↔ 其余19国
        await self._set_rel(sr_service, project_id, s3,  s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔罗
        await self._set_rel(sr_service, project_id, s3,  s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔土
        await self._set_rel(sr_service, project_id, s3,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔南
        await self._set_rel(sr_service, project_id, s3,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔瑞典
        await self._set_rel(sr_service, project_id, s3,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔荷★：比荷邻邦友好
        await self._set_rel(sr_service, project_id, s3,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔匈
        await self._set_rel(sr_service, project_id, s3,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔希
        await self._set_rel(sr_service, project_id, s3,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔葡
        await self._set_rel(sr_service, project_id, s3,  s12, StrategicRelationshipEnum.ALLIANCE)      # 比↔卢★：1921比卢经济联盟
        await self._set_rel(sr_service, project_id, s3,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔丹
        await self._set_rel(sr_service, project_id, s3,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔芬
        await self._set_rel(sr_service, project_id, s3,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔瑞士
        await self._set_rel(sr_service, project_id, s3,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔保
        await self._set_rel(sr_service, project_id, s3,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔挪
        await self._set_rel(sr_service, project_id, s3,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔拉
        await self._set_rel(sr_service, project_id, s3,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔立
        await self._set_rel(sr_service, project_id, s3,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔爱尔兰
        await self._set_rel(sr_service, project_id, s3,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔爱沙
        await self._set_rel(sr_service, project_id, s3,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔阿

        # s4(罗马尼亚) ↔ 其余18国
        await self._set_rel(sr_service, project_id, s4,  s5,  StrategicRelationshipEnum.ALLIANCE)      # 罗↔土★：1934巴尔干协约
        await self._set_rel(sr_service, project_id, s4,  s6,  StrategicRelationshipEnum.ALLIANCE)      # 罗↔南★：小协约+巴尔干协约
        await self._set_rel(sr_service, project_id, s4,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔瑞典
        await self._set_rel(sr_service, project_id, s4,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔荷
        await self._set_rel(sr_service, project_id, s4,  s9,  StrategicRelationshipEnum.CONFLICT)      # 罗↔匈★：特兰西瓦尼亚之争
        await self._set_rel(sr_service, project_id, s4,  s10, StrategicRelationshipEnum.ALLIANCE)      # 罗↔希★：巴尔干协约
        await self._set_rel(sr_service, project_id, s4,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔葡
        await self._set_rel(sr_service, project_id, s4,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔卢
        await self._set_rel(sr_service, project_id, s4,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔丹
        await self._set_rel(sr_service, project_id, s4,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔芬：共同反苏
        await self._set_rel(sr_service, project_id, s4,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔瑞士
        await self._set_rel(sr_service, project_id, s4,  s16, StrategicRelationshipEnum.CONFLICT)      # 罗↔保★：多布罗加之争
        await self._set_rel(sr_service, project_id, s4,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔挪
        await self._set_rel(sr_service, project_id, s4,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔拉
        await self._set_rel(sr_service, project_id, s4,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔立
        await self._set_rel(sr_service, project_id, s4,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔爱尔兰
        await self._set_rel(sr_service, project_id, s4,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔爱沙
        await self._set_rel(sr_service, project_id, s4,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔阿

        # s5(土耳其) ↔ 其余17国
        await self._set_rel(sr_service, project_id, s5,  s6,  StrategicRelationshipEnum.ALLIANCE)      # 土↔南★：巴尔干协约
        await self._set_rel(sr_service, project_id, s5,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 土↔瑞典
        await self._set_rel(sr_service, project_id, s5,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 土↔荷
        await self._set_rel(sr_service, project_id, s5,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 土↔匈
        await self._set_rel(sr_service, project_id, s5,  s10, StrategicRelationshipEnum.ALLIANCE)      # 土↔希★：巴尔干协约（1930后和解）
        await self._set_rel(sr_service, project_id, s5,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔葡
        await self._set_rel(sr_service, project_id, s5,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔卢
        await self._set_rel(sr_service, project_id, s5,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔丹
        await self._set_rel(sr_service, project_id, s5,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔芬
        await self._set_rel(sr_service, project_id, s5,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔瑞士
        await self._set_rel(sr_service, project_id, s5,  s16, StrategicRelationshipEnum.CONFLICT)      # 土↔保：色雷斯/海峡历史敌对
        await self._set_rel(sr_service, project_id, s5,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔挪
        await self._set_rel(sr_service, project_id, s5,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔拉
        await self._set_rel(sr_service, project_id, s5,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔立
        await self._set_rel(sr_service, project_id, s5,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔爱尔兰
        await self._set_rel(sr_service, project_id, s5,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔爱沙
        await self._set_rel(sr_service, project_id, s5,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔阿

        # s6(南斯拉夫) ↔ 其余16国
        await self._set_rel(sr_service, project_id, s6,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 南↔瑞典
        await self._set_rel(sr_service, project_id, s6,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 南↔荷
        await self._set_rel(sr_service, project_id, s6,  s9,  StrategicRelationshipEnum.CONFLICT)      # 南↔匈★：伏伊伏丁那/克罗地亚问题
        await self._set_rel(sr_service, project_id, s6,  s10, StrategicRelationshipEnum.ALLIANCE)      # 南↔希★：巴尔干协约
        await self._set_rel(sr_service, project_id, s6,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔葡
        await self._set_rel(sr_service, project_id, s6,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔卢
        await self._set_rel(sr_service, project_id, s6,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔丹
        await self._set_rel(sr_service, project_id, s6,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔芬
        await self._set_rel(sr_service, project_id, s6,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔瑞士
        await self._set_rel(sr_service, project_id, s6,  s16, StrategicRelationshipEnum.CONFLICT)      # 南↔保★：马其顿问题
        await self._set_rel(sr_service, project_id, s6,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔挪
        await self._set_rel(sr_service, project_id, s6,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔拉
        await self._set_rel(sr_service, project_id, s6,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔立
        await self._set_rel(sr_service, project_id, s6,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔爱尔兰
        await self._set_rel(sr_service, project_id, s6,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔爱沙
        await self._set_rel(sr_service, project_id, s6,  s22, StrategicRelationshipEnum.CONFLICT)      # 南↔阿：科索沃/阿尔巴尼亚族问题，阿为意保护国

        # s7(瑞典) ↔ 其余15国
        await self._set_rel(sr_service, project_id, s7,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔荷
        await self._set_rel(sr_service, project_id, s7,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔匈
        await self._set_rel(sr_service, project_id, s7,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔希
        await self._set_rel(sr_service, project_id, s7,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔葡
        await self._set_rel(sr_service, project_id, s7,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔卢
        await self._set_rel(sr_service, project_id, s7,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔丹★：北欧兄弟
        await self._set_rel(sr_service, project_id, s7,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔芬★：北欧兄弟
        await self._set_rel(sr_service, project_id, s7,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔瑞士：双中立
        await self._set_rel(sr_service, project_id, s7,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔保
        await self._set_rel(sr_service, project_id, s7,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔挪★：北欧兄弟
        await self._set_rel(sr_service, project_id, s7,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔拉
        await self._set_rel(sr_service, project_id, s7,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔立
        await self._set_rel(sr_service, project_id, s7,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔爱尔兰
        await self._set_rel(sr_service, project_id, s7,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔爱沙
        await self._set_rel(sr_service, project_id, s7,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔阿

        # s8(荷兰) ↔ 其余14国
        await self._set_rel(sr_service, project_id, s8,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔匈
        await self._set_rel(sr_service, project_id, s8,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔希
        await self._set_rel(sr_service, project_id, s8,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔葡
        await self._set_rel(sr_service, project_id, s8,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔卢★：低地国家邻邦
        await self._set_rel(sr_service, project_id, s8,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔丹
        await self._set_rel(sr_service, project_id, s8,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔芬
        await self._set_rel(sr_service, project_id, s8,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔瑞士：双中立
        await self._set_rel(sr_service, project_id, s8,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔保
        await self._set_rel(sr_service, project_id, s8,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔挪
        await self._set_rel(sr_service, project_id, s8,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔拉
        await self._set_rel(sr_service, project_id, s8,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔立
        await self._set_rel(sr_service, project_id, s8,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔爱尔兰
        await self._set_rel(sr_service, project_id, s8,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔爱沙
        await self._set_rel(sr_service, project_id, s8,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔阿

        # s9(匈牙利) ↔ 其余13国
        await self._set_rel(sr_service, project_id, s9,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔希
        await self._set_rel(sr_service, project_id, s9,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔葡
        await self._set_rel(sr_service, project_id, s9,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔卢
        await self._set_rel(sr_service, project_id, s9,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔丹
        await self._set_rel(sr_service, project_id, s9,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔芬
        await self._set_rel(sr_service, project_id, s9,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔瑞士
        await self._set_rel(sr_service, project_id, s9,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔保：共同修约主义
        await self._set_rel(sr_service, project_id, s9,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔挪
        await self._set_rel(sr_service, project_id, s9,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔拉
        await self._set_rel(sr_service, project_id, s9,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔立
        await self._set_rel(sr_service, project_id, s9,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔爱尔兰
        await self._set_rel(sr_service, project_id, s9,  s21, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔爱沙
        await self._set_rel(sr_service, project_id, s9,  s22, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔阿

        # s10(希腊) ↔ 其余12国
        await self._set_rel(sr_service, project_id, s10, s11, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔葡
        await self._set_rel(sr_service, project_id, s10, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔卢
        await self._set_rel(sr_service, project_id, s10, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔丹
        await self._set_rel(sr_service, project_id, s10, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔芬
        await self._set_rel(sr_service, project_id, s10, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔瑞士
        await self._set_rel(sr_service, project_id, s10, s16, StrategicRelationshipEnum.CONFLICT)      # 希↔保★：马其顿/色雷斯之争
        await self._set_rel(sr_service, project_id, s10, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔挪
        await self._set_rel(sr_service, project_id, s10, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔拉
        await self._set_rel(sr_service, project_id, s10, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔立
        await self._set_rel(sr_service, project_id, s10, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔爱尔兰
        await self._set_rel(sr_service, project_id, s10, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔爱沙
        await self._set_rel(sr_service, project_id, s10, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔阿

        # s11(葡萄牙) ↔ 其余11国
        await self._set_rel(sr_service, project_id, s11, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔卢
        await self._set_rel(sr_service, project_id, s11, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔丹
        await self._set_rel(sr_service, project_id, s11, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔芬
        await self._set_rel(sr_service, project_id, s11, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔瑞士
        await self._set_rel(sr_service, project_id, s11, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔保
        await self._set_rel(sr_service, project_id, s11, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔挪
        await self._set_rel(sr_service, project_id, s11, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔拉
        await self._set_rel(sr_service, project_id, s11, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔立
        await self._set_rel(sr_service, project_id, s11, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔爱尔兰
        await self._set_rel(sr_service, project_id, s11, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔爱沙
        await self._set_rel(sr_service, project_id, s11, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔阿

        # s12(卢森堡) ↔ 其余10国
        await self._set_rel(sr_service, project_id, s12, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔丹
        await self._set_rel(sr_service, project_id, s12, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔芬
        await self._set_rel(sr_service, project_id, s12, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔瑞士
        await self._set_rel(sr_service, project_id, s12, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔保
        await self._set_rel(sr_service, project_id, s12, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔挪
        await self._set_rel(sr_service, project_id, s12, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔拉
        await self._set_rel(sr_service, project_id, s12, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔立
        await self._set_rel(sr_service, project_id, s12, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔爱尔兰
        await self._set_rel(sr_service, project_id, s12, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔爱沙
        await self._set_rel(sr_service, project_id, s12, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔阿

        # s13(丹麦) ↔ 其余9国
        await self._set_rel(sr_service, project_id, s13, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔芬★：北欧兄弟
        await self._set_rel(sr_service, project_id, s13, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔瑞士
        await self._set_rel(sr_service, project_id, s13, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔保
        await self._set_rel(sr_service, project_id, s13, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔挪★：北欧兄弟
        await self._set_rel(sr_service, project_id, s13, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔拉
        await self._set_rel(sr_service, project_id, s13, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔立
        await self._set_rel(sr_service, project_id, s13, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔爱尔兰
        await self._set_rel(sr_service, project_id, s13, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔爱沙
        await self._set_rel(sr_service, project_id, s13, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔阿

        # s14(芬兰) ↔ 其余8国
        await self._set_rel(sr_service, project_id, s14, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔瑞士
        await self._set_rel(sr_service, project_id, s14, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔保
        await self._set_rel(sr_service, project_id, s14, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔挪★：北欧兄弟
        await self._set_rel(sr_service, project_id, s14, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔拉：波罗的海邻邦
        await self._set_rel(sr_service, project_id, s14, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔立
        await self._set_rel(sr_service, project_id, s14, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔爱尔兰
        await self._set_rel(sr_service, project_id, s14, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔爱沙★：芬族兄弟
        await self._set_rel(sr_service, project_id, s14, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔阿

        # s15(瑞士) ↔ 其余7国
        await self._set_rel(sr_service, project_id, s15, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔保
        await self._set_rel(sr_service, project_id, s15, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔挪
        await self._set_rel(sr_service, project_id, s15, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔拉
        await self._set_rel(sr_service, project_id, s15, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔立
        await self._set_rel(sr_service, project_id, s15, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔爱尔兰
        await self._set_rel(sr_service, project_id, s15, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔爱沙
        await self._set_rel(sr_service, project_id, s15, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔阿

        # s16(保加利亚) ↔ 其余6国
        await self._set_rel(sr_service, project_id, s16, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔挪
        await self._set_rel(sr_service, project_id, s16, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔拉
        await self._set_rel(sr_service, project_id, s16, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔立
        await self._set_rel(sr_service, project_id, s16, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔爱尔兰
        await self._set_rel(sr_service, project_id, s16, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔爱沙
        await self._set_rel(sr_service, project_id, s16, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔阿

        # s17(挪威) ↔ 其余5国
        await self._set_rel(sr_service, project_id, s17, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔拉
        await self._set_rel(sr_service, project_id, s17, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔立
        await self._set_rel(sr_service, project_id, s17, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔爱尔兰
        await self._set_rel(sr_service, project_id, s17, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔爱沙
        await self._set_rel(sr_service, project_id, s17, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔阿

        # s18(拉脱维亚) ↔ 其余4国
        await self._set_rel(sr_service, project_id, s18, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 拉↔立★：波罗的海协约（1934）
        await self._set_rel(sr_service, project_id, s18, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 拉↔爱尔兰
        await self._set_rel(sr_service, project_id, s18, s21, StrategicRelationshipEnum.ALLIANCE)      # 拉↔爱沙★：波罗的海协约
        await self._set_rel(sr_service, project_id, s18, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 拉↔阿

        # s19(立陶宛) ↔ 其余3国
        await self._set_rel(sr_service, project_id, s19, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 立↔爱尔兰
        await self._set_rel(sr_service, project_id, s19, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 立↔爱沙：波罗的海协约
        await self._set_rel(sr_service, project_id, s19, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 立↔阿

        # s20(爱尔兰) ↔ 其余2国
        await self._set_rel(sr_service, project_id, s20, s21, StrategicRelationshipEnum.PARTNERSHIP)   # 爱尔兰↔爱沙
        await self._set_rel(sr_service, project_id, s20, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 爱尔兰↔阿

        # s21(爱沙尼亚) ↔ s22(阿尔巴尼亚)
        await self._set_rel(sr_service, project_id, s21, s22, StrategicRelationshipEnum.PARTNERSHIP)   # 爱沙↔阿

        # 场景2总关系对数: C(28,2)=378, 已显式定义: 378对
        # 分布：强强(3) + 强中小(75) + 中中(3) + 中小(66) + 小小(231) = 378

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

        # ====== 中等国之间（3对） ======
        await self._set_rel(sr_service, project_id, mp1, mp2, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔意：均西方阵营但的里雅斯特边界争议
        await self._set_rel(sr_service, project_id, mp1, mp3, StrategicRelationshipEnum.CONFLICT)      # 法↔波：波兰苏联化，1947法波将断交
        await self._set_rel(sr_service, project_id, mp2, mp3, StrategicRelationshipEnum.NO_DIPLOMACY)  # 意↔波：东西阵营初分，缺乏实质外交

        # ====== 中等国 ↔ 小国（60对） ======
        # mp1(法国) ↔ 小国
        await self._set_rel(sr_service, project_id, mp1, s1,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 法↔西班牙：联合国谴责佛朗哥，外交断裂
        await self._set_rel(sr_service, project_id, mp1, s2,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔土耳其：同西方阵营
        await self._set_rel(sr_service, project_id, mp1, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔捷克：1946尚未完全苏化，传统友好
        await self._set_rel(sr_service, project_id, mp1, s4,  StrategicRelationshipEnum.ALLIANCE)      # 法↔比利时：西欧紧密盟友
        await self._set_rel(sr_service, project_id, mp1, s5,  StrategicRelationshipEnum.ALLIANCE)      # 法↔荷兰：西欧紧密盟友
        await self._set_rel(sr_service, project_id, mp1, s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 法↔瑞典：中立国友好往来
        await self._set_rel(sr_service, project_id, mp1, s7,  StrategicRelationshipEnum.CONFLICT)      # 法↔南斯拉夫：铁托共产，1946对立
        await self._set_rel(sr_service, project_id, mp1, s8,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 法↔罗马尼亚：苏联傀儡，疏远
        await self._set_rel(sr_service, project_id, mp1, s9,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 法↔匈牙利：苏联占领下
        await self._set_rel(sr_service, project_id, mp1, s10, StrategicRelationshipEnum.ALLIANCE)      # 法↔希腊：西方支持反共政府
        await self._set_rel(sr_service, project_id, mp1, s11, StrategicRelationshipEnum.NO_DIPLOMACY)  # 法↔保加利亚：苏联占领下
        await self._set_rel(sr_service, project_id, mp1, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔葡萄牙：西方阵营但避免冲突
        await self._set_rel(sr_service, project_id, mp1, s13, StrategicRelationshipEnum.ALLIANCE)      # 法↔卢森堡：西欧紧密
        await self._set_rel(sr_service, project_id, mp1, s14, StrategicRelationshipEnum.ALLIANCE)      # 法↔丹麦：西方阵营盟友
        await self._set_rel(sr_service, project_id, mp1, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔瑞士：永久中立友好
        await self._set_rel(sr_service, project_id, mp1, s16, StrategicRelationshipEnum.ALLIANCE)      # 法↔挪威：西方阵营盟友
        await self._set_rel(sr_service, project_id, mp1, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔芬兰：芬式中立，谨慎友好
        await self._set_rel(sr_service, project_id, mp1, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔爱尔兰：中立国正常往来
        await self._set_rel(sr_service, project_id, mp1, s19, StrategicRelationshipEnum.CONFLICT)      # 法↔阿尔巴尼亚：共产主义对立
        await self._set_rel(sr_service, project_id, mp1, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 法↔冰岛：1944共和国西方阵营
        # mp2(意大利) ↔ 小国
        await self._set_rel(sr_service, project_id, mp2, s1,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 意↔西班牙：意大利已民主化与佛朗哥疏远
        await self._set_rel(sr_service, project_id, mp2, s2,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔土耳其：同西方阵营
        await self._set_rel(sr_service, project_id, mp2, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔捷克：1946尚未完全苏化
        await self._set_rel(sr_service, project_id, mp2, s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔比利时：西方阵营但意尚未入北约
        await self._set_rel(sr_service, project_id, mp2, s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔荷兰：西方阵营
        await self._set_rel(sr_service, project_id, mp2, s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 意↔瑞典：中立友好
        await self._set_rel(sr_service, project_id, mp2, s7,  StrategicRelationshipEnum.CONFLICT)      # 意↔南斯拉夫：的里雅斯特领土争端
        await self._set_rel(sr_service, project_id, mp2, s8,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 意↔罗马尼亚：苏联傀儡
        await self._set_rel(sr_service, project_id, mp2, s9,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 意↔匈牙利：苏联占领
        await self._set_rel(sr_service, project_id, mp2, s10, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔希腊：同西方阵营
        await self._set_rel(sr_service, project_id, mp2, s11, StrategicRelationshipEnum.NO_DIPLOMACY)  # 意↔保加利亚：苏联占领
        await self._set_rel(sr_service, project_id, mp2, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔葡萄牙：西方阵营
        await self._set_rel(sr_service, project_id, mp2, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔卢森堡：西方阵营
        await self._set_rel(sr_service, project_id, mp2, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔丹麦：西方阵营
        await self._set_rel(sr_service, project_id, mp2, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔瑞士：永久中立友好
        await self._set_rel(sr_service, project_id, mp2, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔挪威：西方阵营
        await self._set_rel(sr_service, project_id, mp2, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔芬兰：芬式中立
        await self._set_rel(sr_service, project_id, mp2, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, mp2, s19, StrategicRelationshipEnum.CONFLICT)      # 意↔阿尔巴尼亚：共产+边界历史
        await self._set_rel(sr_service, project_id, mp2, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 意↔冰岛：西方阵营
        # mp3(波兰) ↔ 小国
        await self._set_rel(sr_service, project_id, mp3, s1,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔西班牙：佛朗哥反共，意识形态对立
        await self._set_rel(sr_service, project_id, mp3, s2,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔土耳其：东西阵营初分
        await self._set_rel(sr_service, project_id, mp3, s3,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔捷克：均苏联阵营，但特申领土微妙
        await self._set_rel(sr_service, project_id, mp3, s4,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔比利时：东西分裂
        await self._set_rel(sr_service, project_id, mp3, s5,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔荷兰：东西分裂
        await self._set_rel(sr_service, project_id, mp3, s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 波↔瑞典：中立国维持往来
        await self._set_rel(sr_service, project_id, mp3, s7,  StrategicRelationshipEnum.ALLIANCE)      # 波↔南斯拉夫：1946仍同苏联阵营盟友
        await self._set_rel(sr_service, project_id, mp3, s8,  StrategicRelationshipEnum.ALLIANCE)      # 波↔罗马尼亚：均苏联阵营
        await self._set_rel(sr_service, project_id, mp3, s9,  StrategicRelationshipEnum.ALLIANCE)      # 波↔匈牙利：均苏联阵营
        await self._set_rel(sr_service, project_id, mp3, s10, StrategicRelationshipEnum.CONFLICT)      # 波↔希腊：希腊反共内战对立
        await self._set_rel(sr_service, project_id, mp3, s11, StrategicRelationshipEnum.ALLIANCE)      # 波↔保加利亚：均苏联阵营
        await self._set_rel(sr_service, project_id, mp3, s12, StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔葡萄牙：东西分裂
        await self._set_rel(sr_service, project_id, mp3, s13, StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔卢森堡：东西分裂
        await self._set_rel(sr_service, project_id, mp3, s14, StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔丹麦：东西分裂
        await self._set_rel(sr_service, project_id, mp3, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔瑞士：永久中立友好
        await self._set_rel(sr_service, project_id, mp3, s16, StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔挪威：东西分裂
        await self._set_rel(sr_service, project_id, mp3, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔芬兰：芬式中立，苏联阵营默契
        await self._set_rel(sr_service, project_id, mp3, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 波↔爱尔兰：中立国正常往来
        await self._set_rel(sr_service, project_id, mp3, s19, StrategicRelationshipEnum.ALLIANCE)      # 波↔阿尔巴尼亚：均苏联阵营
        await self._set_rel(sr_service, project_id, mp3, s20, StrategicRelationshipEnum.NO_DIPLOMACY)  # 波↔冰岛：东西分裂

        # ====== 小国之间（190对，C(20,2)） ======
        # s1(西班牙) ↔ 其余19小国
        await self._set_rel(sr_service, project_id, s1,  s2,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔土耳其：佛朗哥孤立
        await self._set_rel(sr_service, project_id, s1,  s3,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔捷克：佛朗哥孤立
        await self._set_rel(sr_service, project_id, s1,  s4,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔比利时：佛朗哥被孤立
        await self._set_rel(sr_service, project_id, s1,  s5,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔荷兰：佛朗哥被孤立
        await self._set_rel(sr_service, project_id, s1,  s6,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔瑞典：佛朗哥被孤立
        await self._set_rel(sr_service, project_id, s1,  s7,  StrategicRelationshipEnum.CONFLICT)      # 西↔南斯拉夫：意识形态对立
        await self._set_rel(sr_service, project_id, s1,  s8,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔罗马尼亚：意识形态对立
        await self._set_rel(sr_service, project_id, s1,  s9,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔匈牙利：意识形态对立
        await self._set_rel(sr_service, project_id, s1,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔希腊：同反共阵营
        await self._set_rel(sr_service, project_id, s1,  s11, StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔保加利亚：意识形态对立
        await self._set_rel(sr_service, project_id, s1,  s12, StrategicRelationshipEnum.ALLIANCE)      # 西↔葡萄牙：1939伊比利亚条约
        await self._set_rel(sr_service, project_id, s1,  s13, StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔卢森堡：佛朗哥被孤立
        await self._set_rel(sr_service, project_id, s1,  s14, StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔丹麦：佛朗哥被孤立
        await self._set_rel(sr_service, project_id, s1,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔瑞士：瑞士永久中立维持外交
        await self._set_rel(sr_service, project_id, s1,  s16, StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔挪威：佛朗哥被孤立
        await self._set_rel(sr_service, project_id, s1,  s17, StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔芬兰：意识形态对立
        await self._set_rel(sr_service, project_id, s1,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 西↔爱尔兰：均天主教中立
        await self._set_rel(sr_service, project_id, s1,  s19, StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔阿尔巴尼亚：意识形态对立
        await self._set_rel(sr_service, project_id, s1,  s20, StrategicRelationshipEnum.NO_DIPLOMACY)  # 西↔冰岛：佛朗哥被孤立

        # s2(土耳其) ↔ 其余
        await self._set_rel(sr_service, project_id, s2,  s3,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 土↔捷克：东西阵营
        await self._set_rel(sr_service, project_id, s2,  s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 土↔比利时：同西方阵营
        await self._set_rel(sr_service, project_id, s2,  s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 土↔荷兰：同西方阵营
        await self._set_rel(sr_service, project_id, s2,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 土↔瑞典：中立友好
        await self._set_rel(sr_service, project_id, s2,  s7,  StrategicRelationshipEnum.CONFLICT)      # 土↔南斯拉夫：意识形态+巴尔干对立
        await self._set_rel(sr_service, project_id, s2,  s8,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 土↔罗马尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s2,  s9,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 土↔匈牙利：东西阵营
        await self._set_rel(sr_service, project_id, s2,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔希腊：同被苏联施压，1947共同接受杜鲁门援助
        await self._set_rel(sr_service, project_id, s2,  s11, StrategicRelationshipEnum.CONFLICT)      # 土↔保加利亚：巴尔干+海峡问题
        await self._set_rel(sr_service, project_id, s2,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔葡萄牙：同西方阵营
        await self._set_rel(sr_service, project_id, s2,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔卢森堡：同西方阵营
        await self._set_rel(sr_service, project_id, s2,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔丹麦：同西方阵营
        await self._set_rel(sr_service, project_id, s2,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s2,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔挪威：同西方阵营
        await self._set_rel(sr_service, project_id, s2,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔芬兰：均承压国
        await self._set_rel(sr_service, project_id, s2,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s2,  s19, StrategicRelationshipEnum.CONFLICT)      # 土↔阿尔巴尼亚：意识形态对立
        await self._set_rel(sr_service, project_id, s2,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 土↔冰岛：同西方阵营

        # s3(捷克斯洛伐克) ↔ 其余
        await self._set_rel(sr_service, project_id, s3,  s4,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔比利时：1946尚未完全苏化
        await self._set_rel(sr_service, project_id, s3,  s5,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔荷兰：尚未苏化
        await self._set_rel(sr_service, project_id, s3,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔瑞典：中立友好
        await self._set_rel(sr_service, project_id, s3,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔南斯拉夫：同苏阵营
        await self._set_rel(sr_service, project_id, s3,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔罗马尼亚：同苏阵营
        await self._set_rel(sr_service, project_id, s3,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔匈牙利：同苏阵营
        await self._set_rel(sr_service, project_id, s3,  s10, StrategicRelationshipEnum.NO_DIPLOMACY)  # 捷↔希腊：捷克倾苏与反共希腊对立
        await self._set_rel(sr_service, project_id, s3,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔保加利亚：同苏阵营
        await self._set_rel(sr_service, project_id, s3,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔葡萄牙：尚未完全分裂
        await self._set_rel(sr_service, project_id, s3,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔卢森堡：尚未完全分裂
        await self._set_rel(sr_service, project_id, s3,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔丹麦：尚未完全分裂
        await self._set_rel(sr_service, project_id, s3,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s3,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔挪威：尚未完全分裂
        await self._set_rel(sr_service, project_id, s3,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔芬兰：均苏联影响下
        await self._set_rel(sr_service, project_id, s3,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s3,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔阿尔巴尼亚：同苏阵营
        await self._set_rel(sr_service, project_id, s3,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 捷↔冰岛：中立友好

        # s4(比利时) ↔ 其余
        await self._set_rel(sr_service, project_id, s4,  s5,  StrategicRelationshipEnum.ALLIANCE)      # 比↔荷兰：比卢经济联盟、1944关税同盟
        await self._set_rel(sr_service, project_id, s4,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 比↔瑞典：中立友好
        await self._set_rel(sr_service, project_id, s4,  s7,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 比↔南斯拉夫：东西阵营
        await self._set_rel(sr_service, project_id, s4,  s8,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 比↔罗马尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s4,  s9,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 比↔匈牙利：东西阵营
        await self._set_rel(sr_service, project_id, s4,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔希腊：同西方阵营
        await self._set_rel(sr_service, project_id, s4,  s11, StrategicRelationshipEnum.NO_DIPLOMACY)  # 比↔保加利亚：东西阵营
        await self._set_rel(sr_service, project_id, s4,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔葡萄牙：同西方阵营
        await self._set_rel(sr_service, project_id, s4,  s13, StrategicRelationshipEnum.ALLIANCE)      # 比↔卢森堡：比卢经济联盟
        await self._set_rel(sr_service, project_id, s4,  s14, StrategicRelationshipEnum.ALLIANCE)      # 比↔丹麦：同西方阵营
        await self._set_rel(sr_service, project_id, s4,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔瑞士：永久中立友好
        await self._set_rel(sr_service, project_id, s4,  s16, StrategicRelationshipEnum.ALLIANCE)      # 比↔挪威：同西方阵营
        await self._set_rel(sr_service, project_id, s4,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔芬兰：中立友好
        await self._set_rel(sr_service, project_id, s4,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s4,  s19, StrategicRelationshipEnum.NO_DIPLOMACY)  # 比↔阿尔巴尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s4,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 比↔冰岛：西方友好

        # s5(荷兰) ↔ 其余
        await self._set_rel(sr_service, project_id, s5,  s6,  StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔瑞典：中立友好
        await self._set_rel(sr_service, project_id, s5,  s7,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 荷↔南斯拉夫：东西阵营
        await self._set_rel(sr_service, project_id, s5,  s8,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 荷↔罗马尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s5,  s9,  StrategicRelationshipEnum.NO_DIPLOMACY)  # 荷↔匈牙利：东西阵营
        await self._set_rel(sr_service, project_id, s5,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔希腊：同西方阵营
        await self._set_rel(sr_service, project_id, s5,  s11, StrategicRelationshipEnum.NO_DIPLOMACY)  # 荷↔保加利亚：东西阵营
        await self._set_rel(sr_service, project_id, s5,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔葡萄牙：同西方阵营
        await self._set_rel(sr_service, project_id, s5,  s13, StrategicRelationshipEnum.ALLIANCE)      # 荷↔卢森堡：比卢经济联盟
        await self._set_rel(sr_service, project_id, s5,  s14, StrategicRelationshipEnum.ALLIANCE)      # 荷↔丹麦：同西方阵营
        await self._set_rel(sr_service, project_id, s5,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔瑞士：永久中立友好
        await self._set_rel(sr_service, project_id, s5,  s16, StrategicRelationshipEnum.ALLIANCE)      # 荷↔挪威：同西方阵营
        await self._set_rel(sr_service, project_id, s5,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔芬兰：中立友好
        await self._set_rel(sr_service, project_id, s5,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s5,  s19, StrategicRelationshipEnum.NO_DIPLOMACY)  # 荷↔阿尔巴尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s5,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 荷↔冰岛：西方友好

        # s6(瑞典) ↔ 其余
        await self._set_rel(sr_service, project_id, s6,  s7,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔南斯拉夫：中立友好
        await self._set_rel(sr_service, project_id, s6,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔罗马尼亚：中立友好
        await self._set_rel(sr_service, project_id, s6,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔匈牙利：中立友好
        await self._set_rel(sr_service, project_id, s6,  s10, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔希腊：中立友好
        await self._set_rel(sr_service, project_id, s6,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔保加利亚：中立友好
        await self._set_rel(sr_service, project_id, s6,  s12, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔葡萄牙：中立友好
        await self._set_rel(sr_service, project_id, s6,  s13, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔卢森堡：中立友好
        await self._set_rel(sr_service, project_id, s6,  s14, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔丹麦：北欧合作
        await self._set_rel(sr_service, project_id, s6,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔瑞士：均中立友好
        await self._set_rel(sr_service, project_id, s6,  s16, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔挪威：北欧合作
        await self._set_rel(sr_service, project_id, s6,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔芬兰：北欧+均中立
        await self._set_rel(sr_service, project_id, s6,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s6,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔阿尔巴尼亚：中立维持
        await self._set_rel(sr_service, project_id, s6,  s20, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞典↔冰岛：北欧亲缘

        # s7(南斯拉夫) ↔ 其余
        await self._set_rel(sr_service, project_id, s7,  s8,  StrategicRelationshipEnum.PARTNERSHIP)   # 南↔罗马尼亚：同苏阵营
        await self._set_rel(sr_service, project_id, s7,  s9,  StrategicRelationshipEnum.PARTNERSHIP)   # 南↔匈牙利：同苏阵营
        await self._set_rel(sr_service, project_id, s7,  s10, StrategicRelationshipEnum.CONFLICT)      # 南↔希腊：南支持希腊共产游击队
        await self._set_rel(sr_service, project_id, s7,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔保加利亚：共产化盟友
        await self._set_rel(sr_service, project_id, s7,  s12, StrategicRelationshipEnum.NO_DIPLOMACY)  # 南↔葡萄牙：东西阵营
        await self._set_rel(sr_service, project_id, s7,  s13, StrategicRelationshipEnum.NO_DIPLOMACY)  # 南↔卢森堡：东西阵营
        await self._set_rel(sr_service, project_id, s7,  s14, StrategicRelationshipEnum.NO_DIPLOMACY)  # 南↔丹麦：东西阵营
        await self._set_rel(sr_service, project_id, s7,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔瑞士：永久中立友好
        await self._set_rel(sr_service, project_id, s7,  s16, StrategicRelationshipEnum.NO_DIPLOMACY)  # 南↔挪威：东西阵营
        await self._set_rel(sr_service, project_id, s7,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔芬兰：均苏联影响
        await self._set_rel(sr_service, project_id, s7,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 南↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s7,  s19, StrategicRelationshipEnum.ALLIANCE)      # 南↔阿尔巴尼亚：南是阿保护国，1948才决裂
        await self._set_rel(sr_service, project_id, s7,  s20, StrategicRelationshipEnum.NO_DIPLOMACY)  # 南↔冰岛：东西阵营

        # s8(罗马尼亚) ↔ 其余
        await self._set_rel(sr_service, project_id, s8,  s9,  StrategicRelationshipEnum.CONFLICT)      # 罗↔匈牙利：特兰西瓦尼亚归属之争
        await self._set_rel(sr_service, project_id, s8,  s10, StrategicRelationshipEnum.NO_DIPLOMACY)  # 罗↔希腊：东西阵营
        await self._set_rel(sr_service, project_id, s8,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔保加利亚：同苏阵营
        await self._set_rel(sr_service, project_id, s8,  s12, StrategicRelationshipEnum.NO_DIPLOMACY)  # 罗↔葡萄牙：东西阵营
        await self._set_rel(sr_service, project_id, s8,  s13, StrategicRelationshipEnum.NO_DIPLOMACY)  # 罗↔卢森堡：东西阵营
        await self._set_rel(sr_service, project_id, s8,  s14, StrategicRelationshipEnum.NO_DIPLOMACY)  # 罗↔丹麦：东西阵营
        await self._set_rel(sr_service, project_id, s8,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s8,  s16, StrategicRelationshipEnum.NO_DIPLOMACY)  # 罗↔挪威：东西阵营
        await self._set_rel(sr_service, project_id, s8,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔芬兰：均苏联影响
        await self._set_rel(sr_service, project_id, s8,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s8,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 罗↔阿尔巴尼亚：同苏阵营
        await self._set_rel(sr_service, project_id, s8,  s20, StrategicRelationshipEnum.NO_DIPLOMACY)  # 罗↔冰岛：东西阵营

        # s9(匈牙利) ↔ 其余
        await self._set_rel(sr_service, project_id, s9,  s10, StrategicRelationshipEnum.NO_DIPLOMACY)  # 匈↔希腊：东西阵营
        await self._set_rel(sr_service, project_id, s9,  s11, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔保加利亚：同苏阵营
        await self._set_rel(sr_service, project_id, s9,  s12, StrategicRelationshipEnum.NO_DIPLOMACY)  # 匈↔葡萄牙：东西阵营
        await self._set_rel(sr_service, project_id, s9,  s13, StrategicRelationshipEnum.NO_DIPLOMACY)  # 匈↔卢森堡：东西阵营
        await self._set_rel(sr_service, project_id, s9,  s14, StrategicRelationshipEnum.NO_DIPLOMACY)  # 匈↔丹麦：东西阵营
        await self._set_rel(sr_service, project_id, s9,  s15, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s9,  s16, StrategicRelationshipEnum.NO_DIPLOMACY)  # 匈↔挪威：东西阵营
        await self._set_rel(sr_service, project_id, s9,  s17, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔芬兰：均苏联影响
        await self._set_rel(sr_service, project_id, s9,  s18, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s9,  s19, StrategicRelationshipEnum.PARTNERSHIP)   # 匈↔阿尔巴尼亚：同苏阵营
        await self._set_rel(sr_service, project_id, s9,  s20, StrategicRelationshipEnum.NO_DIPLOMACY)  # 匈↔冰岛：东西阵营

        # s10(希腊) ↔ 其余
        await self._set_rel(sr_service, project_id, s10, s11, StrategicRelationshipEnum.CONFLICT)      # 希↔保加利亚：巴尔干+马其顿争端
        await self._set_rel(sr_service, project_id, s10, s12, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔葡萄牙：同西方阵营
        await self._set_rel(sr_service, project_id, s10, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔卢森堡：同西方阵营
        await self._set_rel(sr_service, project_id, s10, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔丹麦：同西方阵营
        await self._set_rel(sr_service, project_id, s10, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s10, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔挪威：同西方阵营
        await self._set_rel(sr_service, project_id, s10, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔芬兰：均承压国
        await self._set_rel(sr_service, project_id, s10, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s10, s19, StrategicRelationshipEnum.CONFLICT)      # 希↔阿尔巴尼亚：阿支持希腊共产游击队
        await self._set_rel(sr_service, project_id, s10, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 希↔冰岛：同西方阵营

        # s11(保加利亚) ↔ 其余
        await self._set_rel(sr_service, project_id, s11, s12, StrategicRelationshipEnum.NO_DIPLOMACY)  # 保↔葡萄牙：东西阵营
        await self._set_rel(sr_service, project_id, s11, s13, StrategicRelationshipEnum.NO_DIPLOMACY)  # 保↔卢森堡：东西阵营
        await self._set_rel(sr_service, project_id, s11, s14, StrategicRelationshipEnum.NO_DIPLOMACY)  # 保↔丹麦：东西阵营
        await self._set_rel(sr_service, project_id, s11, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s11, s16, StrategicRelationshipEnum.NO_DIPLOMACY)  # 保↔挪威：东西阵营
        await self._set_rel(sr_service, project_id, s11, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔芬兰：均苏联影响
        await self._set_rel(sr_service, project_id, s11, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s11, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 保↔阿尔巴尼亚：同苏阵营
        await self._set_rel(sr_service, project_id, s11, s20, StrategicRelationshipEnum.NO_DIPLOMACY)  # 保↔冰岛：东西阵营

        # s12(葡萄牙) ↔ 其余
        await self._set_rel(sr_service, project_id, s12, s13, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔卢森堡：同西方阵营
        await self._set_rel(sr_service, project_id, s12, s14, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔丹麦：同西方阵营
        await self._set_rel(sr_service, project_id, s12, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s12, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔挪威：同西方阵营
        await self._set_rel(sr_service, project_id, s12, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔芬兰：友好
        await self._set_rel(sr_service, project_id, s12, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔爱尔兰：均天主教
        await self._set_rel(sr_service, project_id, s12, s19, StrategicRelationshipEnum.NO_DIPLOMACY)  # 葡↔阿尔巴尼亚：反共萨拉查孤立
        await self._set_rel(sr_service, project_id, s12, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 葡↔冰岛：同西方阵营

        # s13(卢森堡) ↔ 其余
        await self._set_rel(sr_service, project_id, s13, s14, StrategicRelationshipEnum.ALLIANCE)      # 卢↔丹麦：同西方阵营
        await self._set_rel(sr_service, project_id, s13, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s13, s16, StrategicRelationshipEnum.ALLIANCE)      # 卢↔挪威：同西方阵营
        await self._set_rel(sr_service, project_id, s13, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔芬兰：中立友好
        await self._set_rel(sr_service, project_id, s13, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s13, s19, StrategicRelationshipEnum.NO_DIPLOMACY)  # 卢↔阿尔巴尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s13, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 卢↔冰岛：西方友好

        # s14(丹麦) ↔ 其余
        await self._set_rel(sr_service, project_id, s14, s15, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔瑞士：中立友好
        await self._set_rel(sr_service, project_id, s14, s16, StrategicRelationshipEnum.ALLIANCE)      # 丹↔挪威：北欧+同西方
        await self._set_rel(sr_service, project_id, s14, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔芬兰：北欧友好
        await self._set_rel(sr_service, project_id, s14, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s14, s19, StrategicRelationshipEnum.NO_DIPLOMACY)  # 丹↔阿尔巴尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s14, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 丹↔冰岛：1944分离独立但邻近友好

        # s15(瑞士) ↔ 其余
        await self._set_rel(sr_service, project_id, s15, s16, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔挪威：永久中立友好
        await self._set_rel(sr_service, project_id, s15, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔芬兰：均中立
        await self._set_rel(sr_service, project_id, s15, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔爱尔兰：均中立
        await self._set_rel(sr_service, project_id, s15, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔阿尔巴尼亚：永久中立友好
        await self._set_rel(sr_service, project_id, s15, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 瑞士↔冰岛：均小国中立

        # s16(挪威) ↔ 其余
        await self._set_rel(sr_service, project_id, s16, s17, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔芬兰：北欧友好
        await self._set_rel(sr_service, project_id, s16, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔爱尔兰：中立友好
        await self._set_rel(sr_service, project_id, s16, s19, StrategicRelationshipEnum.NO_DIPLOMACY)  # 挪↔阿尔巴尼亚：东西阵营
        await self._set_rel(sr_service, project_id, s16, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 挪↔冰岛：北欧亲缘

        # s17(芬兰) ↔ 其余
        await self._set_rel(sr_service, project_id, s17, s18, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔爱尔兰：均中立
        await self._set_rel(sr_service, project_id, s17, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔阿尔巴尼亚：芬式中立维持
        await self._set_rel(sr_service, project_id, s17, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 芬↔冰岛：北欧亲缘

        # s18(爱尔兰) ↔ 其余
        await self._set_rel(sr_service, project_id, s18, s19, StrategicRelationshipEnum.PARTNERSHIP)   # 爱↔阿尔巴尼亚：中立维持
        await self._set_rel(sr_service, project_id, s18, s20, StrategicRelationshipEnum.PARTNERSHIP)   # 爱↔冰岛：均小岛国中立

        # s19(阿尔巴尼亚) ↔ s20(冰岛)
        await self._set_rel(sr_service, project_id, s19, s20, StrategicRelationshipEnum.NO_DIPLOMACY)  # 阿↔冰岛：东西阵营

        # 总关系对数: 300, 已显式定义: 300对
        # 中-中: 3, 中-小: 60, 小-小: 190; 强强1+强中小46+中中3+中小60+小小190=300


# 单例实例
scene_service = SceneService()
