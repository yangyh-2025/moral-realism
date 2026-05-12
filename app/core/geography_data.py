"""欧洲国家邻接/地缘关系数据 (1913 / 1938 / 1946 三个历史快照)

本模块为三个预设场景提供默认邻接关系初始化数据:
- 场景1: 一战前 1913 欧洲 (19国)
- 场景2: 二战前 1938 欧洲 (28国)
- 场景3: 冷战前 1946 欧洲 (25国)

每个年份提供陆地邻接 (EUROPE_<YEAR>_NEIGHBORS) 和海上邻接 (SEA_LINKS_<YEAR>) 两类数据。
邻接关系按实际历史边界设定,与现有场景中存在的国家集合对齐,不存在的国家忽略。

LLM prompt 中的「邻接关系简报」由 decision_engine 直接从 DB 读出,
不再依赖此模块的任何运行时函数。
"""

from typing import Dict, Set, Tuple

# 直接接壤(陆地共同边境)
EUROPE_1913_NEIGHBORS = {
    'GMY': {'FRN', 'AUH', 'BEL', 'NTH', 'DEN', 'RUS', 'SWZ'},  # 含分治波兰接俄
    'RUS': {'GMY', 'AUH', 'ROM', 'TUR'},  # 奥斯曼通过高加索接壤
    'UKG': set(),  # 岛国, 陆地无邻国(IRE不在19国内)
    'FRN': {'GMY', 'BEL', 'SPN', 'ITA', 'SWZ'},
    'AUH': {'GMY', 'RUS', 'ITA', 'YUG', 'ROM', 'SWZ'},
    'ITA': {'FRN', 'AUH', 'SWZ'},
    'TUR': {'GRC', 'BUL', 'RUS'},
    'BUL': {'TUR', 'GRC', 'ROM', 'YUG'},
    'SPN': {'FRN', 'POR'},
    'BEL': {'FRN', 'GMY', 'NTH'},
    'GRC': {'TUR', 'BUL'},
    'SWD': {'NOR'},  # 1905独立后陆地接壤挪威
    'NTH': {'GMY', 'BEL'},
    'ROM': {'RUS', 'AUH', 'BUL', 'YUG'},
    'POR': {'SPN'},
    'DEN': {'GMY'},
    'SWZ': {'GMY', 'FRN', 'AUH', 'ITA'},
    'YUG': {'AUH', 'BUL', 'ROM'},  # 即塞尔维亚
    'NOR': {'SWD'},
}

# 海上邻接 (短距离海上接壤, 用于英国/丹麦/挪威/瑞典等沿岸国)
SEA_LINKS = {
    'UKG': {'NTH', 'BEL', 'FRN', 'GMY', 'DEN', 'NOR', 'SWD', 'POR'},
    'TUR': {'GRC', 'UKG', 'RUS', 'ITA'},
    'ITA': {'GRC', 'TUR', 'SPN', 'UKG'},
    'GRC': {'TUR', 'ITA', 'UKG'},
    'SWD': {'GMY', 'DEN', 'NOR', 'RUS'},
    'DEN': {'GMY', 'SWD', 'NOR', 'UKG'},
    'NOR': {'SWD', 'DEN', 'UKG'},
    'NTH': {'UKG', 'GMY', 'BEL', 'NOR', 'DEN'},
    'BEL': {'UKG', 'NTH', 'FRN'},
    'FRN': {'UKG', 'SPN', 'ITA'},
    'GMY': {'UKG', 'DEN', 'SWD', 'NOR', 'NTH'},
    'SPN': {'UKG', 'FRN', 'ITA', 'POR'},
    'POR': {'SPN', 'UKG'},
    'RUS': {'SWD', 'DEN', 'TUR'},
}

# 中文别名到 COW 3字母代码的映射 (场景1: 1913 欧洲)
# 用于 agent_name -> country_code 兜底解析
ALIAS_TO_COW = {
    '强国甲': 'GMY', '强国乙': 'RUS', '强国丙': 'UKG',
    '中等国甲': 'FRN', '中等国乙': 'AUH', '中等国丙': 'ITA',
    '小国甲': 'TUR', '小国乙': 'BUL', '小国丙': 'SPN', '小国丁': 'BEL',
    '小国戊': 'GRC', '小国己': 'SWD', '小国庚': 'NTH', '小国辛': 'ROM',
    '小国壬': 'POR', '小国癸': 'DEN', '小国子': 'SWZ', '小国丑': 'YUG',
    '小国寅': 'NOR',
}

