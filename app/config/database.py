"""
数据库配置与初始化模块
ABM仿真系统的数据库配置、连接管理和数据初始化。
"""

import json
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent
# 数据存储目录
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 数据库 URL - 使用异步 SQLite 驱动
# 将路径中的反斜杠转换为正斜杠以确保 URL 兼容性
db_path = str(DATA_DIR / "abm_simulation.db").replace("\\", "/")
DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

class DatabaseConfig:
    """
    数据库配置管理类

    负责数据库引擎的创建、会话工厂管理和连接池管理。
    """

    def __init__(self, db_url: str = DATABASE_URL):
        """
        初始化数据库配置

        Args:
            db_url: 数据库连接字符串，默认使用 SQLite 数据库
        """
        self.db_url = db_url
        self._engine: AsyncEngine | None = None
        self._async_session_factory: async_sessionmaker | None = None

    @property
    def engine(self) -> AsyncEngine:
        """
        获取或创建数据库引擎

        使用懒加载方式创建异步数据库引擎。
        """
        if self._engine is None:
            self._engine = create_async_engine(
                self.db_url,
                echo=False,
                future=True,
                connect_args={"check_same_thread": False},
            )
        return self._engine

    @property
    def async_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        获取或创建异步会话工厂

        用于创建数据库会话实例。
        """
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
        return self._async_session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        获取异步数据库会话

        使用上下文管理器模式提供会话，自动处理提交和回滚。
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """
        关闭数据库连接

        清理资源，关闭引擎和会话工厂。
        """
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._async_session_factory = None


# 全局数据库实例
db_config = DatabaseConfig()


async def init_database() -> None:
    """
    初始化数据库表结构

    创建所有模型对应的数据库表。
    """
    from app.models import Base

    async with db_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_default_data() -> None:
    """
    初始化默认数据

    初始化系统的默认数据：行为配置、预置场景、系统配置。
    """
    from app.models import (
        ActionConfig,
        PresetScene,
        SystemConfig,
    )

    async for session in db_config.get_session():
        # 初始化行为配置数据（如果表为空）
        action_count = await session.execute(
            text("SELECT COUNT(*) FROM action_config")
        )
        if action_count.scalar() == 0:
            await _init_action_configs(session)

        # 初始化预置场景数据（如果表为空）
        scene_count = await session.execute(
            text("SELECT COUNT(*) FROM preset_scene")
        )
        if scene_count.scalar() == 0:
            await _init_preset_scenes(session)

        # 初始化系统配置数据（如果表为空）
        config_count = await session.execute(
            text("SELECT COUNT(*) FROM system_config")
        )
        if config_count.scalar() == 0:
            await _init_system_config(session)


async def _init_action_configs(session: AsyncSession) -> None:
    """
    初始化20项标准互动行为配置

    使用学术模型中的完整行为描述，包含外交、经济、军事和信息四大类行为。
    这些行为配置在系统初始化时自动加载，全程不可修改。

    Args:
        session: 数据库会话
    """
    from app.models import ActionConfig

    # 学术文档中定义的完整20项互动行为描述
    actions = [
        {
            "action_name": "发表公开声明",
            "action_en_name": "MAKE PUBLIC STATEMENT",
            "action_category": "外交手段",
            "action_desc": "行为方针对目标方发表各类公开声明，涵盖拒绝评论、发表正负向评论、考量政策选项、承认/宣示/否认责任、开展象征性行动、表达共情评论、传递共识等所有未另行分类的公开言语表述行为，是基础的二元言语互动行为",
            "respect_sov": True,
            "initiator_power_change": 0,
            "target_power_change": 0,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "呼吁/请求",
            "action_en_name": "APPEAL",
            "action_category": "外交手段",
            "action_desc": "行为方向目标方提出各类诉求与请求，包括呼吁开展经济/军事/司法/情报领域合作、寻求外交政策支持、申请各类援助、呼吁政治改革/对方做出让步，以及请求开展谈判、调解、争端解决等所有未另行分类的诉求表达行为",
            "respect_sov": True,
            "initiator_power_change": 1,
            "target_power_change": 0,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "表达合作意向",
            "action_en_name": "EXPRESS INTENT TO COOPERATE",
            "action_category": "外交手段",
            "action_desc": "行为方明确表达与目标方未来开展合作的意愿，涵盖表达各领域合作意向、承诺提供各类援助、表达实施政治改革的意愿、承诺做出让步，以及表达参与谈判、调解、争端解决的意向等所有未另行分类的合作意愿表达行为",
            "respect_sov": True,
            "initiator_power_change": 2,
            "target_power_change": 1,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "协商/磋商",
            "action_en_name": "CONSULT",
            "action_category": "外交手段",
            "action_desc": "行为方与目标方开展双向沟通协商，包括电话沟通、出访、接待来访、第三方地点会面、开展调解、进行谈判等所有未另行分类的主体间平等磋商互动行为",
            "respect_sov": True,
            "initiator_power_change": 3,
            "target_power_change": 3,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "开展外交合作",
            "action_en_name": "ENGAGE IN DIPLOMATIC COOPERATION",
            "action_category": "外交手段",
            "action_desc": "行为方与目标方开展官方外交层面的合作互动，涵盖赞扬/背书、口头辩护、为对方声援、授予外交承认、正式道歉、宽恕、签署正式协议等所有未另行分类的外交合作行为",
            "respect_sov": True,
            "initiator_power_change": 4,
            "target_power_change": 4,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "开展实质性合作",
            "action_en_name": "ENGAGE IN MATERIAL COOPERATION",
            "action_category": "经济手段",
            "action_desc": "行为方与目标方开展实体层面的实质性合作，包括经济合作、军事合作、司法合作、情报/信息共享等所有未另行分类的、非言语的实际合作行动",
            "respect_sov": True,
            "initiator_power_change": 5,
            "target_power_change": 5,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "提供援助",
            "action_en_name": "PROVIDE AID",
            "action_category": "经济手段",
            "action_desc": "行为方针对目标方提供各类援助支持，涵盖经济援助、军事援助、人道主义援助、军事保护/维和行动，以及授予庇护等所有未另行分类的援助提供行为",
            "respect_sov": True,
            "initiator_power_change": 2,
            "target_power_change": 6,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "让步/屈服",
            "action_en_name": "YIELD",
            "action_category": "外交手段",
            "action_desc": "行为方向目标方做出妥协与让步，包括放宽行政制裁、缓和异议管控、接受政治改革诉求、归还/释放人员与财产、放宽经济制裁、允许国际介入、军事行动降级、宣布停火、撤军/军事投降等所有未另行分类的让步行为",
            "respect_sov": True,
            "initiator_power_change": -5,
            "target_power_change": 5,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "调查",
            "action_en_name": "INVESTIGATE",
            "action_category": "信息手段",
            "action_desc": "行为方针对目标方开展各类官方调查活动，涵盖犯罪/腐败调查、人权侵犯调查、军事行动调查、战争罪调查等所有未另行分类的调查行为",
            "respect_sov": False,
            "initiator_power_change": -1,
            "target_power_change": -2,
            "is_initiative": True,
            "is_response": False
        },
        {
            "action_name": "要求/索要",
            "action_en_name": "DEMAND",
            "action_category": "外交手段",
            "action_desc": "行为方向目标方提出各类强制性要求，包括要求对方开展合作、提供援助、实施政治改革、做出让步，以及要求对方进行谈判、调解、争端解决等所有未另行分类的、具有强制诉求属性的行为",
            "respect_sov": False,
            "initiator_power_change": -2,
            "target_power_change": -1,
            "is_initiative": True,
            "is_response": False
        },
        {
            "action_name": "表达不满/不赞成",
            "action_en_name": "DISAPPROVE",
            "action_category": "外交手段",
            "action_desc": "行为方向目标方表达负面态度与异议，涵盖批评/谴责、各类指控、煽动反对、正式投诉、提起诉讼、司法定罪等所有未另行分类的不赞成行为",
            "respect_sov": False,
            "initiator_power_change": 0,
            "target_power_change": -1,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "拒绝",
            "action_en_name": "REJECT",
            "action_category": "外交手段",
            "action_desc": "行为方拒绝目标方提出的各类诉求与提议，包括拒绝合作、拒绝援助/改革诉求、拒绝做出让步、拒绝谈判/调解/争端解决方案、违背规范/法律、行使否决权等所有未另行分类的拒绝行为",
            "respect_sov": True,
            "initiator_power_change": 1,
            "target_power_change": -1,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "威胁",
            "action_en_name": "THREATEN",
            "action_category": "信息手段",
            "action_desc": "行为方向目标方发出各类威胁性表述，涵盖非武力制裁威胁、行政制裁威胁、煽动抗议/镇压威胁、中断谈判/调解威胁、军事武力威胁、发出最后通牒等所有未另行分类的威胁行为",
            "respect_sov": False,
            "initiator_power_change": -3,
            "target_power_change": -2,
            "is_initiative": True,
            "is_response": False
        },
        {
            "action_name": "抗议",
            "action_en_name": "PROTEST",
            "action_category": "外交手段",
            "action_desc": "行为方针对目标方开展各类政治异议与抗议行动，涵盖集会示威、绝食抗议、罢工/抵制、封锁道路、暴力抗议/骚乱等所有未另行分类的集体政治抗议行为",
            "respect_sov": False,
            "initiator_power_change": -4,
            "target_power_change": -3,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "展示军事姿态",
            "action_en_name": "EXHIBIT MILITARY POSTURE",
            "action_category": "军事手段",
            "action_desc": "行为方针对目标方展示军警力量与军事威慑姿态，包括提升警察/军事警戒级别、动员/增强警察/武装/网络军事力量等所有未实际使用武力、仅做力量展示的行为",
            "respect_sov": False,
            "initiator_power_change": -2,
            "target_power_change": -3,
            "is_initiative": True,
            "is_response": False
        },
        {
            "action_name": "降级关系",
            "action_en_name": "REDUCE RELATIONS",
            "action_category": "外交手段",
            "action_desc": "行为方针对目标方降级双边互动关系，涵盖降级/断绝外交关系、削减/ari止各类援助、实施禁运/抵制/制裁、中断谈判/调解、驱逐/撤出相关人员与机构等所有未另行分类的关系降级行为",
            "respect_sov": True,
            "initiator_power_change": -1,
            "target_power_change": -4,
            "is_initiative": True,
            "is_response": True
        },
        {
            "action_name": "胁迫/强制",
            "action_en_name": "COERCE",
            "action_category": "军事手段",
            "action_desc": "行为方针对目标方实施强制性胁迫行动，涵盖扣押/损毁财产、实施行政制裁、逮捕/拘留、驱逐个人、暴力镇压、网络攻击等所有未另行分类的强制胁迫行为",
            "respect_sov": False,
            "initiator_power_change": -5,
            "target_power_change": -6,
            "is_initiative": True,
            "is_response": False
        },
        {
            "action_name": "攻击/袭击",
            "action_en_name": "ASSAULT",
            "action_category": "军事手段",
            "action_desc": "行为方针对目标方使用非常规暴力行动，涵盖绑架/劫持人质、人身/性侵犯、酷刑、各类非军事爆炸袭击、使用人肉盾牌、暗杀/暗杀未遂等所有未另行分类的非常规暴力行为",
            "respect_sov": False,
            "initiator_power_change": -8,
            "target_power_change": -7,
            "is_initiative": True,
            "is_response": False
        },
        {
            "action_name": "交战/使用常规军事武力",
            "action_en_name": "FIGHT",
            "action_category": "军事手段",
            "action_desc": "行为方针对目标方使用常规军事武力开展交战，涵盖实施军事封锁、占领领土、轻武器交火、火炮/坦克作战、空中军事打击、违反停火协议等所有未另行分类的常规军事武力使用行为",
            "respect_sov": False,
            "initiator_power_change": -7,
            "target_power_change": -9,
            "is_initiative": True,
            "is_response": False
        },
        {
            "action_name": "实施非常规大规模暴力",
            "action_en_name": "ENGAGE IN UNCONVENTIONAL MASS VIOLENCE",
            "action_category": "军事手段",
            "action_desc": "行为方针对目标方实施非常规大规模暴力行动，涵盖大规模驱逐、大规模屠杀、种族清洗、使用化学/生物/放射性/核武器等大规模杀伤性武器的所有未另行分类的极端暴力行为",
            "respect_sov": False,
            "initiator_power_change": -10,
            "target_power_change": -10,
            "is_initiative": True,
            "is_response": False
        }
    ]

    # 批量添加所有行为配置到数据库
    for action_data in actions:
        action = ActionConfig(**action_data)
        session.add(action)


async def _init_preset_scenes(session: AsyncSession) -> None:
    """
    初始化预置仿真场景

    暂未实现，计划添加3个经典学术场景供一键启动。

    Args:
        session: 数据库会话
    """
    # 待实现：添加3个经典学术场景
    pass


async def _init_system_config(session: AsyncSession) -> None:
    """
    初始化系统配置

    设置 LLM 模型、API 配置、仿真并发数等系统默认参数。

    Args:
        session: 数据库会话
    """
    from app.models import SystemConfig

    # 默认系统配置项
    configs = [
        {
            "config_key": "llm_model_name",
            "config_value": "gpt-4-turbo",
            "config_desc": "LLM模型名称",
        },
        {
            "config_key": "llm_api_key",
            "config_value": "",
            "config_desc": "LLM API密钥",
        },
        {
            "config_key": "llm_api_base",
            "config_value": "",
            "config_desc": "LLM API基础URL",
        },
        {
            "config_key": "llm_timeout",
            "config_value": "60",
            "config_desc": "LLM调用超时时间（秒）",
        },
        {
            "config_key": "llm_max_retries",
            "config_value": "3",
            "config_desc": "LLM调用最大重试次数",
        },
        {
            "config_key": "simulation_concurrency",
            "config_value": "5",
            "config_desc": "仿真并发数",
        },
        {
            "config_key": "log_level",
            "config_value": "INFO",
            "config_desc": "日志级别",
        },
        {
            "config_key": "default_scene_id",
            "config_value": "1",
            "config_desc": "默认场景ID",
        },
    ]

    for config_data in configs:
        config = SystemConfig(**config_data)
        session.add(config)
