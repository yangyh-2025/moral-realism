"""
国内冲突预测脚本 - 2025年和2026年预测
================================================

本脚本用于预测2025年和2026年的国内冲突风险水平（三分类：0/1/2）

主要功能：
1. 使用1961-2024年数据进行训练
2. 预测2025年，并递推预测2026年
3. 使用expanding-window三折时间序列交叉验证
4. 使用宏观F1得分作为评估指标
5. 对非连续变量使用合适的预测方法
6. 使用随机森林的直接预测结果，不使用固定阈值

作者说明：
- 添加了极其详细的中文注释
- 每个步骤、每个参数设置、每个函数的作用都有详细解释
- 适合编程水平不高的读者阅读和理解
"""

from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import matplotlib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTENC
from imblearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler, label_binarize

# 设置matplotlib为非交互式后端（不显示图形窗口，只保存文件）
matplotlib.use("Agg")

# 配置中文字体（在Windows上使用微软雅黑或SimHei）
from matplotlib import pyplot as plt
from matplotlib import font_manager
import platform

if platform.system() == "Windows":
    # Windows平台使用微软雅黑或SimHei
    fonts = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    for font in fonts:
        try:
            plt.rcParams['font.sans-serif'] = [font]
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
            break
        except:
            continue
else:
    # 其他平台使用SimHei或其他支持中文的字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 第一部分：全局配置和常量定义
# ============================================================================

# ----------------------------------------------------------------------------
# 变量定义部分
# ----------------------------------------------------------------------------

# 因变量列名：UCDP国内冲突三分类指标
# 取值范围：0/1/2（整数）
# 0 表示无冲突
# 1 表示低强度冲突
# 2 表示高强度冲突
DV_COLUMN = "UCDP_Civil_conflict_0_1_2"

# 自变量列名列表（共10项自变量）
# 注意：这些变量名必须与数据文件中的列名完全一致
IV_COLUMNS = [
    "polity",                    # 政体得分，范围：-10到10的整数
    "GDP_per_capita_ln",         # 人均GDP的对数值，范围：大于0
    "GDP_growth",                # GDP增长率，范围：无限制（可以是负数）
    "population_size",           # 0-14周岁人口占比，范围：0到1（百分比）
    "trade",                     # 贸易额占国民生产总值比例，范围：大于0
    "ethnic_diversity",          # 种族分化指数，范围：0到1
    "national_capacity",        # 国家综合国力指数，范围：0到1
    "government",                # 政府吸纳度，范围：0/1/2/3的整数
    "congress",                  # 议会吸纳度，范围：1到7，每增加0.5一个级别（只有.5和整数）
    "ucdp_neighbor_confilctnumber", # 发生冲突的邻国数量，范围：0到正无穷的正整数
]

# ----------------------------------------------------------------------------
# ARIMA模型预测的变量列表
# ----------------------------------------------------------------------------

# 使用ARIMA模型预测的连续变量列表
# 这些变量是连续变化的，适合使用时间序列方法（ARIMA）进行预测
# ARIMA（自回归积分滑动平均模型）适合处理具有趋势和季节性的连续时间序列数据
ARIMA_COLUMNS = [
    "GDP_per_capita_ln",         # 人均GDP对数值，连续变量，通常有明显的趋势
    "GDP_growth",                # GDP增长率，连续变量，波动性较大
    "trade",                     # 贸易额占比，连续变量，通常在一定范围内波动
]

# ----------------------------------------------------------------------------
# 简单外推方法预测的变量列表
# ----------------------------------------------------------------------------

# 使用简单外推方法预测的非连续变量列表
# 这些变量是离散的、整数或百分比变量，不适合使用ARIMA模型
# 简单外推方法包括：移动平均、线性外推、加权平均等
NON_CONTINUOUS_COLUMNS = [
    "polity",                    # 整数变量，取值范围-10到10，离散变化
    "government",                # 整数变量，取值范围0到3，离散变化
    "congress",                  # .5或整数，取值范围1到7，离散变化
    "ucdp_neighbor_confilctnumber", # 正整数变量，取值范围0到正无穷，离散变化
    "population_size",           # 0到1之间的值，虽然连续但变化缓慢
    "ethnic_diversity",          # 0到1之间的值，通常变化不大
    "national_capacity",        # 0到1之间的值，通常变化缓慢
]

# ----------------------------------------------------------------------------
# 变量取值范围约束
# ----------------------------------------------------------------------------

# 每个变量的取值范围约束
# 格式：变量名 -> (最小值, 最大值)，None表示无限制
# 这些约束用于预测时确保预测值在合理范围内
# 例如：polity变量虽然预测出-10.2，但根据约束会被限制为-10
VALUE_BOUNDS = {
    "polity": (-10.0, 10.0),                           # 政体得分：-10到10（整数）
    "GDP_per_capita_ln": (0.0, None),                   # 人均GDP对数：大于0（无上限）
    "GDP_growth": (None, None),                         # GDP增长率：无限制（可以是负数）
    "population_size": (0.0, 1.0),                     # 人口占比：0到1（百分比）
    "trade": (0.0, None),                              # 贸易占比：大于0（无上限）
    "ethnic_diversity": (0.0, 1.0),                    # 种族分化：0到1（指数）
    "national_capacity": (0.0, 1.0),                   # 国家国力：0到1（指数）
    "government": (0.0, 3.0),                          # 政府吸纳度：0到3（整数）
    "congress": (1.0, 7.0),                            # 议会吸纳度：1到7（.5或整数）
    "ucdp_neighbor_confilctnumber": (0.0, None),       # 邻国冲突数：大于等于0（无上限）
}

# ----------------------------------------------------------------------------
# ARIMA模型参数组合
# ----------------------------------------------------------------------------

# ARIMA模型尝试的参数组合（p,d,q）
# p: 自回归阶数（Autoregressive order），表示使用过去p个值预测当前值
# d: 差分阶数（Differencing order），用于使序列平稳（去除趋势）
# q: 移动平均阶数（Moving Average order），表示使用过去q个误差项预测当前值
#
# 例如：ARIMA(1,1,0)表示：
# - 使用前1个值进行自回归
# - 对序列进行1阶差分（去除趋势）
# - 不使用移动平均项
ARIMA_ORDERS = [
    (0, 1, 0),  # 随机游走模型（最简单，假设下一年等于今年）
    (1, 1, 0),  # 一阶自回归差分模型（考虑近期趋势）
    (0, 1, 1),  # 一阶移动平均差分模型（考虑近期误差）
    (1, 1, 1),  # ARIMA(1,1,1)完整模型（综合考虑）
    (2, 1, 0),  # 二阶自回归差分模型（考虑更长期趋势）
    (0, 1, 2),  # 二阶移动平均差分模型（考虑更长期误差）
    (2, 1, 1),  # 复杂模型（二阶自回归+一阶移动平均）
]

# ----------------------------------------------------------------------------
# 随机森林超参数搜索空间
# ----------------------------------------------------------------------------

# 随机森林超参数搜索空间
# 这些参数会在交叉验证中尝试不同的组合，以找到最优配置
# GridSearchCV会尝试所有参数组合，选择交叉验证得分最高的组合
PARAM_GRID = {
    "smote__k_neighbors": [3, 5],           # SMOTE过采样时的近邻数
                                              # SMOTE（合成少数类过采样技术）
                                              # 通过在少数类样本之间生成新样本来平衡数据集
                                              # k_neighbors表示用于生成新样本的近邻数量
    "clf__n_estimators": [100],              # 随机森林中决策树的数量 (临时减少以加快回测速度)
                                              # 越多越稳定，但计算成本越高
                                              # 生产环境建议使用200
    "clf__max_depth": [6, 10, None],         # 决策树的最大深度
                                              # None表示不限制深度
                                              # 较小的深度可以防止过拟合
    "clf__min_samples_leaf": [1, 3],         # 叶节点所需的最小样本数
                                              # 越大越保守，可以防止过拟合
    "clf__class_weight": [None, "balanced_subsample"],  # 类别权重设置
                                              # None：不调整类别权重
                                              # "balanced_subsample"：根据每棵树的样本分布自动调整权重
}

# ----------------------------------------------------------------------------
# Expanding-Window交叉验证配置（重要）
# ----------------------------------------------------------------------------

# expanding-window交叉验证的年份划分
# 这种方法模拟真实预测场景：训练集不断扩展，验证集向前滚动
#
# 第一折：训练集1963-1974年（12年），验证集1975-1986x年（12年）
#   - 使用1963-1974年的数据训练模型
#   - 在1975-1986年的数据上验证模型性能
#   - 模拟1974年底预测1975年的场景
#
# 第二折：训练集1963-1986年（24年），验证集1987-1998年（12年）
#   - 使用1963-1986年的数据训练模型（包含第一折的验证集）
#   - 在1987-1998年的数据上验证模型性能
#   - 训练集扩展了，验证集向前滚动
#
# 第三折：训练集1963-1998年（36年），验证集1999-2010年（12年）
#   - 使用1963-1998年的数据训练模型（包含前两折的验证集）
#   - 在1999-2010年的数据上验证模型性能
#   - 训练集继续扩展，验证集继续向前滚动
#
# 这种方法的优点：
# 1. 模拟真实预测场景（使用所有历史数据预测未来）
# 2. 充分利用数据（验证集数据也用于后续训练）
# 3. 评估模型在不同时间段的稳定性
CV_SPLITS = [
    # (训练集开始年份, 训练集结束年份, 验证集开始年份, 验证集结束年份)
    (1963, 1974, 1975, 1986),  # 第一折：训练12年，验证12年
    (1963, 1986, 1987, 1998),  # 第二折：训练24年，验证12年
    (1963, 1998, 1999, 2010),  # 第三折：训练36年，验证12年
]


# ============================================================================
# 第二部分：数据类定义（用于配置管理）
# ============================================================================

@dataclass(frozen=True)
class RunConfig:
    """
    运行配置数据类

    使用Python的dataclass装饰器创建数据类，简化类的创建
    frozen=True表示创建后不可修改（不可变对象）

    属性说明：
    - data_path: 数据文件路径（Excel格式）
    - train_cutoff: 训练集截止年份（之前的年份用于训练，从该年份开始用于验证）
    - observed_last_year: 观测数据最后一年（已知的真实数据）
    - forecast_year: 预测年份（第一个预测年）
    - recursive_year: 递推预测年份（基于第一个预测年的结果再预测）
    - max_dv_lag: 因变量的最大滞后期数（使用过去几年的冲突水平作为特征）
    - max_iv_lag: 自变量的最大滞后期数（使用过去几年的自变量作为特征）
    - n_splits: 交叉验证折数（固定为3折）
    - random_state: 随机种子（用于结果复现，确保每次运行结果一致）
    - output_prefix: 输出文件前缀（所有输出文件的前缀名）
    """
    data_path: Path  # 数据文件路径
    train_cutoff: int = 2011  # 训练集截止年份：1961-2010年用于训练
    observed_last_year: int = 2024  # 观测数据最后一年：1961-2024年的真实数据
    forecast_year: int = 2025  # 预测2025年（第一个预测年）
    recursive_year: int = 2026  # 递推预测2026年（基于2025年预测结果）
    max_dv_lag: int = 2  # 因变量最大滞后期数：使用过去2年的冲突水平
    max_iv_lag: int = 1  # 自变量最大滞后期数：使用过去1年的自变量
    n_splits: int = 3  # 交叉验证折数：固定为3折
    random_state: int = 42  # 随机种子：固定值确保结果可复现
    output_prefix: str = "domestic_clean"  # 输出文件前缀


@dataclass(frozen=True)
class FeatureSpec:
    """
    特征规范数据类

    用于指定使用哪些滞后特征进行建模

    属性说明：
    - dv_lag: 因变量的滞后期数（使用过去dv_lag年的冲突水平）
    - iv_lag: 自变量的滞后期数（使用过去iv_lag年的自变量）
    - numeric_cols: 数值型特征列名列表（所有数值型特征）
    - feature_cols: 所有特征列名列表（包括数值型和分类型）
    """
    dv_lag: int  # 因变量滞后期数
    iv_lag: int  # 自变量滞后期数
    numeric_cols: list[str]  # 数值型特征列名列表
    feature_cols: list[str]  # 所有特征列名列表


@dataclass(frozen=True)
class SearchResult:
    """
    模型搜索结果数据类

    用于存储模型选择和超参数调优的结果

    属性说明：
    - spec: 选定的特征规范（最佳的滞后特征配置）
    - best_params: 最优超参数组合（GridSearchCV找到的最佳参数）
    - best_score: 最优的交叉验证得分（宏观F1得分）
    """
    spec: FeatureSpec  # 选定的特征规范
    best_params: dict[str, Any]  # 最优超参数组合
    best_score: float  # 最优的交叉验证得分