# COW 数字代码(int, NMC-60-abridged.csv 中的 ccode) -> COW 3字母代码 映射
# 仅覆盖本仿真涵盖的 19 个 1913 欧洲国家
COW_NUM_TO_ABB = {
    255: 'GMY',  # Germany
    365: 'RUS',  # Russia
    200: 'UKG',  # United Kingdom
    220: 'FRN',  # France
    300: 'AUH',  # Austria-Hungary
    325: 'ITA',  # Italy
    640: 'TUR',  # Ottoman Empire / Turkey
    355: 'BUL',  # Bulgaria
    230: 'SPN',  # Spain
    211: 'BEL',  # Belgium
    350: 'GRC',  # Greece
    380: 'SWD',  # Sweden
    210: 'NTH',  # Netherlands
    360: 'ROM',  # Romania
    235: 'POR',  # Portugal
    390: 'DEN',  # Denmark
    225: 'SWZ',  # Switzerland
    345: 'YUG',  # Serbia / Yugoslavia
    385: 'NOR',  # Norway
}


# ============================================================================
# 场景2: 1938 年欧洲 (28国)
# ============================================================================
# 关键背景:
# - 波兰已独立 (1918), 与 GMY/CZE/LIT/ROM/HUN/RUS 陆地接壤
# - 奥匈解体, 由 CZE/HUN/YUG 等承接 (本场景无奥地利)
# - 波罗的海三国 LAT/LIT/EST 独立
# - 芬兰 FIN 独立, 爱尔兰 IRE 独立
# - 阿尔巴尼亚 ALB、卢森堡 LUX 独立
# - 1938 年慕尼黑协议前 CZE 仍完整

EUROPE_1938_NEIGHBORS = {
    'GMY': {'FRN', 'BEL', 'NTH', 'DEN', 'POL', 'CZE', 'SWZ', 'LUX', 'LIT'},  # LIT 通过东普鲁士接壤
    'RUS': {'POL', 'ROM', 'TUR', 'FIN', 'LAT', 'EST'},  # TUR 通过高加索
    'UKG': set(),  # 岛国
    'FRN': {'GMY', 'BEL', 'SPN', 'ITA', 'SWZ', 'LUX'},
    'ITA': {'FRN', 'SWZ', 'YUG'},  # 1938 ITA 与 YUG 接壤(Istria/Rijeka 一线)
    'POL': {'GMY', 'CZE', 'LIT', 'ROM', 'HUN', 'RUS', 'LAT'},  # 1938 POL-LAT 短界
    'SPN': {'FRN', 'POR'},
    'CZE': {'GMY', 'POL', 'HUN', 'ROM'},  # 含 SVK 部分, 与 ROM 短界
    'BEL': {'FRN', 'GMY', 'NTH', 'LUX'},
    'ROM': {'RUS', 'POL', 'HUN', 'YUG', 'BUL', 'CZE'},
    'TUR': {'GRC', 'BUL', 'RUS'},
    'YUG': {'ITA', 'HUN', 'ROM', 'BUL', 'GRC', 'ALB'},
    'SWD': {'NOR', 'FIN'},
    'NTH': {'GMY', 'BEL'},
    'HUN': {'CZE', 'POL', 'ROM', 'YUG'},
    'GRC': {'YUG', 'BUL', 'ALB', 'TUR'},
    'POR': {'SPN'},
    'LUX': {'GMY', 'FRN', 'BEL'},
    'DEN': {'GMY'},
    'FIN': {'RUS', 'NOR', 'SWD'},
    'SWZ': {'GMY', 'FRN', 'ITA'},
    'BUL': {'TUR', 'GRC', 'ROM', 'YUG'},
    'NOR': {'SWD', 'FIN'},
    'LAT': {'LIT', 'EST', 'RUS', 'POL'},
    'LIT': {'GMY', 'POL', 'LAT'},
    'IRE': set(),  # 岛国
    'EST': {'LAT', 'RUS'},
    'ALB': {'YUG', 'GRC'},
}

