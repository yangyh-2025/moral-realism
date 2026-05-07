"""
CINC数据加载模块
CINC Data Loader Module

加载COW NMC v6.0 CINC数据集（1816-2016, 217个国家），
提供按国家代码+年份查询CINC数据的API。

数据来源：cinc/NMC-60-abridged/NMC-60-abridged.csv
字段说明：
- stateabb: COW国家缩写代码
- ccode: COW国家数字代码
- year: 年份
- milex: 军事支出（千美元）
- milper: 军事人员（千人）
- irst: 钢铁产量（千吨）
- pec: 一次能源消耗（千吨煤当量）
- tpop: 总人口（千人）
- upop: 城市人口（千人）
- cinc: CINC综合国力指数（比例值，0-1）
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class CINCRecord:
    """单条CINC数据记录"""
    stateabb: str
    ccode: int
    year: int
    milex: float  # 军事支出
    milper: float  # 军事人员
    irst: float  # 钢铁产量
    pec: float  # 能源消耗
    tpop: float  # 总人口
    upop: float  # 城市人口
    cinc: float  # CINC指数

    def to_dict(self) -> Dict:
        return {
            "stateabb": self.stateabb,
            "ccode": self.ccode,
            "year": self.year,
            "milex": self.milex,
            "milper": self.milper,
            "irst": self.irst,
            "pec": self.pec,
            "tpop": self.tpop,
            "upop": self.upop,
            "cinc": self.cinc,
        }


# COW国家代码到中文名称的映射（常见国家）
COW_COUNTRY_NAMES = {
    2: "美国", 20: "加拿大", 40: "古巴", 70: "墨西哥", 100: "哥伦比亚",
    101: "委内瑞拉", 130: "厄瓜多尔", 135: "秘鲁", 140: "巴西", 145: "玻利维亚",
    150: "巴拉圭", 155: "智利", 160: "阿根廷", 165: "乌拉圭",
    200: "英国", 205: "爱尔兰", 210: "荷兰", 211: "比利时", 212: "卢森堡",
    220: "法国", 225: "瑞士", 230: "西班牙", 235: "葡萄牙", 245: "巴伐利亚",
    255: "德国", 260: "西德", 265: "东德", 290: "波兰", 300: "奥匈帝国",
    305: "奥地利", 310: "匈牙利", 315: "捷克斯洛伐克", 316: "捷克",
    317: "斯洛伐克", 325: "意大利", 327: "教皇国", 339: "阿尔巴尼亚",
    343: "马其顿", 344: "克罗地亚", 345: "南斯拉夫", 346: "波斯尼亚",
    347: "科索沃", 349: "斯洛文尼亚", 350: "希腊", 352: "塞浦路斯",
    355: "保加利亚", 359: "摩尔多瓦", 360: "罗马尼亚", 365: "俄罗斯",
    366: "爱沙尼亚", 367: "拉脱维亚", 368: "立陶宛", 369: "乌克兰",
    370: "白俄罗斯", 371: "亚美尼亚", 372: "格鲁吉亚", 373: "阿塞拜疆",
    375: "芬兰", 380: "瑞典", 385: "挪威", 390: "丹麦", 395: "冰岛",
    402: "佛得角", 403: "圣多美和普林西比", 404: "几内亚比绍", 411: "赤道几内亚",
    420: "冈比亚", 432: "马里", 433: "塞内加尔", 434: "贝宁", 435: "毛里塔尼亚",
    436: "尼日尔", 437: "科特迪瓦", 438: "几内亚", 439: "布基纳法索",
    450: "利比里亚", 451: "塞拉利昂", 452: "加纳", 461: "多哥", 471: "喀麦隆",
    475: "尼日利亚", 481: "加蓬", 482: "中非共和国", 483: "乍得",
    484: "刚果共和国", 490: "刚果民主共和国", 500: "乌干达", 501: "肯尼亚",
    510: "坦桑尼亚", 511: "桑给巴尔", 516: "布隆迪", 517: "卢旺达",
    520: "索马里", 522: "吉布提", 530: "埃塞俄比亚", 531: "厄立特里亚",
    540: "安哥拉", 541: "莫桑比克", 551: "赞比亚", 552: "津巴布韦",
    553: "马拉维", 560: "南非", 565: "纳米比亚", 570: "莱索托", 571: "博茨瓦纳",
    572: "斯威士兰", 580: "马达加斯加", 581: "科摩罗", 590: "毛里求斯",
    591: "塞舌尔", 600: "摩洛哥", 615: "阿尔及利亚", 616: "突尼斯",
    620: "利比亚", 625: "苏丹", 626: "南苏丹", 630: "伊朗", 640: "土耳其",
    645: "伊拉克", 651: "埃及", 652: "叙利亚", 660: "黎巴嫩", 663: "约旦",
    666: "以色列", 670: "沙特阿拉伯", 678: "也门", 680: "南也门", 690: "科威特",
    692: "巴林", 694: "卡塔尔", 696: "阿联酋", 698: "阿曼", 700: "阿富汗",
    701: "土库曼斯坦", 702: "塔吉克斯坦", 703: "吉尔吉斯斯坦", 704: "乌兹别克斯坦",
    705: "哈萨克斯坦", 710: "中国", 712: "蒙古", 713: "台湾", 730: "朝鲜",
    731: "北朝鲜", 732: "韩国", 740: "日本", 750: "印度", 760: "不丹",
    770: "巴基斯坦", 771: "孟加拉国", 775: "缅甸", 780: "斯里兰卡", 781: "马尔代夫",
    790: "尼泊尔", 800: "泰国", 811: "柬埔寨", 812: "老挝", 815: "越南",
    816: "北越南", 817: "南越南", 820: "马来西亚", 830: "新加坡", 835: "文莱",
    840: "菲律宾", 850: "印度尼西亚", 860: "东帝汶", 900: "澳大利亚",
    910: "巴布亚新几内亚", 920: "新西兰", 940: "所罗门群岛", 950: "斐济",
    955: "汤加", 970: "基里巴斯", 990: "西萨摩亚",
}

# 糊名后的国家名称映射（用于学术研究保护隐私）
# COW代码 -> (英文缩写, 真实中文名)
COW_COUNTRY_INFO = {code: {"name": name, "stateabb": ""} for code, name in COW_COUNTRY_NAMES.items()}


class CINCDataLoader:
    """
    CINC数据加载器 - 单例模式

    负责加载并缓存COW NMC v6.0数据，提供按国家代码、年份的查询接口。
    """

    _instance: Optional["CINCDataLoader"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 数据存储：以(ccode, year)为键
        self._records: Dict[Tuple[int, int], CINCRecord] = {}
        # 国家代码到英文缩写的映射
        self._ccode_to_abb: Dict[int, str] = {}
        # 英文缩写到国家代码的映射
        self._abb_to_ccode: Dict[str, int] = {}
        # 所有可用年份
        self._available_years: set = set()
        # 所有可用国家代码
        self._available_ccodes: set = set()

        self._load_data()
        self._initialized = True

    def _find_csv_path(self) -> Path:
        """
        查找CINC CSV数据文件路径

        优先按相对路径查找，找不到时按工作目录查找
        """
        # 从app/core/cinc_data_loader.py出发推算工作根目录
        current_file = Path(__file__).resolve()
        # python/app/core -> python/
        project_root = current_file.parent.parent.parent
        csv_path = project_root / "cinc" / "NMC-60-abridged" / "NMC-60-abridged.csv"

        if csv_path.exists():
            return csv_path

        # 备用路径：从当前工作目录查找
        cwd_path = Path.cwd() / "cinc" / "NMC-60-abridged" / "NMC-60-abridged.csv"
        if cwd_path.exists():
            return cwd_path

        raise FileNotFoundError(
            f"CINC数据文件未找到，已尝试: {csv_path} 和 {cwd_path}"
        )

    def _parse_float(self, value: str) -> float:
        """
        解析浮点数（处理 -9 等缺失值标记）

        COW数据集中，-9 表示数据缺失。
        """
        try:
            v = float(value)
            if v == -9:
                return 0.0
            return v
        except (ValueError, TypeError):
            return 0.0

    def _load_data(self) -> None:
        """加载CSV数据到内存"""
        try:
            csv_path = self._find_csv_path()
            logger.info(f"正在加载CINC数据: {csv_path}")

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    try:
                        ccode = int(row["ccode"])
                        year = int(row["year"])
                        stateabb = row["stateabb"].strip()

                        record = CINCRecord(
                            stateabb=stateabb,
                            ccode=ccode,
                            year=year,
                            milex=self._parse_float(row.get("milex", "0")),
                            milper=self._parse_float(row.get("milper", "0")),
                            irst=self._parse_float(row.get("irst", "0")),
                            pec=self._parse_float(row.get("pec", "0")),
                            tpop=self._parse_float(row.get("tpop", "0")),
                            upop=self._parse_float(row.get("upop", "0")),
                            cinc=self._parse_float(row.get("cinc", "0")),
                        )

                        self._records[(ccode, year)] = record
                        self._ccode_to_abb[ccode] = stateabb
                        self._abb_to_ccode[stateabb] = ccode
                        self._available_years.add(year)
                        self._available_ccodes.add(ccode)
                        count += 1
                    except (ValueError, KeyError) as e:
                        logger.warning(f"跳过无效行: {row}, 错误: {e}")
                        continue

            logger.info(
                f"CINC数据加载完成: {count} 条记录, "
                f"{len(self._available_ccodes)} 个国家, "
                f"{min(self._available_years)}-{max(self._available_years)} 年"
            )
        except Exception as e:
            logger.error(f"CINC数据加载失败: {e}", exc_info=True)
            raise

    def get_record(self, ccode: int, year: int) -> Optional[CINCRecord]:
        """
        按国家代码和年份获取CINC记录

        Args:
            ccode: COW国家数字代码
            year: 年份

        Returns:
            CINCRecord对象，未找到则返回None
        """
        return self._records.get((ccode, year))

    def get_record_by_abb(self, stateabb: str, year: int) -> Optional[CINCRecord]:
        """
        按国家英文缩写和年份获取CINC记录

        Args:
            stateabb: COW国家缩写代码（如"USA"）
            year: 年份

        Returns:
            CINCRecord对象，未找到则返回None
        """
        ccode = self._abb_to_ccode.get(stateabb.upper())
        if ccode is None:
            return None
        return self.get_record(ccode, year)

    def get_country_name(self, ccode: int) -> str:
        """
        按COW数字代码获取国家中文名称

        Args:
            ccode: COW国家数字代码

        Returns:
            中文名称，未知则返回缩写或代码
        """
        if ccode in COW_COUNTRY_NAMES:
            return COW_COUNTRY_NAMES[ccode]
        # 回退到英文缩写
        abb = self._ccode_to_abb.get(ccode)
        if abb:
            return abb
        return f"Country_{ccode}"

    def get_available_years(self) -> List[int]:
        """获取所有可用年份的有序列表"""
        return sorted(self._available_years)

    def get_available_countries(self) -> List[Dict]:
        """
        获取所有可用国家列表

        Returns:
            列表，每项为 {"ccode": int, "stateabb": str, "name": str}
        """
        return [
            {
                "ccode": ccode,
                "stateabb": self._ccode_to_abb.get(ccode, ""),
                "name": self.get_country_name(ccode),
            }
            for ccode in sorted(self._available_ccodes)
        ]

    def get_countries_by_year(self, year: int) -> List[Dict]:
        """
        获取指定年份所有有数据的国家

        Args:
            year: 年份

        Returns:
            国家列表
        """
        countries = []
        for (ccode, y), record in self._records.items():
            if y == year and record.cinc > 0:
                countries.append({
                    "ccode": ccode,
                    "stateabb": record.stateabb,
                    "name": self.get_country_name(ccode),
                    "cinc": record.cinc,
                    "milex": record.milex,
                    "milper": record.milper,
                    "irst": record.irst,
                    "pec": record.pec,
                    "tpop": record.tpop,
                    "upop": record.upop,
                })
        # 按CINC降序排列
        countries.sort(key=lambda x: x["cinc"], reverse=True)
        return countries

    def get_default_record(self) -> CINCRecord:
        """
        获取默认CINC记录（用于无数据时的兜底）
        使用2016年USA的数据作为模板，但cinc设为很小的值
        """
        return CINCRecord(
            stateabb="DEFAULT",
            ccode=0,
            year=2016,
            milex=1000.0,
            milper=10.0,
            irst=100.0,
            pec=1000.0,
            tpop=10000.0,
            upop=5000.0,
            cinc=0.001,
        )


# 全局单例
_cinc_loader: Optional[CINCDataLoader] = None


def get_cinc_loader() -> CINCDataLoader:
    """获取CINC数据加载器单例"""
    global _cinc_loader
    if _cinc_loader is None:
        _cinc_loader = CINCDataLoader()
    return _cinc_loader