# ============================================================================
# 第三部分：辅助函数定义
# ============================================================================

def parse_args() -> RunConfig:
    """
    解析命令行参数并返回运行配置

    功能说明：
    - 从命令行读取用户指定的参数
    - 如果用户没有指定，使用RunConfig中的默认值
    - 返回一个RunConfig对象，包含所有配置信息

    命令行参数示例：
    python domestic_conflict_pipeline_clean.py --data-path data.xlsx --output-prefix my_results

    返回：
        RunConfig对象，包含脚本运行的所有配置
    """
    # 获取脚本所在目录
    # __file__表示当前脚本的路径
    # resolve()将相对路径转换为绝对路径
    # parent获取父目录
    script_dir = Path(__file__).resolve().parent

    # 创建命令行参数解析器
    # description参数会在帮助信息中显示
    parser = argparse.ArgumentParser(
        description="Clean domestic-conflict pipeline with leak-free CV and recursive forecast."
    )

    # 添加数据文件路径参数
    # --data-path是长选项名，-d是短选项名
    # default参数指定默认值
    # help参数是参数的描述信息
    parser.add_argument(
        "--data-path",
        default=str(script_dir / "data.xlsx"),  # 默认使用脚本目录下的data.xlsx
        help="Path to domestic conflict data file (Excel format).",
    )

    # 添加输出文件前缀参数
    parser.add_argument(
        "--output-prefix",
        default=str(script_dir / "domestic_clean"),  # 默认前缀
        help="Prefix for saved artifacts in the current directory.",
    )

    # 解析命令行参数
    # 返回的args对象包含所有解析后的参数
    args = parser.parse_args()

    # 返回配置对象
    # 将命令行参数传递给RunConfig构造函数
    return RunConfig(data_path=Path(args.data_path), output_prefix=args.output_prefix)


def clip_value(name: str, value: float) -> float:
    """
    将数值限制在合理的取值范围内

    参数说明：
        name: 变量名称（用于查找VALUE_BOUNDS中定义的取值范围约束）
        value: 需要限制的原始值

    返回：
        限制在合理范围内的值

    功能说明：
        - 查找VALUE_BOUNDS字典中定义的变量取值范围
        - 如果值小于最小值，则设为最小值
        - 如果值大于最大值，则设为最大值
        - 如果没有定义范围（None），则不修改该侧约束

    示例：
        clip_value("polity", -12) -> -10.0  # 小于最小值，设为最小值
        clip_value("polity", 15) -> 10.0    # 大于最大值，设为最大值
        clip_value("polity", 5) -> 5.0      # 在范围内，不修改
    """
    # 获取变量的取值范围
    # .get()方法如果键不存在，返回默认值(None, None)
    lower, upper = VALUE_BOUNDS.get(name, (None, None))

    # 如果有下限（lower不是None），确保值不小于下限
    if lower is not None:
        value = max(lower, value)

    # 如果有上限（upper不是None），确保值不大于上限
    if upper is not None:
        value = min(upper, value)

    # 返回限制后的值
    # 确保返回类型为float
    return float(value)


def clip_to_integer(name: str, value: float) -> int:
    """
    将数值限制在整数范围内并返回整数

    参数说明：
        name: 变量名称（用于查找取值范围约束）
        value: 需要限制的原始值

    返回：
        限制在合理范围内的整数值

    功能说明：
        - 首先使用clip_value函数限制范围
        - 然后四舍五入为整数
        - 适用于polity、government等整数变量

    示例：
        clip_to_integer("polity", -12.3) -> -10  # 先限制为-10，四舍五入为-10
        clip_to_integer("polity", 3.7) -> 4     # 四舍五入为4
    """
    # 先使用clip_value限制在合理范围内
    clipped = clip_value(name, value)
    # 四舍五入为整数
    # round()函数进行四舍五入
    # int()将结果转换为整数类型
    return int(round(clipped))


def clip_to_half_integer(name: str, value: float) -> float:
    """
    将数值限制在0.5步长的范围内（适用于congress变量）

    参数说明：
        name: 变量名称（用于查找取值范围约束）
        value: 需要限制的原始值

    返回：
        限制在合理范围内的0.5倍数值

    功能说明：
        - 首先使用clip_value函数限制范围
        - 然后四舍五入到最近的0.5倍数
        - 适用于congress变量（可能的值：1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7）

    示例：
        clip_to_half_integer("congress", 1.2) -> 1.0   # 四舍五入到最近的0.5倍数
        clip_to_half_integer("congress", 1.3) -> 1.5   # 四舍五入到最近的0.5倍数
        clip_to_half_integer("congress", 2.7) -> 2.5   # 四舍五入到最近的0.5倍数

    算法说明：
        1. 乘以2：将0.5的步长转换为1的步长
        2. round()：四舍五入到最近的整数
        3. 除以2：恢复0.5的步长
    """
    # 先限制在合理范围内
    clipped = clip_value(name, value)
    # 四舍五入到最近的0.5倍数
    # 例如：1.2 -> 2.4 -> 2 -> 1.0
    # 例如：1.3 -> 2.6 -> 3 -> 1.5
    return round(clipped * 2) / 2


def load_domestic_data(path: Path) -> pd.DataFrame:
    """
    加载国内冲突数据

    参数说明：
        path: 数据文件路径（Excel格式，.xlsx或.xls）

    返回：
        加载并预处理后的DataFrame

    功能说明：
        - 读取Excel文件
        - 检查必需的列是否存在
        - 选择需要的列（因变量+自变量）
        - 转换数据类型
        - 按国家和年份排序

    数据格式要求：
        - 必须包含列：ccode（国家代码）、year（年份）
        - 必须包含列：UCDP_Civil_conflict_0_1_2（因变量）
        - 必须包含列：polity、GDP_per_capita_ln、GDP_growth、population_size、trade、
                        ethnic_diversity、national_capacity、government、congress、
                        ucdp_neighbor_confilctnumber（10个自变量）
    """
    # 读取Excel文件
    # pd.read_excel()可以读取.xlsx和.xls格式
    # openpyxl是处理.xlsx文件的引擎
    df = pd.read_excel(path)

    # 检查必需的列是否存在
    # required是一个集合，包含所有必需的列名
    # set(df.columns)是将DataFrame的列名转换为集合
    # 两个集合相减得到缺失的列
    required = {"ccode", "year", DV_COLUMN, *IV_COLUMNS}
    missing = sorted(required - set(df.columns))
    if missing:
        # 如果有缺失的列，抛出ValueError异常
        raise ValueError(f"数据文件中缺少以下列: {missing}")

    # 选择需要的列并按指定顺序排列
    # ordered列表定义了列的顺序
    # [DV_COLUMN, *IV_COLUMNS]表示DV_COLUMN后面跟着所有IV_COLUMNS中的元素
    ordered = ["ccode", "year", DV_COLUMN, *IV_COLUMNS]
    df = df[ordered].copy()  # .copy()创建副本，避免修改原始数据

    # 转换数据类型
    df["ccode"] = df["ccode"].astype(int)  # 国家代码转为整数
    df["year"] = df["year"].astype(int)  # 年份转为整数
    # 冲突水平转为整数（填充缺失值为0）
    # fillna(0)将缺失值填充为0
    # astype(int)转换为整数类型
    df[DV_COLUMN] = df[DV_COLUMN].fillna(0).astype(int)

    # 按国家和年份排序
    # sort_values()按照指定的列排序
    # ["ccode", "year"]表示先按国家代码排序，国家代码相同时按年份排序
    # reset_index(drop=True)重置索引（丢弃旧索引）
    return df.sort_values(["ccode", "year"]).reset_index(drop=True)


def infer_classes(df: pd.DataFrame) -> list[int]:
    """
    推断因变量的类别列表

    参数说明：
        df: 数据DataFrame

    返回：
        排序后的类别列表，例如[0, 1, 2]

    功能说明：
        - 提取因变量的所有唯一值
        - 去除缺失值
        - 转换为整数
        - 排序后返回

    示例：
        如果数据中有冲突水平0、1、2，返回[0, 1, 2]
    """
    return sorted(df[DV_COLUMN].dropna().astype(int).unique().tolist())


def generate_descriptive_stats(df: pd.DataFrame, output_path: Path) -> None:
    """
    生成描述性统计并保存为Markdown文件

    参数说明：
        df: 数据DataFrame
        output_path: 输出Markdown文件路径

    功能说明：
        - 计算数据的基本信息（行数、列数、国家数、年份范围）
        - 计算缺失值数量
        - 计算数值列的描述性统计（样本量、平均值、标准差、最小值、最大值）
        - 保存为Markdown格式文件
    """
    # 数据基本信息
    total_rows = len(df)
    total_cols = len(df.columns)
    num_countries = df["ccode"].nunique()
    year_min = df["year"].min()
    year_max = df["year"].max()

    # 缺失值统计
    missing_counts = df.isnull().sum()

    # 排除不需要描述性统计的列（ccode, year, 因变量）
    # 计算自变量的描述性统计
    numeric_cols = IV_COLUMNS.copy()
    summary_stats = df[numeric_cols].describe().T[["count", "mean", "std", "min", "max"]]

    # 格式化为三位小数
    summary_stats = summary_stats.map(lambda x: f"{float(x):.3f}")

    # 列名映射为中文
    summary_stats.columns = ["样本量", "平均值", "标准差", "最小值", "最大值"]

    # 变量名中文映射
    var_name_map = {
        "polity": "政体得分",
        "GDP_per_capita_ln": "人均GDP（对数）",
        "GDP_growth": "GDP增长率",
        "population_size": "0-14岁人口占比",
        "trade": "贸易额占GDP比重",
        "ethnic_diversity": "种族分化指数",
        "national_capacity": "国家综合国力指数",
        "government": "政府吸纳度",
        "congress": "议会吸纳度",
        "ucdp_neighbor_confilctnumber": "邻国冲突数量",
    }

    # 构建Markdown内容
    md_lines = [
        "# 国内冲突预测数据描述性统计",
        "",
        "## 数据基本信息",
        "",
        f"- **总行数**: {total_rows}",
        f"- **总列数**: {total_cols}",
        f"- **国家数量**: {num_countries}",
        f"- **年份范围**: {year_min}年 - {year_max}年",
        "",
        "## 缺失值统计",
        "",
        "| 变量名 | 缺失值数量 |",
        "|---------|------------|",
    ]

    for col in df.columns:
        var_name_cn = var_name_map.get(col, col)
        md_lines.append(f"| {var_name_cn} ({col}) | {missing_counts[col]} |")

    md_lines.extend([
        "",
        "## 描述性统计（保留三位小数）",
        "",
        "| 变量名 | 样本量 | 平均值 | 标准差 | 最小值 | 最大值 |",
        "|--------|--------|--------|--------|--------|--------|",
    ])

    for var_name, row in summary_stats.iterrows():
        var_name_cn = var_name_map.get(var_name, var_name)
        md_lines.append(f"| {var_name_cn} ({var_name}) | {row['样本量']} | {row['平均值']} | {row['标准差']} | {row['最小值']} | {row['最大值']} |")

    # 因变量分布统计
    md_lines.extend([
        "",
        "## 因变量（国内冲突水平）分布",
        "",
        f"| 冲突水平 | 数量 | 比例 |",
        f"|----------|------|------|",
    ])

    dv_counts = df[DV_COLUMN].value_counts().sort_index()
    dv_total = dv_counts.sum()
    for level, count in dv_counts.items():
        ratio = count / dv_total * 100
        md_lines.append(f"| {int(level)} | {int(count)} | {ratio:.2f}% |")

    # 保存为Markdown文件
    output_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"已生成描述性统计: {output_path}")


# ============================================================================
# 第四部分：预测函数（使用ARIMA和其他方法预测未来值）
# ============================================================================