# 1938 海上邻接 (短距离海上)
SEA_LINKS_1938 = {
    'UKG': {'NTH', 'BEL', 'FRN', 'GMY', 'DEN', 'NOR', 'SWD', 'POR', 'IRE'},
    'IRE': {'UKG'},
    'TUR': {'GRC', 'UKG', 'RUS', 'ITA', 'BUL', 'ROM'},
    'ITA': {'GRC', 'TUR', 'SPN', 'UKG', 'YUG', 'ALB', 'FRN'},
    'GRC': {'TUR', 'ITA', 'UKG', 'ALB', 'YUG', 'BUL'},
    'SWD': {'GMY', 'DEN', 'NOR', 'RUS', 'POL', 'FIN', 'LAT', 'EST', 'LIT'},
    'DEN': {'GMY', 'SWD', 'NOR', 'UKG'},
    'NOR': {'SWD', 'DEN', 'UKG'},
    'NTH': {'UKG', 'GMY', 'BEL', 'NOR', 'DEN'},
    'BEL': {'UKG', 'NTH', 'FRN'},
    'FRN': {'UKG', 'SPN', 'ITA'},
    'GMY': {'UKG', 'DEN', 'SWD', 'NOR', 'NTH', 'POL', 'LIT', 'LAT', 'EST', 'FIN', 'RUS'},
    'SPN': {'UKG', 'FRN', 'ITA', 'POR'},
    'POR': {'SPN', 'UKG'},
    'RUS': {'SWD', 'DEN', 'TUR', 'GMY', 'FIN', 'POL', 'EST', 'LAT'},
    'POL': {'SWD', 'DEN', 'GMY', 'LAT', 'LIT', 'EST', 'FIN', 'RUS'},
    'FIN': {'SWD', 'NOR', 'RUS', 'EST', 'POL', 'LAT', 'LIT', 'GMY'},
    'LAT': {'SWD', 'EST', 'FIN', 'LIT', 'GMY', 'POL', 'RUS'},
    'LIT': {'SWD', 'GMY', 'POL', 'LAT', 'FIN'},
    'EST': {'SWD', 'FIN', 'LAT', 'RUS', 'POL', 'GMY'},
    'BUL': {'TUR', 'ROM', 'RUS'},
    'ROM': {'TUR', 'BUL', 'RUS'},
    'ALB': {'ITA', 'GRC', 'YUG'},
    'YUG': {'ITA', 'GRC', 'ALB'},
}

# 中文别名到 COW 3字母代码的映射 (场景2: 1938 欧洲)
ALIAS_TO_COW_1938 = {
    '强国甲': 'RUS', '强国乙': 'GMY', '强国丙': 'UKG',
    '中等国甲': 'FRN', '中等国乙': 'ITA', '中等国丙': 'POL',
    '小国甲': 'SPN', '小国乙': 'CZE', '小国丙': 'BEL', '小国丁': 'ROM',
    '小国戊': 'TUR', '小国己': 'YUG', '小国庚': 'SWD', '小国辛': 'NTH',
    '小国壬': 'HUN', '小国癸': 'GRC', '小国子': 'POR', '小国丑': 'LUX',
    '小国寅': 'DEN', '小国卯': 'FIN', '小国辰': 'SWZ', '小国巳': 'BUL',
    '小国午': 'NOR', '小国未': 'LAT', '小国申': 'LIT', '小国酉': 'IRE',
    '小国戌': 'EST', '小国亥': 'ALB',
}

# 1938 场景 index → COW 映射 (与 scene_service._create_scene2_agents 同步)
INDEX_TO_COW_1938 = {
    1: 'RUS', 2: 'GMY', 3: 'UKG', 4: 'FRN', 5: 'ITA', 6: 'POL',
    7: 'SPN', 8: 'CZE', 9: 'BEL', 10: 'ROM', 11: 'TUR', 12: 'YUG',
    13: 'SWD', 14: 'NTH', 15: 'HUN', 16: 'GRC', 17: 'POR', 18: 'LUX',
    19: 'DEN', 20: 'FIN', 21: 'SWZ', 22: 'BUL', 23: 'NOR', 24: 'LAT',
    25: 'LIT', 26: 'IRE', 27: 'EST', 28: 'ALB',
}


# ============================================================================
# 场景3: 1946 年欧洲 (25国)
# ============================================================================
# 关键背景 (与 1938 对比):
# - 二战后德国被分占, 本场景不含 GMY agent (邻接数据中也忽略 GMY)
# - 波兰边界西移 (奥得-尼斯线), 失去东部并入 RUS;
#   1946 场景中 POL 与 CZE/RUS/HUN(间接, 此处不直邻)/ROM(不接) 接壤
# - 波罗的海三国 LAT/LIT/EST 已并入苏联, 本场景无之
# - 阿尔巴尼亚 ALB 仍存在 (1944 后共产党政权)
# - 冰岛 ICE 新增 (1944 独立)