def forecast_one_step_arima(years: pd.Series, values: pd.Series) -> float:
    """
    使用ARIMA模型进行单步预测

    参数说明：
        years: 年份序列（pandas Series）
        values: 对应的数值序列（pandas Series）

    返回：
        下一年的预测值（浮点数）

    功能说明：
        - 构建时间序列数据
        - 尝试多个ARIMA(p,d,q)参数组合
        - 选择AIC（赤池信息量准则）最小的模型
        - 使用最优模型进行一步预测
        - 如果无法建模（数据太少或所有值相同），返回最后一个观测值

    ARIMA模型说明：
        ARIMA(Autoregressive Integrated Moving Average)是时间序列预测模型
        - AR（自回归）：使用过去的值预测当前值
        - I（积分）：通过差分使序列平稳
        - MA（移动平均）：使用过去的误差预测当前值

    AIC说明：
        AIC（Akaike Information Criterion）用于评估模型质量
        AIC = -2*log(似然) + 2*k
        其中k是参数数量
        AIC越小越好（在模型复杂度和拟合优度之间取得平衡）
    """
    # 构建DataFrame并删除缺失值
    # years和values必须长度相同
    frame = pd.DataFrame({"year": years, "value": values}).dropna()

    # 如果没有数据，返回NaN
    if frame.empty:
        return np.nan

    # 创建pandas时间序列对象（年度频率）
    # pd.PeriodIndex创建周期索引
    # freq="Y"表示年度频率
    series = pd.Series(
        frame["value"].to_numpy(dtype=float),
        index=pd.PeriodIndex(frame["year"].astype(int), freq="Y"),
    )

    # 如果数据点太少或所有值相同，直接返回最后一个观测值
    # len(series) < 4：数据点太少，无法拟合ARIMA
    # series.nunique() == 1：所有值相同，无法计算趋势
    if len(series) < 4 or series.nunique() == 1:
        return float(series.iloc[-1])

    # 初始化最佳AIC（越大越不好）和最佳预测值
    best_aic = np.inf  # np.inf表示正无穷
    best_value = float(series.iloc[-1])  # 默认使用最后一个观测值

    # 遍历所有ARIMA参数组合
    # ARIMA_ORDERS在全局配置中定义，包含多个(p,d,q)组合
    for order in ARIMA_ORDERS:
        try:
            # 拟合ARIMA模型
            # 使用上下文管理器捕获并忽略警告信息
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # 忽略所有警告
                # 从statsmodels导入ARIMA模型
                from statsmodels.tsa.arima.model import ARIMA
                # 拟合ARIMA模型
                # series：时间序列数据
                # order：ARIMA参数(p,d,q)
                # trend="n"：不包含趋势项（因为已经有差分）
                # enforce_stationarity=False：不强制检查平稳性
                # enforce_invertibility=False：不强制检查可逆性
                fitted = ARIMA(
                    series,
                    order=order,
                    trend="n",
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                ).fit()

            # 如果AIC不是最优（是NaN或大于当前最佳AIC），跳过
            if not np.isfinite(fitted.aic) or fitted.aic >= best_aic:
                continue

            # 进行一步预测
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # forecast(steps=1)预测未来1个值
                forecast = fitted.forecast(steps=1)

            # 更新最佳AIC和最佳预测值
            best_aic = float(fitted.aic)
            best_value = float(forecast.iloc[0])
        except Exception:
            # 如果ARIMA拟合失败，跳过该参数组合
            # 例如：数据不足、数值不稳定等
            continue

    # 返回最佳预测值
    return best_value


def forecast_simple_extrapolation(years: pd.Series, values: pd.Series,
                                   is_integer: bool = False,
                                   is_half_integer: bool = False) -> float:
    """
    使用简单外推方法进行预测（线性外推或移动平均）

    参数说明：
        years: 年份序列（pandas Series）
        values: 对应的数值序列（pandas Series）
        is_integer: 是否返回整数（用于polity、government等）
        is_half_integer: 是否返回0.5倍数（用于congress）

    返回：
        下一年的预测值

    功能说明：
        - 计算简单的线性趋势
        - 如果趋势明显，使用线性外推（最后一个值 + 趋势）
        - 如果趋势不明显，使用简单移动平均（加权平均）
        - 适用于非连续变量（离散变量、整数变量）

    预测方法说明：
        1. 线性外推：predicted = last_value + (last_value - second_last_value)
           假设趋势保持不变
        2. 移动平均：predicted = weighted average of recent values
           使用最近几个值的加权平均，越近的权重越大

    示例：
        values = [1.0, 1.2, 1.5, 1.8] -> 趋势 = 1.8 - 1.5 = 0.3 -> 预测 = 1.8 + 0.3 = 2.1
        values = [1.0, 1.1, 0.9, 1.0] -> 趋势很小 -> 使用加权平均
    """
    # 构建DataFrame并删除缺失值
    frame = pd.DataFrame({"year": years, "value": values}).dropna()

    # 如果没有数据，返回NaN
    if frame.empty:
        return np.nan

    # 如果只有一个数据点，直接返回
    if len(frame) == 1:
        return float(frame["value"].iloc[0])

    # 获取最近5年的数据（如果有的话）
    # tail(5)获取最后5行
    recent = frame.tail(5)

    # 计算线性回归斜率（简单方法）
    # 使用最近两个点的差值作为趋势
    if len(recent) >= 2:
        # 获取最近两个值
        last_value = float(recent["value"].iloc[-1])
        second_last_value = float(recent["value"].iloc[-2])
        # 计算趋势（简单斜率）
        trend = last_value - second_last_value

        # 如果趋势很小（绝对值小于0.1），使用移动平均
        if abs(trend) < 0.1:
            # 使用最近3个值的加权平均（越近的权重越大）
            # 权重：[1, 2, 3]，表示最近的值权重最大
            weights = np.array([1, 2, 3])
            if len(recent) >= 3:
                # np.average计算加权平均
                weighted_avg = np.average(recent["value"].iloc[-3:], weights=weights)
                predicted = float(weighted_avg)
            else:
                # 数据点不足3个，使用最后一个值
                predicted = last_value
        else:
            # 使用线性外推
            # 预测值 = 最后一个值 + 趋势
            predicted = last_value + trend
    else:
        # 数据点太少，使用最后一个值
        predicted = float(recent["value"].iloc[-1])

    # 应用整数约束
    if is_half_integer:
        # 适用于congress变量
        # 使用clip_to_half_integer限制为0.5的倍数
        predicted = clip_to_half_integer("congress", predicted)
    elif is_integer:
        # 适用于polity、government等变量
        # 使用clip_to_integer限制为整数
        predicted = clip_to_integer("polity" if is_integer else "government", predicted)

    return predicted


def forecast_integer_count(years: pd.Series, values: pd.Series) -> int:
    """
    预测整数计数变量（如邻国冲突数）

    参数说明：
        years: 年份序列（pandas Series）
        values: 对应的数值序列（pandas Series）

    返回：
        下一年的预测整数值

    功能说明：
        - 计算最近几年的平均值
        - 四舍五入为整数
        - 确保不小于0

    预测方法说明：
        使用简单的移动平均方法，然后四舍五入
        适用于计数变量（如邻国冲突数）

    示例：
        最近5年邻国冲突数：[2, 3, 1, 2, 3] -> 平均 = 2.2 -> 预测 = 2
    """
    frame = pd.DataFrame({"year": years, "value": values}).dropna()

    if frame.empty:
        return 0

    # 使用最近5年的数据计算平均值
    recent = frame.tail(5)
    # mean()计算平均值
    avg_value = float(recent["value"].mean())

    # 四舍五入为整数
    predicted = int(round(avg_value))

    # 确保不小于0（计数不能为负）
    predicted = max(0, predicted)

    return predicted


def append_forecast_year(df: pd.DataFrame, target_year: int) -> pd.DataFrame:
    """
    为所有国家添加预测年份的数据行

    参数说明：
        df: 原始DataFrame（包含历史数据）
        target_year: 需要预测的年份

    返回：
        添加了预测年份数据的新DataFrame

    功能说明：
        - 为每个国家创建一个target_year的数据行
        - 对每个自变量进行预测
        - 因变量设为NaN（需要后续预测）

    预测逻辑：
        1. 遍历所有国家
        2. 对每个国家的每个自变量进行预测
        3. 连续变量（GDP、贸易等）使用ARIMA
        4. 整数变量（polity、government等）使用简单外推
        5. 计数变量（邻国冲突数）使用移动平均
        6. 将预测结果作为新数据行添加到DataFrame

    示例：
        原始数据包含1961-2024年的数据
        调用append_forecast_year(df, 2025)
        返回包含1961-2025年数据的DataFrame
        其中2025年的自变量是预测的，因变量是NaN
    """
    rows: list[dict[str, Any]] = []

    # 按国家分组处理
    # groupby("ccode")按国家代码分组
    # sort=True确保按国家代码排序
    for ccode, group in df.groupby("ccode", sort=True):
        # 创建预测行的基础结构
        row = {
            "ccode": ccode,  # 国家代码
            "year": target_year,  # 目标年份
            DV_COLUMN: np.nan,  # 因变量设为NaN，需要后续预测
        }

        # ------------------------------------------------------------------------
        # 预测连续变量（使用ARIMA）
        # ------------------------------------------------------------------------

        for column in ARIMA_COLUMNS:
            # 使用ARIMA预测连续变量
            # forecast_one_step_arima函数使用ARIMA模型预测
            value = forecast_one_step_arima(group["year"], group[column])
            # 使用clip_value限制在合理范围内
            row[column] = clip_value(column, value)

        # ------------------------------------------------------------------------
        # 预测整数变量（使用简单外推）
        # ------------------------------------------------------------------------

        # 预测polity（整数，-10到10）
        # is_integer=True表示返回整数
        row["polity"] = clip_to_integer("polity",
            forecast_simple_extrapolation(group["year"], group["polity"], is_integer=True))

        # 预测government（整数，0到3）
        row["government"] = clip_to_integer("government",
            forecast_simple_extrapolation(group["year"], group["government"], is_integer=True))

        # 预测congress（0.5倍数，1到7）
        # is_half_integer=True表示返回0.5的倍数
        row["congress"] = clip_to_half_integer("congress",
            forecast_simple_extrapolation(group["year"], group["congress"], is_half_integer=True))

        # ------------------------------------------------------------------------
        # 预测计数变量（使用移动平均）
        # ------------------------------------------------------------------------

        # 预测邻国冲突数（非负整数）
        row["ucdp_neighbor_confilctnumber"] = forecast_integer_count(
            group["year"], group["ucdp_neighbor_confilctnumber"])

        # ------------------------------------------------------------------------
        # 预测百分比/指数变量（使用简单外推）
        # ------------------------------------------------------------------------

        # 预测population_size（0到1）
        row["population_size"] = clip_value("population_size",
            forecast_simple_extrapolation(group["year"], group["population_size"]))

        # 预测ethnic_diversity（0到1）
        row["ethnic_diversity"] = clip_value("ethnic_diversity",
            forecast_simple_extrapolation(group["year"], group["ethnic_diversity"]))

        # 预测national_capacity（（0到1）
        row["national_capacity"] = clip_value("national_capacity",
            forecast_simple_extrapolation(group["year"], group["national_capacity"]))

        # 添加到结果列表
        rows.append(row)

    # 创建预测DataFrame
    forecast_df = pd.DataFrame(rows)

    # 合并原始数据和预测数据
    # ignore_index=True重新生成索引
    combined = pd.concat([df, forecast_df], ignore_index=True)

    # 按国家和年份排序
    return combined.sort_values(["ccode", "year"]).reset_index(drop=True)


def build_country_code_map(df: pd.DataFrame) -> dict[int, int]:
    """
    构建国家代码映射

    参数说明：
        df: 数据DataFrame

    返回：
        字典：原始国家代码 -> 映射后的整数代码

    功能说明：
        - 将原始的国家代码映射为连续的整数
        - 用于机器学习模型的输入
        - 例如：原始代码[2, 155, 255] -> 映射后[0, 1, 2]

    映射原因：
        1. 机器学习模型通常需要连续的整数作为输入
        2. 原始的国家代码可能不连续（如2, 155, 255）
        3. 映射后可以使用one-hot编码

    示例：
        原始国家代码：[2, 155, 255, 740]
        映射后：{2: 0, 155: 1, 255: 2, 740: 3}
    """
    # 获取所有唯一的国家代码并排序
    countries = sorted(df["ccode"].unique().tolist())
    # 创建映射字典：原始代码 -> 索引（从0开始）
    return {country: idx for idx, country in enumerate(countries)}


# ============================================================================
# 第五部分：特征工程函数（创建滞后特征）
# ============================================================================

def add_lag_features(df: pd.DataFrame, max_dv_lag: int, max_iv_lag: int) -> pd.DataFrame:
    """
    添加滞后特征

    参数说明：
        df: 原始DataFrame
        max_dv_lag: 因变量的最大滞后期数
        max_iv_lag: 自变量的最大滞后期数

    返回：
        添加了滞后特征的新DataFrame

    功能说明：
        - 为因变量添加滞后特征（如dv_lag1表示去年冲突水平，dv_lag2表示前年冲突水平）
        - 为每个自变量添加滞后特征
        - 滞后特征按国家分组计算（每个国家单独计算滞后）

    滞后特征说明：
        滞后特征（Lag feature）是使用过去时期的值作为当前时期的特征
        例如：
        - 2023年的dv_lag1 = 2022年的冲突水平
        - 2023年的polity_lag1 = 2022年的polity值
        - 2023年的dv_lag2 = 2021年的冲突水平

    为什么使用滞后特征：
        1. 捕捉时间依赖性（过去的冲突水平影响未来的冲突）
        2. 模拟真实预测场景（预测时只能使用过去的数据）
        3. 防止数据泄露（不使用未来的数据预测过去）

    示例：
        原始数据：
        国家  年份  冲突水平
        2     2020   0
        2     2021   1
        2     2022   2

        添加滞后特征后：
        国家  年份  冲突水平  dv_lag1  dv_lag2
        2     2020   0        NaN      NaN
        2     2021   1        0        NaN
        2     2022   2        1        0
    """
    lagged = df.copy()

    # 添加因变量的滞后特征
    # range(1, max_dv_lag + 1)生成1到max_dv_lag的序列
    for lag in range(1, max_dv_lag + 1):
        # groupby("ccode")按国家分组
        # shift(lag)向下移动lag个位置（创建滞后）
        lagged[f"dv_lag{lag}"] = lagged.groupby("ccode")[DV_COLUMN].shift(lag)

    # 添加自变量的滞后特征
    for lag in range(1, max_iv_lag + 1):
        for column in IV_COLUMNS:
            # 对每个自变量添加滞后特征
            lagged[f"{column}_lag{lag}"] = lagged.groupby("ccode")[column].shift(lag)

    return lagged


def build_feature_specs(max_dv_lag: int, max_iv_lag: int) -> list[FeatureSpec]:
    """
    构建所有可能的特征规范组合

    参数说明：
        max_dv_lag: 因变量的最大滞后期数
        max_iv_lag: 自变量的最大滞后期数

    返回：
        所有可能的FeatureSpec列表

    功能说明：
        - 遍历所有可能的因变量滞后和自变量滞后组合
        - 为每个组合创建一个FeatureSpec对象
        - 用于后续的模型选择（尝试不同的滞后配置）

    特征规范说明：
        特征规范指定使用哪些滞后特征进行建模
        例如：
        - dv_lag=2, iv_lag1: 使用过去2年的冲突水平 + 过去1年的所有自变量
        - dv_lag=1, iv_lag2: 使用过去1年的冲突水平 + 过去2年的所有自变量

    模型选择说明：
        我们会尝试不同的特征规范组合，选择验证集得分最高的组合
        这是在特征工程层面的超参数调优

    示例：
        max_dv_lag=2, max_iv_lag=1
        生成的特征规范：
        1. dv_lag=1, iv_lag=1: 使用dv_lag1 + 所有iv_lag1
        2. dv_lag=2, iv_lag=1: 使用dv_lag1+dv_lag2 + 所有iv_lag1
    """
    specs: list[FeatureSpec] = []

    # 遍历所有可能的因变量滞后和自变量滞后组合
    for dv_lag in range(1, max_dv_lag + 1):
        for iv_lag in range(1, max_iv_lag + 1):
            # 构建数值型特征列名列表
            numeric_cols = [
                # 所有自变量的滞后特征
                # f"{column}_lag{lag}"生成如"polity_lag1"的字符串
                *(f"{column}_lag{lag}" for column in IV_COLUMNS for lag in range(1, iv_lag + 1)),
                # 因变量的滞后特征
                *(f"dv_lag{lag}" for lag in range(1, dv_lag + 1)),
            ]

            # 创建特征规范对象
            specs.append(
                FeatureSpec(
                    dv_lag=dv_lag,
                    iv_lag=iv_lag,
                    numeric_cols=list(numeric_cols),
                    feature_cols=[*numeric_cols, "country_code"],
                )
            )

    return specs


def build_lagged_frame(df: pd.DataFrame, country_codes: dict[int, int], config: RunConfig) -> pd.DataFrame:
    """
    构建包含滞后特征的DataFrame

    参数说明：
        df: 原始DataFrame
        country_codes: 国家代码映射
        config: 运行配置

    返回：
        包含滞后特征的DataFrame

    功能说明：
        - 添加滞后特征
        - 映射国家代码（原始代码 -> 映射后的整数代码）
        - 按年份和国家排序

    处理流程：
        1. 使用add_lag_features添加滞后特征
        2. 将原始国家代码映射为整数代码
        3. 按年份和国家排序（确保时间顺序正确）
    """
    # 添加滞后特征
    lagged = add_lag_features(df, config.max_dv_lag, config.max_iv_lag)

    # 映射国家代码
    # map()函数根据映射字典转换值
    lagged["country_code"] = lagged["ccode"].map(country_codes).astype(int)

    # 按年份和国家排序
    return lagged.sort_values(["year", "ccode"]).reset_index(drop=True)


def build_observed_frame_for_spec(
    lagged_df: pd.DataFrame,
    spec: FeatureSpec,
    last_year: int,
) -> pd.DataFrame:
    """
    根据特征规范构建观测DataFrame

    参数说明：
        lagged_df: 包含滞后特征的DataFrame
        spec: 特征规范（指定使用哪些滞后特征）
        last_year: 包含的最后一个年份

    返回：
        筛选后的DataFrame

    功能说明：
        - 只保留last_year及之前的数据
        - 删除因变量或特征有缺失值的行
        - 按年份和国家排序

    数据清理说明：
        1. 删除未来数据（last_year之后的数据）
        2. 删除有缺失值的行（滞后特征可能有缺失值）
        3. 确保因变量是整数类型

    示例：
        lagged_df包含1961-2025年的数据
        last_year=2020
        返回只包含1961-2020年数据的DataFrame
    """
    # 只保留last_year及之前的数据
    frame = lagged_df[lagged_df["year"] <= last_year].copy()

    # 删除因变量或特征有缺失值的行
    # dropna(subset=...)只删除指定列有缺失值的行
    frame = frame.dropna(subset=[DV_COLUMN, *spec.feature_cols]).copy()

    # 确保因变量是整数类型
    frame[DV_COLUMN] = frame[DV_COLUMN].astype(int)

    # 按年份和国家排序
    return frame.sort_values(["year", "ccode"]).reset_index(drop=True)