EUROPE_1946_NEIGHBORS = {
    'RUS': {'POL', 'ROM', 'TUR', 'FIN', 'CZE', 'HUN', 'NOR'},  # 二战后扩张, NOR 通过 Pechenga 短界
    'UKG': set(),  # 岛国
    'FRN': {'BEL', 'SPN', 'ITA', 'SWZ', 'LUX'},  # GMY 占领区不计入本场景 agent
    'ITA': {'FRN', 'SWZ', 'YUG'},
    'POL': {'CZE', 'RUS'},  # 1946 POL 主要陆邻 (西邻为分占德国, 本场景无 agent)
    'SPN': {'FRN', 'POR'},
    'TUR': {'GRC', 'BUL', 'RUS'},
    'CZE': {'POL', 'HUN', 'RUS'},  # 含 SVK 部分; 1945 后将 Subcarpathia 让予苏联,获 RUS 短陆界
    'BEL': {'FRN', 'NTH', 'LUX'},
    'NTH': {'BEL'},
    'SWD': {'NOR', 'FIN'},
    'YUG': {'ITA', 'HUN', 'ROM', 'BUL', 'GRC', 'ALB'},
    'ROM': {'RUS', 'HUN', 'YUG', 'BUL'},
    'HUN': {'CZE', 'ROM', 'YUG', 'RUS'},  # 与 RUS(占领区/Subcarpathia 后)接壤
    'GRC': {'YUG', 'BUL', 'ALB', 'TUR'},
    'BUL': {'TUR', 'GRC', 'ROM', 'YUG'},
    'POR': {'SPN'},
    'LUX': {'FRN', 'BEL'},
    'DEN': set(),  # 二战后与德接壤但本场景无 GMY, 留空陆邻
    'SWZ': {'FRN', 'ITA'},
    'NOR': {'SWD', 'FIN', 'RUS'},
    'FIN': {'RUS', 'NOR', 'SWD'},
    'IRE': set(),  # 岛国
    'ALB': {'YUG', 'GRC'},
    'ICE': set(),  # 岛国
}

# 1946 海上邻接
SEA_LINKS_1946 = {
    'UKG': {'NTH', 'BEL', 'FRN', 'DEN', 'NOR', 'SWD', 'POR', 'IRE', 'ICE'},
    'IRE': {'UKG'},
    'ICE': {'UKG', 'NOR'},
    'TUR': {'GRC', 'UKG', 'RUS', 'ITA', 'BUL', 'ROM'},
    'ITA': {'GRC', 'TUR', 'SPN', 'UKG', 'YUG', 'ALB', 'FRN'},
    'GRC': {'TUR', 'ITA', 'UKG', 'ALB', 'YUG', 'BUL'},
    'SWD': {'DEN', 'NOR', 'RUS', 'POL', 'FIN'},
    'DEN': {'SWD', 'NOR', 'UKG'},
    'NOR': {'SWD', 'DEN', 'UKG', 'ICE'},
    'NTH': {'UKG', 'BEL', 'NOR', 'DEN'},
    'BEL': {'UKG', 'NTH', 'FRN'},
    'FRN': {'UKG', 'SPN', 'ITA'},
    'SPN': {'UKG', 'FRN', 'ITA', 'POR'},
    'POR': {'SPN', 'UKG'},
    'RUS': {'SWD', 'DEN', 'TUR', 'FIN', 'POL', 'NOR'},
    'POL': {'SWD', 'DEN', 'FIN', 'RUS'},
    'FIN': {'SWD', 'NOR', 'RUS', 'POL'},
    'BUL': {'TUR', 'ROM', 'RUS'},
    'ROM': {'TUR', 'BUL', 'RUS'},
    'ALB': {'ITA', 'GRC', 'YUG'},
    'YUG': {'ITA', 'GRC', 'ALB'},
}

# 中文别名到 COW 3字母代码的映射 (场景3: 1946 欧洲)
ALIAS_TO_COW_1946 = {
    '强国甲': 'RUS', '强国乙': 'UKG',
    '中等国甲': 'FRN', '中等国乙': 'ITA', '中等国丙': 'POL',
    '小国甲': 'SPN', '小国乙': 'TUR', '小国丙': 'CZE', '小国丁': 'BEL',
    '小国戊': 'NTH', '小国己': 'SWD', '小国庚': 'YUG', '小国辛': 'ROM',
    '小国壬': 'HUN', '小国癸': 'GRC', '小国子': 'BUL', '小国丑': 'POR',
    '小国寅': 'LUX', '小国卯': 'DEN', '小国辰': 'SWZ', '小国巳': 'NOR',
    '小国午': 'FIN', '小国未': 'IRE', '小国申': 'ALB', '小国酉': 'ICE',
}