def to_builtin(value: Any) -> Any:
    """
    将numpy类型转换为Python内置类型

    参数说明：
        value: 任意值

    返回：
        转换后的值

    功能说明：
        - 递归地将numpy类型转换为Python内置类型
        - 用于JSON序列化（numpy类型不能直接序列化为JSON）

    转换规则：
        - 字典：递归转换每个值
        - 列表/元组：递归转换每个元素
        - numpy整数/浮点数：转换为Python整数/浮点数
        - 其他类型：保持不变

    示例：
        to_builtin(np.int32(5)) -> 5 (Python int)
        to_builtin(np.float64(3.14)) -> 3.14 (Python float)
        to_builtin({"a": np.int32(1), "b": np.float64(2.0)}) -> {"a": 1, "b": 2.0}
    """
    if isinstance(value, dict):
        return {str(key): to_builtin(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_builtin(item) for item in value]
    if isinstance(value, tuple):
        return [to_builtin(item) for item in value]
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    return value


def custom_cv_splits(df: pd.DataFrame, cv_config: list) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    生成自定义的expanding-window交叉验证划分

    参数说明：
        df: 数据DataFrame
        cv_config:：交叉验证配置列表，每个元素是(训练开始, 训练结束, 验证开始, 验证结束)

    返回：
        交叉验证划分列表，每个元素是(训练集索引, 验证集索引)

    功能说明：
        - 根据CV_SPLITS配置生成交叉验证划分
        - 第一折：训练集1963-1974年，验证集1975-1986年
        - 第二折：训练集1963-1986年，验证集1987-1998年
        - 第三折：训练集1963-1998年，验证集1999-2010年

    Expanding-Window交叉验证说明：
        也称为时间序列交叉验证，特点是：
        1. 训练集不断扩大（expanding window）
        2. 验证集向前滚动
        3. 模拟真实预测场景（使用历史数据预测未来）
        4. 防止数据泄露（验证集数据不在训练集中）

    与K折交叉验证的区别：
        - K折交叉验证：验证集是随机抽取的，可能使用未来数据
        - Expanding-window：验证集是时间顺序的，只使用历史数据

    返回格式：
        [(train_indices_fold1, valid_indices_fold1),
         (train_indices_fold2, valid_indices_fold2),
         (train_indices_fold3, valid_indices_fold3)]
    """
    splits: list[tuple[np.ndarray, np.ndarray]] = []

    for train_start, train_end, valid_start, valid_end in cv_config:
        # 获取训练集的年份范围
        # range(train_start, train_end + 1)生成[train_start, train_end]的列表
        train_years = list(range(train_start, train_end + 1))

        # 获取验证集的年份范围
        valid_years = list(range(valid_start, valid_end + 1))

        # 获取训练集的索引
        # df.index获取索引
        # isin()检查是否在指定列表中
        # to_numpy()转换为numpy数组
        train_idx = df.index[df["year"].isin(train_years)].to_numpy()

        # 获取验证集的索引
        valid_idx = df.index[df["year"].isin(valid_years)].to_numpy()

        # 添加到划分列表
        splits.append((train_idx, valid_idx))

    return splits


# ============================================================================
# 第六部分：模型构建函数
# ============================================================================

def build_pipeline(numeric_cols: list[str], random_state: int) -> Pipeline:
    """
    构建机器学习管道

    参数说明：
        numeric_cols: 数值型特征列名列表
        random_state: 随机种子

    返回：
        完整的机器学习管道（Pipeline对象）

    功能说明：
        构建一个完整的机器学习管道，包含以下步骤：

        管道步骤：
        1. pre_smote（预处理）：标准化数值特征
        2. smote（SMOTE过采样）：处理类别不平衡
        3. post_smote（后处理）：one-hot编码国家代码
        4. clf（分类器）：随机森林分类器

    为什么要使用Pipeline：
        1. 避免数据泄露（预处理在训练集上，然后应用到验证集）
        2. 简化代码（多个步骤封装在一个对象中）
        3. 方便超参数调优（可以调整管道中的任何参数）

    管道处理流程：
        输入数据 -> 标准化 -> SMOTE过采样 -> one-hot编码 -> 随机森林 -> 预测结果

    详细说明：
        1. 标准化：将数值特征缩放到标准正态分布（均值0，标准差1）
        2. SMOTE：对少数类进行过采样，平衡类别分布
        3. One-hot编码：将国家代码转换为二进制向量（每个国家一个特征）
        4. 随机森林：集成多个决策树，进行分类预测
    """
    # 第一步预处理：标准化数值特征，国家代码直接传递
    # ColumnTransformer允许对不同列应用不同的转换
    pre_smote = ColumnTransformer(
        [
            # ("名称", 转换器, 列名)的格式
            ("num", StandardScaler(), numeric_cols),  # 标准化数值特征
            # StandardScaler：均值归一化（(x - mean) / std）
            ("country", "passthrough", ["country_code"]),  # 国家代码直接传递（不转换）
        ],
        verbose_feature_names_out=False,  # 不在特征转换名称中添加前缀
    )

    # SMOTE之后：one-hot编码国家代码
    # SMOTE只处理数值特征，所以需要单独对国家代码进行one-hot编码
    post_smote = ColumnTransformer(
        [
            # 数值特征直接传递（SMOTE之后）
            ("num", "passthrough", list(range(len(numeric_cols)))),
            # list(range(len(numeric_cols)))生成[0, 1, 2, ..., len(numeric_cols)-1]
            # 这些是SMOTE输出中数值特征的位置索引

            # 对国家代码进行one-hot编码
            ("country", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
             [len(numeric_cols)]),  # len(numeric_cols)是国家代码在SMOTE输出中的位置
            # handle_unknown="ignore"：忽略未知类别（新国家）
            # sparse_output=False：返回稠密矩阵而非稀疏矩阵
        ],
        verbose_feature_names_out=False,
    )

    # 构建完整的管道
    # Pipeline将多个步骤串联起来
    return Pipeline(
        steps=[
            ("pre_smote", pre_smote),  # 预处理：标准化
            (
                "smote",
                SMOTENC(categorical_features=[len(numeric_cols)],
                       random_state=random_state),  # SMOTE过采样
                # categorical_features指定哪些特征是分类特征（国家代码）
            ),
            ("post_smote", post_smote),  # 后处理：one-hot编码
            ("clf", RandomForestClassifier(random_state=random_state, n_jobs=-1)),  # 随机森林
            # n_jobs=-1：使用所有CPU核心进行并行计算
        ]
    )


def search_best_model(lagged_df: pd.DataFrame, specs: list[FeatureSpec],
                    config: RunConfig) -> SearchResult:
    """
    搜索最佳模型

    参数说明：
        lagged_df: 包含滞后特征的DataFrame
        specs: 所有可能的特征规范列表
        config: 运行配置

    返回：
        最佳搜索结果（SearchResult对象）

    功能说明：
        - 遍历所有可能的特征规范
        - 对每个规范使用网格搜索寻找最优超参数
        - 使用宏观F1得分作为评估指标
        - 返回得分最高的模型配置

    模型选择流程：
        1. 遍历所有特征规范组合
        2. 对每个特征规范：
           a. 构建训练数据
           b. 创建GridSearchCV对象
           c. 在交叉验证上评估模型
           d. 记录最佳得分和参数
        3. 选择所有特征规范中得分最高的配置

    宏观F1得分说明：
        F1得分 = 2 * (精确度 * 召回率) / (精确度 + 召回率)
        宏观F1：先计算每个类别的F1得分，然后取平均
        宏观F1适合类别不平衡的情况，因为每个类别权重相同

    网格搜索说明：
        GridSearchCV会尝试PARAM_GRID中所有参数组合
        对于每种组合，在交叉验证上评估模型
        选择验证集得分最高的组合
    """
    # 使用宏观F1得分作为评估指标
    # make_scorer将评分函数转换为scorer对象
    # f1_score：F1得分
    # average="macro"：宏观平均
    scorer = make_scorer(f1_score, average="macro")
    best_result: SearchResult | None = None

    # 遍历所有特征规范
    for spec in specs:
        # 构建观测DataFrame
        # 只包含因变量和特征都有值的行
        observed_df = build_observed_frame_for_spec(lagged_df, spec, config.observed_last_year)

        # 只使用训练截止年份之前的数据进行模型选择
        # 防止数据泄露（验证集数据不参与模型选择）
        train_df = observed_df[observed_df["year"] < config.train_cutoff].reset_index(drop=True)

        # 如果训练集为空或年份太少，跳过
        if train_df.empty or train_df["year"].nunique() <= config.n_splits:
            continue

        # 使用自定义的expanding-window交叉验证
        cv = custom_cv_splits(train_df, CV_SPLITS)

        # 创建网格搜索对象
        search = GridSearchCV(
            estimator=build_pipeline(spec.numeric_cols, config.random_state),  # 估计器（模型管道）
            param_grid=PARAM_GRID,  # 超参数搜索空间
            scoring=scorer,  # 评估指标：宏观F1得分
            cv=cv,  # 交叉验证划分
            n_jobs=-1,  # 使用所有CPU核心进行并行计算
            refit=True,  # 在整个数据上重新拟合最优模型
        )

        # 拟合网格搜索
        # search.fit()会尝试所有参数组合，选择最好的
        search.fit(train_df[spec.feature_cols], train_df[DV_COLUMN])

        # 保存结果
        result = SearchResult(
            spec=spec,
            best_params=search.best_params_,  # 最优参数
            best_score=float(search.best_score_),  # 最优得分
        )

        # 如果这是第一个结果，或者得分更高，更新最佳结果
        if best_result is None or result.best_score > best_result.best_score:
            best_result = result

    # 如果没有找到任何结果，报错
    if best_result is None:
        raise RuntimeError("网格搜索没有产生任何结果。")

    return best_result


def fit_pipeline(df: pd.DataFrame, spec: FeatureSpec,
                params: dict[str, Any], config: RunConfig) -> Pipeline:
    """
    使用指定参数拟合管道

    参数说明：
        df: 训练数据DataFrame
        spec: 特征规范
        params: 超参数字典
        config: 运行配置

    返回：
        拟合好的管道（Pipeline对象）

    功能说明：
        - 创建管道
        - 设置超参数
        - 拟合模型

    拟合流程：
        1. 创建管道对象
        2. 使用set_params设置超参数
        3. 使用fit训练模型

    为什么需要单独的fit函数：
        - search_best_model中已经找到最优参数
        - 但我们需要在完整数据上重新拟合模型
        - 这个函数用于在任意数据上拟合模型
    """
    # 创建管道
    model = build_pipeline(spec.numeric_cols, config.random_state)

    # 设置超参数
    # set_params(**params)将字典中的键值对设置为管道参数
    model.set_params(**params)

    # 拟合模型
    # fit(X, y)：X是特征矩阵，y是目标变量
    model.fit(df[spec.feature_cols], df[DV_COLUMN])

    return model


def probability_frame(model: Pipeline, features: pd.DataFrame,
                      classes: list[int]) -> pd.DataFrame:
    """
    获取预测概率DataFrame

    参数说明：
        model: 拟合好的模型
        features: 特征DataFrame
        classes: 所有类别列表

    返回：
        包含各类别预测概率的DataFrame

    功能说明：
        - 使用predict_proba获取预测概率
        - 对齐类别顺序
        - 返回格式化的DataFrame

    预测概率说明：
        predict_proba返回每个类别的概率
        例如：对于三分类[0, 1, 2]
        返回：[[P(class=0), P(class=1), P(class=2)], ...]

    对齐类别说明：
        模型的类别顺序可能与classes参数不一致
        需要重新对齐，确保输出顺序与classes参数一致

    返回格式：
        DataFrame包含列：prob_0, prob_1, prob_2
        每行表示一个样本，值表示属于该类别的概率
    """
    # 获取预测概率
    proba = model.predict_proba(features)

    # 创建结果DataFrame
    frame = pd.DataFrame(index=features.index)

    # 初始化所有类别的概率为0
    for cls in classes:
        frame[f"prob_{cls}"] = 0.0

    # 填充实际概率
    # model.named_steps["clf"].classes_获取模型的类别顺序
    for idx, cls in enumerate(model.named_steps["clf"].classes_):
        frame[f"prob_{int(cls)}"] = proba[:, idx]

    # 按类别顺序返回
    return frame[[f"prob_{cls}" for cls in classes]]


def aligned_probabilities(model: Pipeline, features: pd.DataFrame,
                          classes: list[int]) -> np.ndarray:
    """
    获取对齐的预测概率数组

    参数说明：
        model: 拟合好的模型
        features: 特征DataFrame
        classes: 所有类别列表

    返回：
        对齐的预测概率数组（numpy数组）

    功能说明：
        - 确保概率数组的列顺序与classes参数一致
        - 用于后续的ROC曲线计算

    对齐说明：
        模型的类别顺序可能与classes参数不一致
        需要创建一个映射，将模型的类别顺序映射到classes顺序

    返回格式：
        numpy数组，形状为(n_samples, n_classes)
        每行表示一个样本，每列表示一个类别的概率

    与probability_frame的区别：
        - probability_frame返回DataFrame，方便查看
        - aligned_probabilities返回numpy数组，方便计算
    """
    # 获取预测概率
    proba = model.predict_proba(features)

    # 创建类别到位置的映射
    # 例如：classes=[0, 1, 2] -> class_to_pos={0: 0, 1: 1, 2: 2}
    class_to_pos = {cls: idx for idx, cls in enumerate(classes)}

    # 创建对齐的数组
    # zeros((n_samples, n_classes))创建全零数组
    aligned = np.zeros((len(features), len(classes)), dtype=float)

    # 填充对齐的值
    for idx, cls in enumerate(model.named_steps["clf"].classes_):
        aligned[:, class_to_pos[int(cls)]] = proba[:, idx]

    return aligned


# ============================================================================
# 第七部分：评估函数（计算模型性能指标）
# ============================================================================

def build_roc_payload(y_true: pd.Series, y_score: np.ndarray,
                     classes: list[int]) -> dict[str, Any]:
    """
    构建ROC曲线数据

    参数说明：
        y_true: 真实类别（pandas Series）
        y_score: 预测概率（numpy数组）
        classes: 所有类别列表

    返回：
        包含ROC曲线数据的字典

    功能说明：
        - 计算每个类别的ROC曲线
        - 计算微平均和宏平均ROC曲线
        - 计算AUC值（曲线下面积）

    ROC曲线说明：
        ROC（Receiver Operating Characteristic）曲线用于评估分类器性能
        - 横轴：假正例率（False Positive Rate, FPR）
        - 纵轴：真正例率（True Positive Rate, TPR）
        - 对角线：随机分类器
        - 左上角：完美分类器

    AUC说明：
        AUC（Area Under Curve）是ROC曲线下的面积
        - AUC=1：完美分类器
        - AUC=0.5：随机分类器
        - AUC越大，分类器性能越好

    微平均vs宏平均：
        - 微平均：所有样本和所有类别一起计算
        - 宏平均：先对每个类别计算，然后平均

    返回格式：
        {
            "fpr": {类别: 假正例率列表},
            "tpr": {类别: 真正例率列表},
            "auc": {类别: AUC值}
        }
    """
    # 转换为numpy数组
    class_array = np.array(classes, dtype=int)

    # 将多类别转换为二进制格式（one-hot编码）
    # label_binarize将标签转换为二进制矩阵
    # 例如：y_true=[0, 1, 2, 0] -> [[1,0,0], [0,1,0], [0,0,1], [1,0,0]]
    y_bin = label_binarize(y_true, classes=class_array)

    # 初始化结果字典
    fpr: dict[str, list[float]] = {}  # 假正例率
    tpr: dict[str, list[float]] = {}  # 真正例率
    auc_scores: dict[str, float] = {}  # AUC值

    # 计算每个类别的ROC曲线
    for idx, class_id in enumerate(class_array):
        # roc_curve计算ROC曲线
        # y_bin[:, idx]是该类别的二进制标签
        # y_score[:, idx]是该类别的预测概率
        x_fpr, x_tpr, _ = roc_curve(y_bin[:, idx], y_score[:, idx])
        fpr[str(class_id)] = x_fpr.tolist()  # 转换为列表（便于JSON序列化）
        tpr[str(class_id)] = x_tpr.tolist()
        auc_scores[str(class_id)] = float(auc(x_fpr, x_tpr))  # 计算AUC

    # 计算微平均ROC曲线（所有样本和所有类别一起计算）
    micro_fpr, micro_tpr, _ = roc_curve(y_bin.ravel(), y_score.ravel())
    # ravel()将矩阵展平为一维数组
    fpr["micro"] = micro_fpr.tolist()
    tpr["micro"] = micro_tpr.tolist()
    auc_scores["micro"] = float(auc(micro_fpr, micro_tpr))

    # 计算宏平均ROC曲线（先对每个类别平均，再插值）
    # 先获取所有唯一的假正例率
    all_fpr = np.unique(np.concatenate([np.asarray(fpr[str(class_id)]) for class_id in class_array]))
    # 对每个假正例率，计算平均真正例率
    mean_tpr = np.zeros_like(all_fpr)
    for class_id in class_array:
        mean_tpr += np.interp(all_fpr, np.asarray(fpr[str(class_id)]),
                             np.asarray(tpr[str(class_id)]))
    mean_tpr /= len(class_array)  # 除以类别数量

    fpr["macro"] = all_fpr.tolist()
    tpr["macro"] = mean_tpr.tolist()
    auc_scores["macro"] = float(auc(all_fpr, mean_tpr))

    # 计算多类别AUC
    # 使用one-vs-rest（OVR）策略
    auc_scores["macro_ovr"] = float(roc_auc_score(y_bin, y_score,
                                                   average="macro", multi_class="ovr"))
    auc_scores["micro_ovr"] = float(roc_auc_score(y_bin, y_score,
                                                   average="micro", multi_class="ovr"))

    return {"fpr": fpr, "tpr": tpr, "auc": auc_scores}


def evaluate_model(model: Pipeline, test_df: pd.DataFrame,
                 spec: FeatureSpec, classes: list[int]) -> dict[str, Any]:
    """
    评估模型性能

    参数说明：
        model: 拟合好的模型
        test_df: 测试数据
        spec: 特征规范
        classes: 所有类别列表

    返回：
        评估指标字典

    功能说明：
        - 进行预测
        - 计算分类报告（精确度、召回率、F1得分）
        - 计算混淆矩阵
        - 计算宏观F1得分
        - 计算ROC曲线

    评估指标说明：
        1. 精确度（Precision）：预测为正例的样本中，真正为正例的比例
           Precision = TP / (TP + FP)

        2. 召回率（Recall）：真正为正例的样本中，预测为正例的比例
           Recall = TP / (TP + FN)

        3. F1得分（F1-score）：精确度和召回率的调和平均
           F1 = 2 * (Precision * Recall) / (Precision + Recall)

        4. 混淆矩阵（Confusion Matrix）：显示预测类别和真实类别的对应关系
           行：真实类别
           列：预测类别

        5. ROC曲线和AUC：评估分类器的整体性能

    返回格式：
        {
            "macro_f1": 宏观F1得分,
            "confusion_matrix": 混淆矩阵,
            "classification_report": 分类报告,
            "roc": ROC曲线数据
        }
    """
    # 获取特征和真实标签
    features = test_df[spec.feature_cols]
    y_true = test_df[DV_COLUMN].astype(int)

    # 进行预测
    # predict()返回预测的类别
    y_pred = model.predict(features).astype(int)

    # 获取预测概率
    y_score = aligned_probabilities(model, features, classes)

    # 计算分类报告
    # classification_report生成详细的分类报告
    # digits=4：保留4位小数
    # output_dict=True：返回字典而非字符串
    # zero_division=0：除零时返回0
    report = classification_report(y_true, y_pred, digits=4,
                                  output_dict=True, zero_division=0)

    # 返回所有评估指标
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),  # 转换为列表
        "classification_report": report,
        "roc": build_roc_payload(y_true, y_score, classes),
    }


def save_roc_curve(roc_payload: dict[str, Any], output_path: Path) -> None:
    """
    保存ROC曲线图

    参数说明：
        roc_payload: ROC曲线数据
        output_path: 输出文件路径

    功能说明：
        - 绘制每个类别的ROC曲线
        - 绘制微平均和宏平均ROC曲线
        - 保存为SVG格式（矢量图形，可缩放）

    图形说明：
        - 横轴：假正例率（False Positive Rate）
        - 纵轴：真正例率（True Positive Rate）
        - 对角线：随机分类器
        - 曲线越靠近左上角，分类器性能越好

    颜色方案：
        - 类别0（无冲突）：灰色
        - 类别1（低强度冲突）：橙色
        - 类别2（高强度冲突）：红色
        - 宏平均：深蓝色（虚线）
        - 微平均：青色（点线）
    """
    # 创建图形
    # figsize=(8, 6)设置图形大小为8x6英寸
    fig, ax = plt.subplots(figsize=(8, 6))

    # 定义颜色方案
    palette = {"0": "#6c757d",  # 类别0：灰色
               "1": "#f4a261",  # 类别1：橙色
               "2": "#d62828",  # 类别2：红色
               "macro": "#1d3557",  # 宏平均：深蓝色
               "micro": "#2a9d8f"}  # 微平均：青色

    # 获取数字类别的键
    # 过滤掉"macro"和"micro"，只保留数字类别
    class_keys = sorted([key for key in roc_payload["auc"] if key.isdigit()], key=int)

    # 绘制每个类别的ROC曲线
    for key in class_keys:
        ax.plot(
            roc_payload["fpr"][key],
            roc_payload["tpr"][key],
            lw=2,  # 线宽
            color=palette[key],
            label=f"类别 {key} (AUC = {roc_payload['auc'][key]:.3f})",
        )

    # 绘制宏平均ROC曲线
    ax.plot(
        roc_payload["fpr"]["macro"],
        roc_payload["tpr"]["macro"],
        lw=2.5,
        color=palette["macro"],
        linestyle="--",  # 虚线
        label=f"宏平均 (AUC = {roc_payload['auc']['macro']:.3f})",
    )

    # 绘制微平均ROC曲线
    ax.plot(
        roc_payload["fpr"]["micro"],
        roc_payload["tpr"]["micro"],
        lw=2.5,
        color=palette["micro"],
        linestyle=":",  # 点线
        label=f"微平均 (AUC = {roc_payload['auc']['micro']:.3f})",
    )

    # 绘制对角线（随机分类器）
    ax.plot([0, 1], [0, 1], color="black", lw=1, linestyle="--")

    # 设置图形属性
    ax.set_xlim(0.0, 1.0)  # x轴范围
    ax.set_ylim(0.0, 1.05)  # y轴范围（稍微留点空间）
    ax.set_xlabel("假正例率 (False Positive Rate)")  # x轴标签
    ax.set_ylabel("真正例率 (True Positive Rate)")  # y轴标签
    ax.set_title("国内冲突预测ROC曲线")  # 标题
    ax.legend(loc="lower right")  # 图例位置
    ax.grid(alpha=0.25)  # 网格线，透明度0.25

    # 保存图形
    fig.tight_layout()  # 自动调整布局
    fig.savefig(output_path, format="svg")  # 保存为SVG格式
    plt.close(fig)  # 关闭图形，释放内存


def make_target_feature_frame(
    history_df: pd.DataFrame,
    spec: FeatureSpec,
    country_codes: dict[int, int],
    target_year: int,
) -> pd.DataFrame:
    """
    构建预测年份的特征DataFrame

    参数说明：
        history_df: 历史数据DataFrame
        spec: 特征规范
        country_codes: 国家代码映射
        target_year: 目标预测年份

    返回：
        预测年份的特征DataFrame

    功能说明：
        - 为每个国家构建target_year的特征
        - 使用滞后特征（从历史数据中提取）
        - 只包含有完整特征的国家

    构建逻辑：
        1. 遍历所有国家
        2. 对于每个国家，从历史数据中提取滞后特征
        3. 例如：预测2025年，需要2024年的值（滞后1期）
        4. 如果所有滞后特征都有值，则添加到结果中
        5. 如果有缺失值，则跳过该国家

    示例：
        预测2025年，spec.dv_lag=2
        需要：
        - 2024年的冲突水平（dv_lag1）
        - 2023年的冲突水平（dv_lag2）
        - 2024年的所有自变量（iv_lag1）

    返回格式：
        DataFrame包含：
        - ccode：国家代码
        - year：目标年份
        - country_code：映射后的国家代码
        - dv_lag1, dv_lag2：因变量滞后特征
        - polity_lag1, GDP_per_capita_ln_lag1, ...：自变量滞后特征
    """
    rows: list[dict[str, Any]] = []

    # 按国家分组处理
    for ccode, group in history_df.groupby("ccode", sort=True):
        # 创建预测行的基础结构
        row = {
            "ccode": ccode,
            "year": target_year,
            "country_code": country_codes[ccode],
        }

        valid = True  # 标记该国家是否有完整特征

        # 添加因变量的滞后特征
        # 需要过去spec.dv_lag年的冲突水平
        for lag in range(1, spec.dv_lag + 1):
            # 获取target_year - lag年的数据
            year_df = group[group["year"] == target_year - lag]
            # 如果数据不存在或因变量有缺失值，标记为无效
            if year_df.empty or year_df[DV_COLUMN].isna().any():
                valid = False
                break
            # 添加滞后特征
            row[f"dv_lag{lag}"] = float(year_df[DV_COLUMN].iloc[0])

        if not valid:
            continue  # 跳过该国家

        # 添加自变量的滞后特征
        # 需要过去spec.iv_lag年的所有自变量
        for lag in range(1, spec.iv_lag + 1):
            year_df = group[group["year"] == target_year - lag]
            if year_df.empty:
                valid = False
                break
            # 对每个自变量添加滞后特征
            for column in IV_COLUMNS:
                row[f"{column}_lag{lag}"] = float(year_df[column].iloc[0])

        if valid:
            rows.append(row)

    # 创建DataFrame
    frame = pd.DataFrame(rows)
    return frame.sort_values("ccode").reset_index(drop=True)


def prediction_table(model: Pipeline, features: pd.DataFrame, year: int,
                     classes: list[int]) -> pd.DataFrame:
    """
    生成预测结果表

    参数说明：
        model: 拟合好的模型
        features: 特征DataFrame
        year: 预测年份
        classes: 所有类别列表

    返回：
        预测结果DataFrame

    功能说明：
        - 进行预测
        - 获取预测概率
        - 返回格式化的预测结果表

    预测方法说明：
        本脚本使用随机森林的直接预测结果
        不使用固定阈值或阈值放大

        随机森林的预测原理：
        1. 集成多个决策树
        2. 每棵树进行预测
        3. 通过投票（分类）或平均（回归）得到最终结果

        对于分类问题：
        - predict()返回概率最高的类别
        - predict_proba()返回每个类别的概率
        - 最终预测 = argmax(probabilities)

        为什么不使用固定阈值：
        1. 随机森林内部已经有复杂的决策机制
        2. 使用固定阈值可能破坏模型的决策逻辑
        3. 交叉验证已经优化了模型参数
        4. 直接使用模型的预测结果更可靠

    返回格式：
        DataFrame包含：
        - ccode：国家代码
        - predicted_conflict_2025：预测的冲突水平
        - prob_0：类别0的概率
        - prob_1：类别1的概率
        - prob_2：类别2的概率
    """
    # 获取预测概率
    proba = probability_frame(model, features, classes)

    # 获取特征列（排除country和year）
    model_cols = [column for column in features.columns
                  if column not in {"ccode", "year"}]

    # 进行预测
    # 使用随机森林的直接预测结果
    # 不使用固定阈值或阈值放大
    prediction = model.predict(features[model_cols]).astype(int)

    # 创建结果DataFrame
    result = pd.DataFrame(
        {
            "ccode": features["ccode"],
            f"predicted_conflict_{year}": prediction,
        }
    )

    # 合并预测结果和预测概率
    return pd.concat([result, proba.reset_index(drop=True)], axis=1)


def actual_target_frame(raw_df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    获取指定年份的真实值

    参数说明：
        raw_df: 原始数据DataFrame
        year: 年份

    返回：
        包含真实值的DataFrame

    功能说明：
        - 从原始数据中提取指定年份的真实值
        - 只保留国家代码和因变量

    返回格式：
        DataFrame包含：
        - ccode：国家代码
        - actual_intensity：真实的冲突水平
    """
    frame = raw_df[raw_df["year"] == year][["ccode", DV_COLUMN]].copy()
    # 重命名因变量列
    return frame.rename(columns={DV_COLUMN: "actual_intensity"})


def score_prediction_rows(df: pd.DataFrame, classes: list[int]) -> dict[str, Any]:
    """
    评估预测结果

    参数说明：
        df: 包含预测值和真实值的DataFrame
        classes: 所有类别列表

    返回：
        评估指标字典

    功能说明：
        - 计算分类报告
        - 计算混淆矩阵
        - 计算宏观F1得分
        - 计算ROC曲线
    """
    # 获取真实值和预测值
    y_true = df["actual_intensity"].astype(int)
    y_pred = df["predicted_intensity"].astype(int)

    # 获取预测概率
    y_score = df[[f"prob_{cls}" for cls in classes]].to_numpy(dtype=float)

    # 计算分类报告
    report = classification_report(y_true, y_pred, digits=4,
                                  output_dict=True, zero_division=0)

    # 返回所有评估指标
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": report,
        "roc": build_roc_payload(y_true, y_score, classes),
        "rows": int(len(df)),  # 预测样本数
    }


# ============================================================================
# 第八部分：结果可视化和保存函数
# ============================================================================

def format_metric_text(value: Any) -> str:
    """
    格式化指标文本

    参数说明：
        value: 指标值

    返回：
        格式化后的字符串

    功能说明：
        将数值格式化为保留3位小数的字符串

    示例：
        format_metric_text(0.123456) -> "0.123"
        format_metric_text(0.9999) -> "1.000"
    """
    return f"{float(value):.3f}"


def build_holdout_class_table(metrics: dict[str, Any],
                              classes: list[int]) -> pd.DataFrame:
    """
    构建各类别预测得分表

    参数说明：
        metrics: 评估指标字典
        classes: 所有类别列表

    返回：
        各类别得分表

    功能说明：
        - 从分类报告中提取每个类别的得分
        - 创建包含类别、精确度、召回率、F1得分的表格

    返回格式：
        DataFrame包含：
        - 类别：0、1、2
        - 精确度 (Precision)：每个类别的精确度
        - 召回率 (Recall)：每个类别的召回率
        - F1得分 (F1-score)：每个类别的F1得分
    """
    report = metrics["classification_report"]
    rows: list[dict[str, Any]] = []

    # 为每个类别创建一行
    for cls in classes:
        cls_key = str(cls)  # 转换为字符串（分类报告中的键是字符串）
        rows.append(
            {
                "类别": str(cls),
                "精确度 (Precision)": format_metric_text(report[cls_key]["precision"]),
                "召回率 (Recall)": format_metric_text(report[cls_key]["recall"]),
                "F1得分 (F1-score)": format_metric_text(report[cls_key]["f1-score"]),
            }
        )

    return pd.DataFrame(rows, dtype=object)


def build_holdout_overall_table(metrics: dict[str, Any]) -> pd.DataFrame:
    """
    构建总体得分表

    参数说明：
        metrics: 评估指标字典

    返回：
        总体得分表

    功能说明：
        - 从分类报告中提取宏平均和加权平均得分
        - 创建包含指标名称、精确度、召回率、F1得分的表格

    返回格式：
        DataFrame包含：
        - 指标：宏平均、加权平均
        - 精确度 (Precision)：相应的精确度
        - 召回率 (Recall)：相应的召回率
        - F1得分 (F1-score)：相应的F1得分
    """
    report = metrics["classification_report"]
    rows = []

    # 为宏平均和加权平均创建行
    for label, key in [("宏平均 (Macro Avg)", "macro avg"),
                       ("加权平均 (Weighted Avg)", "weighted avg")]:
        rows.append(
            {
                "指标": label,
                "精确度 (Precision)": format_metric_text(report[key]["precision"]),
                "召回率 (Recall)": format_metric_text(report[key]["recall"]),
                "F1得分 (F1-score)": format_metric_text(report[key]["f1-score"]),
            }
        )

    return pd.DataFrame(rows, dtype=object)