# 1946 场景 index → COW 映射 (与 scene_service._create_scene3_agents 同步)
INDEX_TO_COW_1946 = {
    1: 'RUS', 2: 'UKG', 3: 'FRN', 4: 'ITA', 5: 'POL',
    6: 'SPN', 7: 'TUR', 8: 'CZE', 9: 'BEL', 10: 'NTH',
    11: 'SWD', 12: 'YUG', 13: 'ROM', 14: 'HUN', 15: 'GRC',
    16: 'BUL', 17: 'POR', 18: 'LUX', 19: 'DEN', 20: 'SWZ',
    21: 'NOR', 22: 'FIN', 23: 'IRE', 24: 'ALB', 25: 'ICE',
}


def resolve_country_code(agent_name: str = None, country_code_num=None) -> str:
    """统一解析国家代码:
    优先用数字 COW 代码映射, 否则用中文别名映射, 都失败则返回空字符串。

    Args:
        agent_name: 中文别名(如 '强国甲')
        country_code_num: int 类型的 COW 数字代码(可选)

    Returns:
        3字母 COW 代码(如 'GMY'),失败则返回 ''
    """
    if country_code_num is not None:
        try:
            code = COW_NUM_TO_ABB.get(int(country_code_num))
            if code:
                return code
        except (ValueError, TypeError):
            pass
    if agent_name:
        return ALIAS_TO_COW.get(agent_name, '')
    return ''


def get_default_neighbors_for_scene(year: int, agent_map: Dict[int, int]) -> Set[Tuple[int, int]]:
    """
    根据场景年份返回默认邻接关系对子(agent_id 二元组, 已归一化 source<target)。

    Args:
        year: 场景年份, 当前支持 1913 / 1938 / 1946
        agent_map: Dict[int, int] - scene 内的 index(1-based) → 实际 agent_id 映射
                   - 1913: index 1..19 (见 INDEX_TO_COW_1913)
                   - 1938: index 1..28 (见 INDEX_TO_COW_1938)
                   - 1946: index 1..25 (见 INDEX_TO_COW_1946)

    Returns:
        Set of (smaller_agent_id, larger_agent_id) tuples; 未知年份返回空 set。
    """
    # 1913 场景的 index → COW 3字母 映射 (与 scene_service._create_scene1_agents 同步)
    INDEX_TO_COW_1913 = {
        1: 'GMY', 2: 'RUS', 3: 'UKG', 4: 'FRN', 5: 'AUH', 6: 'ITA',
        7: 'TUR', 8: 'BUL', 9: 'SPN', 10: 'BEL', 11: 'GRC', 12: 'SWD',
        13: 'NTH', 14: 'ROM', 15: 'POR', 16: 'DEN', 17: 'SWZ', 18: 'YUG', 19: 'NOR',
    }

    if year == 1913:
        index_to_cow = INDEX_TO_COW_1913
        land_neighbors = EUROPE_1913_NEIGHBORS
        sea_neighbors = SEA_LINKS
    elif year == 1938:
        index_to_cow = INDEX_TO_COW_1938
        land_neighbors = EUROPE_1938_NEIGHBORS
        sea_neighbors = SEA_LINKS_1938
    elif year == 1946:
        index_to_cow = INDEX_TO_COW_1946
        land_neighbors = EUROPE_1946_NEIGHBORS
        sea_neighbors = SEA_LINKS_1946
    else:
        return set()

    cow_to_index = {v: k for k, v in index_to_cow.items()}

    pairs: Set[Tuple[int, int]] = set()

    def _add_pair(c1: str, c2: str):
        idx1 = cow_to_index.get(c1)
        idx2 = cow_to_index.get(c2)
        if idx1 is None or idx2 is None:
            return
        aid1 = agent_map.get(idx1)
        aid2 = agent_map.get(idx2)
        if aid1 is None or aid2 is None:
            return
        a, b = (aid1, aid2) if aid1 < aid2 else (aid2, aid1)
        if a != b:
            pairs.add((a, b))

    # 合并陆地邻接 + 海上邻接 (二元)
    for c1, neighbors in land_neighbors.items():
        for c2 in neighbors:
            _add_pair(c1, c2)
    for c1, sea_set in sea_neighbors.items():
        for c2 in sea_set:
            _add_pair(c1, c2)

    return pairs