def build_model_selection_table(search: SearchResult) -> pd.DataFrame:
    """
    构建模型选择结果表

    参数说明：
        search: 搜索结果

    返回：
        模型选择结果表

    功能说明：
        - 提取最优模型的各种参数
        - 创建包含参数名称和数值的表格

    返回格式：
        DataFrame包含：
        - 指标：参数名称
        - 数值：参数值
    """
    params = search.best_params
    rows = [
        {"指标": "最佳因变量滞后期", "数值": str(search.spec.dv_lag)},
        {"指标": "最佳自变量滞后期", "数值": str(search.spec.iv_lag)},
        {"指标": "最佳交叉验证宏平均F1", "数值": f"{search.best_score:.3f}"},
        {"指标": "决策树数量", "数值": str(params["clf__n_estimators"])},
        {"指标": "最大树深", "数值": str(params["clf__max_depth"])},
        {"指标": "叶节点最小样本数", "数值": str(params["clf__min_samples_leaf"])},
        {"指标": "类别权重", "数值": "None" if params["clf__class_weight"] is None
         else str(params["clf__class_weight"])},
        {"指标": "SMOTENC近邻数", "数值": str(params["smote__k_neighbors"])},
    ]
    return pd.DataFrame(rows, dtype=object)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """
    将DataFrame转换为Markdown表格

    参数说明：
        df: DataFrame

    返回：
        Markdown表格字符串

    功能说明：
        - 将DataFrame转换为Markdown格式的表格
        - Markdown表格可以在文本编辑器中显示

    Markdown表格格式：
        | 列1 | 列2 | 列3 |
        |-----|-----|-----|
        | 值1 | 值2 | 值3 |
        | 值4 | 值5 | 值6 |
    """
    def format_cell(value: Any) -> str:
        # 处理缺失值
        if pd.isna(value):
            return ""
        # 处理整数
        if isinstance(value, (np.integer, int)):
            return str(int(value))
        # 处理浮点数
        if isinstance(value, (np.floating, float)):
            if float(value).is_integer():
                return str(int(value))
            return f"{float(value):.3f}"
        # 其他类型
        return str(value)

    # 获取列名
    headers = list(df.columns)

    # 创建表头
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    # 添加数据行
    for row in df.itertuples(index=False, name=None):
        values = [format_cell(value) for value in row]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def save_report_tables(prefix: Path, metrics: dict[str, Any],
                      search: SearchResult, classes: list[int]) -> None:
    """
    保存结果表格

    参数说明：
        prefix: 输出文件前缀
        metrics: 评估指标字典
        search: 搜索结果
        classes: 所有类别列表

    功能说明：
        - 保存各类别得分表为CSV
        - 保存总体得分表为CSV
        - 保存模型选择结果表为CSV
        - 保存所有表格为Markdown

    输出文件：
        1. {prefix}_holdout_class_table.csv：各类别得分表（CSV格式）
        2. {prefix}_holdout_overall_table.csv：总体得分表（CSV格式）
        3. {prefix}_model_selection_table.csv：模型选择结果表（CSV格式）
        4. {prefix}_report_tables.md：所有表格（Markdown格式）
    """
    # 构建表格
    class_table = build_holdout_class_table(metrics, classes)
    overall_table = build_holdout_overall_table(metrics)
    model_table = build_model_selection_table(search)

    # 保存为CSV（使用utf-8-sig编码以支持Excel）
    # utf-8-sig添加BOM（字节顺序标记），Excel可以正确识别UTF-8编码
    class_table.to_csv(f"{prefix}_holdout_class_table.csv",
                       index=False, encoding="utf-8-sig")
    overall_table.to_csv(f"{prefix}_holdout_overall_table.csv",
                        index=False, encoding="utf-8-sig")
    model_table.to_csv(f"{prefix}_model_selection_table.csv",
                      index=False, encoding="utf-8-sig")

    # 保存为Markdown
    markdown = "\n\n".join(
        [
            "表 1：国内冲突各类别预测得分\n" + dataframe_to_markdown(class_table),
            "表 2：国内冲突预测总体得分\n" + dataframe_to_markdown(overall_table),
            "表 3：国内冲突模型最优参数与滞后期\n" + dataframe_to_markdown(model_table),
        ]
    )
    Path(f"{prefix}_report_tables.md").write_text(markdown, encoding="utf-8")


# ============================================================================
# 第九部分：递推回测函数
# ============================================================================

def inject_predictions(df: pd.DataFrame, predictions: pd.DataFrame,
                      year: int) -> pd.DataFrame:
    """
    将预测结果注入数据集

    参数说明：
        df: 原始DataFrame
        predictions: 预测结果DataFrame
        year: 预测年份

    返回：
        注入预测结果后的DataFrame

    功能说明：
        - 将预测结果作为观测值添加到数据集中
        - 用于递推预测（使用前一年的预测结果预测下一年）

    为什么需要注入预测：
        递推预测需要使用预测年的结果作为特征
        例如：预测2026年时需要2025年的冲突水平
        但2025年的冲突水平是预测的，不是真实的
        所以需要将预测结果注入数据集

    示例：
        原始数据：1961-2024年
        预测2025年
        注入预测后的数据：1961-2025年（2025年的冲突水平是预测的）
        使用预测后的数据预测2026年
    """
    # 获取预测值列名
    value_col = f"predicted_conflict_{year}"

    # 创建国家代码到预测值的映射
    mapping = predictions.set_index("ccode")[value_col]

    # 复制原始数据
    updated = df.copy()

    # 将预测值注入对应年份的因变量
    mask = updated["year"] == year  # 找到预测年份的行
    updated.loc[mask, DV_COLUMN] = updated.loc[mask, "ccode"].map(mapping)

    # 按国家和年份排序
    return updated.sort_values(["ccode", "year"]).reset_index(drop=True)


def run_recursive_backtest(
    raw_df: pd.DataFrame,
    spec: FeatureSpec,
    params: dict[str, Any],
    country_codes: dict[int, int],
    config: RunConfig,
    classes: list[int],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    运行递推回测

    参数说明：
        raw_df: 原始数据DataFrame
        spec: 特征规范
        params: 超参数
        country_codes: 国家代码映射
        config: 运行配置
        classes: 所有类别列表

    返回：
        (回测结果DataFrame, 回测指标字典)

    功能说明：
        - 模拟真实的预测流程
        - 使用历史数据训练模型
        - 预测下一年
        - 将预测结果作为观测值
        - 递推预测下下一年
        - 计算预测准确率

    递推回测逻辑：
        1. 遍历所有可能的起始年份
        2. 对于每个起始年份：
           a. 使用历史数据训练模型
           b. 预测下一年（预测距离1年）
           c. 将预测结果注入数据集
           d. 使用预测结果预测下下一年（预测距离2年）
           e. 与真实值比较，计算准确率
        3. 汇总所有预测结果，计算总体指标

    回测年份示例：
        - origin_year=2010：
          - 训练集：1961-2010年
          - 预测2011年（预测距离1年）
          - 预测2012年（预测距离2年）
        - origin_year=2011：
          - 训练集：1961-2011年
          - 预测2012年（预测距离1年）
          - 预测2013年（预测距离2年）
        - ...
        - origin_year=2022：
          - 训练集：1961-2022年
          - 预测2023年（预测距离1年）
          - 预测2024年（预测距离2年）

    返回格式：
        (回测结果DataFrame, {总体指标, 距离1年指标, 距离2年指标})
    """
    rows: list[pd.DataFrame] = []
    total_years = config.observed_last_year - config.train_cutoff + 1

    # 遍历所有可能的起始年份
    # 从train_cutoff-1到observed_last_year-1
    # 确保有足够的数据进行2年递推预测
    for i, origin_year in enumerate(range(config.train_cutoff - 1, config.observed_last_year - 1)):
        progress = (i + 1) / total_years * 100
        print(f"递推回测进度: {i+1}/{total_years} ({progress:.1f}%) - 起始年份 {origin_year}")
        # 只使用origin_year及之前的数据
        observed_history = raw_df[raw_df["year"] <= origin_year].copy()

        # 构建滞后特征
        lagged_history = build_lagged_frame(observed_history, country_codes, config)

        # 构建训练数据
        train_frame = build_observed_frame_for_spec(lagged_history, spec, origin_year)

        # 如果训练数据太少，跳过
        if train_frame.empty or train_frame["year"].nunique() <= config.n_splits:
            continue

        # 拟合模型
        model = fit_pipeline(train_frame, spec, params, config)

        # ------------------------------------------------------------------------
        # 第一步：预测origin_year + 1年（预测距离1年）
        # ------------------------------------------------------------------------

        # 预测origin_year + 1年的自变量
        forecast_history = append_forecast_year(observed_history, origin_year + 1)

        # 构建origin_year + 1年的特征
        feature_step_1 = make_target_feature_frame(forecast_history, spec,
                                                  country_codes, origin_year + 1)
        if feature_step_1.empty:
            continue

        # 预测origin_year + 1年的冲突水平
        result_step_1 = prediction_table(
            model,
            feature_step_1[["ccode", "year", *spec.feature_cols]],
            origin_year + 1,
            classes,
        )

        # 与真实值合并
        step_1 = result_step_1.merge(actual_target_frame(raw_df, origin_year + 1),
                                    on="ccode", how="inner")
        step_1["origin_year"] = origin_year
        step_1["target_year"] = origin_year + 1
        step_1["horizon"] = 1  # 预测距离1年
        step_1 = step_1.rename(columns={f"predicted_conflict_{origin_year + 1}":
                                        "predicted_intensity"})
        rows.append(step_1)

        # ------------------------------------------------------------------------
        # 第二步：递推预测origin_year + 2年（预测距离2年）
        # ------------------------------------------------------------------------

        # 将预测结果注入数据集，用于递推预测
        recursive_history = inject_predictions(forecast_history, result_step_1,
                                              origin_year + 1)

        # 构建origin_year + 2年的特征
        feature_step_2 = make_target_feature_frame(recursive_history, spec,
                                                  country_codes, origin_year + 2)
        if feature_step_2.empty:
            continue

        # 预测origin_year + 2年的冲突水平
        result_step_2 = prediction_table(
            model,
            feature_step_2[["ccode", "year", *spec.feature_cols]],
            origin_year + 2,
            classes,
        )

        # 与真实值合并
        step_2 = result_step_2.merge(actual_target_frame(raw_df, origin_year + 2),
                                    on="ccode", how="inner")
        step_2["origin_year"] = origin_year
        step_2["target_year"] = origin_year + 2
        step_2["horizon"] = 2  # 预测距离2年
        step_2 = step_2.rename(columns={f"predicted_conflict_{origin_year + 2}":
                                        "predicted_intensity"})
        rows.append(step_2)

    # 如果没有产生任何结果，报错
    if not rows:
        raise RuntimeError("递推回测没有产生任何结果。")

    # 合并所有回测结果
    backtest_df = pd.concat(rows, ignore_index=True)

    # 计算总体回测指标
    metrics = {"combined": score_prediction_rows(backtest_df, classes)}

    # 计算不同预测距离的指标
    # horizon=1：预测距离1年的指标
    # horizon=2：预测距离2年的指标
    for horizon in sorted(backtest_df["horizon"].unique().tolist()):
        horizon_df = backtest_df[backtest_df["horizon"] == horizon].reset_index(drop=True)
        metrics[f"horizon_{horizon}"] = score_prediction_rows(horizon_df, classes)

    return backtest_df, metrics


# ============================================================================
# 第十部分：输出保存函数
# ============================================================================

def save_outputs(
    config: RunConfig,
    forecast_df: pd.DataFrame,
    metrics: dict[str, Any],
    recursive_backtest_df: pd.DataFrame,
    classes: list[int],
    result_2025: pd.DataFrame,
    result_2026: pd.DataFrame,
    model: Pipeline,
    search: SearchResult,
    country_codes: dict[int, int],
) -> None:
    """
    保存所有输出文件

    参数说明：
        config: 运行配置
        forecast_df: 包含预测年的DataFrame
        metrics: 评估指标
        recursive_backtest_df: 回测结果
        classes: 所有类别列表
        result_2025: 2025年预测结果
        result_2026: 2026年预测结果
        model: 最终模型
        search: 搜索结果
        country_codes: 国家代码映射

    功能说明：
        - 保存包含预测数据的数据集
        - 保存预测结果
        - 保存回测结果
        - 保存评估表格
        - 保存ROC曲线
        - 保存评估指标JSON
        - 保存模型对象

    输出文件列表：
        1. {prefix}_with_2025.csv：包含2025年数据的DataFrame
        2. {prefix}_predictions_2025.csv：2025年预测结果
        3. {prefix}_predictions_2026.csv：2026年预测结果
        4. {prefix}_recursive_backtest.csv：递推回测结果
        5. {prefix}_holdout_class_table.csv：各类别得分表
        6. {prefix}_holdout_overall_table.csv：总体得分表
        7. {prefix}_model_selection_table.csv：模型选择结果表
        8. {prefix}_report_tables.md：所有表格（Markdown）
        9. {prefix}_roc_curve.svg：ROC曲线图
        10. {prefix}_metrics.json：评估指标JSON
        11. {prefix}_model.joblib：模型对象（包含模型、参数、配置等）
    """
    prefix = Path(config.output_prefix)

    # 保存包含2025年数据的DataFrame
    forecast_df.to_csv(f"{prefix}_with_2025.csv", index=False)

    # 保存预测结果
    result_2025.to_csv(f"{prefix}_predictions_2025.csv", index=False)
    result_2026.to_csv(f"{prefix}_predictions_2026.csv", index=False)

    # 保存回测结果
    recursive_backtest_df.to_csv(f"{prefix}_recursive_backtest.csv", index=False)

    # 保存结果表格
    save_report_tables(prefix, metrics, search, classes)

    # 保存ROC曲线
    save_roc_curve(metrics["roc"], Path(f"{prefix}_roc_curve.svg"))

    # 保存评估指标JSON
    # to_builtin将numpy类型转换为Python内置类型
    # ensure_ascii=False允许非ASCII字符（如中文）
    # indent=2设置缩进为2个空格
    with Path(f"{prefix}_metrics.json").open("w", encoding="utf-8") as fh:
        json.dump(to_builtin(metrics), fh, ensure_ascii=False, indent=2)

    # 保存模型对象
    # joblib.dump可以保存Python对象（包括sklearn模型）
    payload = {
        "config": {**asdict(config), "data_path": str(config.data_path)},
        "search": {
            "dv_lag": search.spec.dv_lag,
            "iv_lag": search.spec.iv_lag,
            "feature_cols": search.spec.feature_cols,
            "numeric_cols": search.spec.numeric_cols,
            "best_params": search.best_params,
            "best_score": search.best_score,
        },
        "country_codes": country_codes,
        "model": model,
    }
    joblib.dump(payload, f"{prefix}_model.joblib")


# ============================================================================
# 第十一部分：主运行函数
# ============================================================================

def run(config: RunConfig) -> None:
    """
    主运行函数

    参数说明：
        config: 运行配置

    功能说明：
        完整的预测流程：
        1. 数据准备：加载数据，生成预测年份数据
        2. 模型选择：使用交叉验证选择最优模型
        3. 模型评估：在验证集上评估模型性能
        4. 递推回测：模拟真实预测流程，评估预测准确率
        5. 最终预测：使用所有数据拟合模型，预测2025年和2026年
        6. 结果保存：保存所有输出文件

    执行流程说明：

    第一步：数据准备
    - 加载1961-2024年的原始数据
    - 预测2025年的自变量（使用ARIMA和简单外推）
    - 构建国家代码映射
    - 添加滞后特征

    第二步：模型选择
    - 使用expanding-window 3折交叉验证
    - 尝试不同的滞后特征组合
    - 尝试不同的超参数组合
    - 选择宏观F1得分最高的模型

    第三步：模型评估
    - 使用选定的模型参数
    - 在1961-2010年数据上训练
    - 在2011-2024年数据上验证
    - 计算各种评估指标

    第四步：递推回测
    - 模拟真实预测场景
    - 使用历史数据训练
    - 预测下一年和下下一年
    - 与真实值比较
    - 计算预测准确率

    第五步：最终预测
    - 使用所有数据（1961-2024年）训练
    - 预测2025年
    - 使用2025年预测结果预测2026年

    第六步：结果保存
    - 保存所有输出文件
    - 打印结果摘要
    """
    # ========== 第一步：数据准备 ==========
    print("=== 数据准备阶段 ===")
    print(f"正在加载数据文件: {config.data_path}")

    # 加载数据
    raw_df = load_domestic_data(config.data_path)
    print(f"数据加载完成：{len(raw_df)} 行，{raw_df['year'].min()}-{raw_df['year'].max()} 年")

    # 生成描述性统计
    descriptive_stats_path = Path(config.output_prefix + "_descriptive_stats.md")
    generate_descriptive_stats(raw_df, descriptive_stats_path)

    # 推断类别
    classes = infer_classes(raw_df)
    print(f"因变量类别: {classes}")

    # 生成2025年的数据（预测自变量）
    # 注意：只预测自变量，因变量留空（NaN）
    forecast_df = append_forecast_year(raw_df, config.forecast_year)
    print(f"已生成 {config.forecast_year} 年的自变量预测")

    # 构建国家代码映射
    country_codes = build_country_code_map(forecast_df)
    print(f"国家数量: {len(country_codes)}")

    # 构建滞后特征
    lagged_df = build_lagged_frame(forecast_df, country_codes, config)
    print("滞后特征构建完成")

    # ========== 第二步：模型选择 ==========
    print("\n=== 模型选择阶段 ===")
    print(f"使用expanding-window {config.n_splits}折交叉验证")
    print("交叉验证配置:")
    for idx, (train_start, train_end, valid_start, valid_end) in enumerate(CV_SPLITS, 1):
        print(f"  第{idx}折: 训练集{train_start}-{train_end}年, 验证集{valid_start}-{valid_end}年")

    # 构建所有可能的特征规范
    specs = build_feature_specs(config.max_dv_lag, config.max_iv_lag)
    print(f"待测试的特征规范数量: {len(specs)}")

    # 使用网格搜索寻找最佳模型
    search = search_best_model(lagged_df, specs, config)
    print(f"最佳模型已找到: 宏观F1 = {search.best_score:.4f}")
    print(f"  因变量滞后期: {search.spec.dv_lag}, 自变量滞后期: {search.spec.iv_lag}")

    # ========== 第三步：模型评估 ==========
    print("\n=== 模型评估阶段 ===")

    # 构建观测数据
    model_df = build_observed_frame_for_spec(lagged_df, search.spec,
                                            config.observed_last_year)

    # 划分训练集和验证集
    # 训练集：1961-2010年（train_cutoff=2011，所以<2011）
    # 验证集：2011-2024年（train_cutoff=2011到observed_last_year=2024）
    train_df = model_df[model_df["year"] < config.train_cutoff].reset_index(drop=True)
    test_df = model_df[
        (model_df["year"] >= config.train_cutoff) &
        (model_df["year"] <= config.observed_last_year)
    ].reset_index(drop=True)

    print(f"训练集: {train_df['year'].min()}-{train_df['year'].max()} 年")
    print(f"验证集: {test_df['year'].min()}-{test_df['year'].max()} 年")

    # 在训练集上拟合模型
    eval_model = fit_pipeline(train_df, search.spec, search.best_params, config)

    # 在验证集上评估模型
    metrics = evaluate_model(eval_model, test_df, search.spec, classes)
    print(f"验证集宏观F1得分: {metrics['macro_f1']:.4f}")

    # ========== 第四步：递推回测 ==========
    print("\n=== 递推回测阶段 ===")

    # 运行递推回测
    recursive_backtest_df, recursive_backtest_metrics = run_recursive_backtest(
        raw_df=raw_df,
        spec=search.spec,
        params=search.best_params,
        country_codes=country_codes,
        config=config,
        classes=classes,
    )

    print(f"递推回测总体宏观F1得分: {recursive_backtest_metrics['combined']['macro_f1']:.4f}")
    for horizon in sorted(key for key in recursive_backtest_metrics
                         if key.startswith("horizon_")):
        print(f"  预测距离{horizon.split('_')[1]}年: "
              f"{recursive_backtest_metrics[horizon]['macro_f1']:.4f}")

    metrics["recursive_backtest"] = recursive_backtest_metrics

    # ========== 第五步：最终预测 ==========
    print("\n=== 最终预测阶段 ===")

    # 使用所有观测数据拟合最终模型
    # 注意：这里使用model_df，包含所有观测数据（1961-2024年）
    print(f"使用所有数据 ({model_df['year'].min()}-{model_df['year'].max()}年) 拟合最终模型")
    final_model = fit_pipeline(model_df, search.spec, search.best_params, config)

    # ------------------------------------------------------------------------
    # 预测2025年
    # ------------------------------------------------------------------------

    print(f"正在预测 {config.forecast_year} 年...")
    feature_2025 = make_target_feature_frame(forecast_df, search.spec,
                                            country_codes, config.forecast_year)
    result_2025 = prediction_table(
        final_model,
        feature_2025[["ccode", "year", *search.spec.feature_cols]],
        config.forecast_year,
        classes,
    )
    print(f"已预测 {config.forecast_year} 年，共 {len(result_2025)} 个国家")

    # ------------------------------------------------------------------------
    # 预测2026年（递推预测）
    # ------------------------------------------------------------------------

    # 将2025年预测结果注入数据集，用于递推预测2026年
    # 注入后，2025年的冲突水平使用预测值（而非真实值，因为2025年还没有真实值）
    recursive_input = inject_predictions(forecast_df, result_2025, config.forecast_year)

    # 使用注入后的数据构建2026年的特征
    # 注意：2026年的特征需要2025年的值，2025年的值是预测的
    print(f"正在预测 {config.recursive_year} 年（递推预测）...")
    feature_2026 = make_target_feature_frame(recursive_input, search.spec,
                                            country_codes, config.recursive_year)
    result_2026 = prediction_table(
        final_model,
        feature_2026[["ccode", "year", *search.spec.feature_cols]],
        config.recursive_year,
        classes,
    )
    print(f"已预测 {config.recursive_year} 年，共 {len(result_2026)} 个国家")

    # ========== 第六步：结果保存 ==========
    print("\n=== 结果保存阶段 ===")

    # 保存所有输出
    save_outputs(
        config=config,
        forecast_df=forecast_df,
        metrics=metrics,
        recursive_backtest_df=recursive_backtest_df,
        classes=classes,
        result_2025=result_2025,
        result_2026=result_2026,
        model=final_model,
        search=search,
        country_codes=country_codes,
    )

    print("所有文件已保存")

    # ========== 打印结果摘要 ==========
    print("\n" + "="*50)
    print("运行结果摘要")
    print("="*50)

    print("\n【模型选择结果】")
    print(f"最佳交叉验证宏观F1得分: {search.best_score:.4f}")
    print(f"因变量滞后期: {search.spec.dv_lag} 年")
    print(f"自变量滞后期: {search.spec.iv_lag} 年")

    print("\n【模型参数】")
    print(search.best_params)

    print("\n【验证集性能】")
    print(f"宏观F1得分: {metrics['macro_f1']:.4f}")
    print("混淆矩阵:")
    print(pd.DataFrame(metrics["confusion_matrix"]))

    print("\n各类别详细得分:")
    print(build_holdout_class_table(metrics, classes).to_string(index=False))

    print("\n总体指标:")
    print(build_holdout_overall_table(metrics).to_string(index=False))

    print("\n【模型选择结果】")
    print(build_model_selection_table(search).to_string(index=False))

    print("\n【递推回测性能】")
    print(f"总体宏观F1得分: {metrics['recursive_backtest']['combined']['macro_f1']:.4f}")
    for horizon in sorted(key for key in metrics['recursive_backtest']
                         if key.startswith("horizon_")):
        print(f"预测距离{horizon.split('_')[1]}年: "
              f"{metrics['recursive_backtest'][horizon]['macro_f1']:.4f}")

    print("\n【预测结果】")
    print(f"{config.forecast_year} 年预测: {len(result_2025)} 个国家")
    print(f"{config.recursive_year} 年预测: {len(result_2026)} 个国家")

    print("\n【输出文件】")
    print(f"{config.output_prefix}_with_2025.csv")
    print(f"{config.output_prefix}_predictions_2025.csv")
    print(f"{config.output_prefix}_predictions_2026.csv")
    print(f"{config.output_prefix}_recursive_backtest.csv")
    print(f"{config.output_prefix}_holdout_class_table.csv")
    print(f"{config.output_prefix}_holdout_overall_table.csv")
    print(f"{config.output_prefix}_model_selection_table.csv")
    print(f"{config.output_prefix}_report_tables.md")
    print(f"{config.output_prefix}_metrics.json")
    print(f"{config.output_prefix}_roc_curve.svg")
    print(f"{config.output_prefix}_model.joblib")

    print("\n运行完成!")


# ============================================================================
# 第十二部分：程序入口
# ============================================================================

if __name__ == "__main__":
    """
    程序入口

    功能说明：
        - 解析命令行参数
        - 运行主函数

    __name__说明：
        __name__是Python的特殊变量
        - 当脚本直接运行时，__name__ == "__main__"
        - 当脚本被导入时，__name__ == 脚本文件名

    这种写法的好处：
        - 脚本可以直接运行：python script.py
        - 脚本可以导入使用：import script
        - 导入时不会自动运行main函数
    """
    # 解析命令行参数
    config = parse_args()

    # 运行主函数
    run(config)
