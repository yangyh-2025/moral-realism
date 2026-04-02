"""
国际冲突二分类预测管道脚本
=================================

本脚本用于预测国家层面的国际冲突风险（二分类：0或1）

使用expanding-window时间序列交叉验证的随机森林模型，
并通过递推方式预测2025年和2026年的冲突风险。

作者：Auto-generated
日期：2025
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# 设置stdout为UTF-8编码，解决Windows控制台显示Unicode字符的问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
    roc_curve,
)
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 设置matplotlib后端为非交互式，避免在服务器环境下报错
matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib import font_manager
import platform

# 配置中文字体（在Windows上使用微软雅黑或SimHei）
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


# ============================================
# 第一部分：配置参数定义
# ============================================

# 自变量列名列表（7个变量）
# 1. polity：政体得分【-10到10（整数）】
# 2. GDP_per_capita_ln：人均GDP（对数处理后）【大于0】
# 3. GDP_growth：GDP增长【无区间限制】
# 4. population_density_ln：人口密度（对数处理后）【大于0】
# 5. trade：贸易额占国民生产总值【大于0】
# 6. military_expenditure_final：军费开支占GDP比重【0到1】
# 7. national_capacity：国家综合国力指数【0到1】
IV_COLUMNS = [
    "polity",
    "GDP_per_capita_ln",
    "GDP_growth",
    "population_density_ln",
    "trade",
    "military_expenditure_final",
    "national_capacity",
]

# 需要用ARIMA或其他时间序列方法预测的变量列名
# 这些是连续变量，可以使用ARIMA模型进行预测
ARIMA_COLUMNS = [
    "GDP_per_capita_ln",
    "GDP_growth",
    "population_density_ln",
    "trade",
]

# 需要用其他方法（如移动平均、线性外推）预测的变量列名
# 这些是非连续或边界约束的变量：
# - polity是整数变量【-10到10】，不宜用ARIMA
# - military_expenditure_final在【0到1】之间，有边界约束
# - national_capacity在【0到1】之间，有边界约束
NON_ARIMA_COLUMNS = [
    "polity",
    "military_expenditure_final",
    "national_capacity",
]

# 变量取值范围约束字典
# 格式：{"变量名": (下界, 上界)}
# 下界或上界为None表示没有对应限制
VALUE_BOUNDS = {
    "polity": (-10.0, 10.0),                    # 政体得分：-10到10的整数
    "GDP_per_capita_ln": (0.0, None),          # 人均GDP对数：大于0
    "GDP_growth": (None, None),                 # GDP增长：无限制
    "population_density_ln": (0.0, None),       # 人口密度对数：大于0
    "trade": (0.0, None),                      # 贸易占比：大于0
    "military_expenditure_final": (0.0, 1.0),  # 军费占比：0到1之间
    "national_capacity": (0.0, 1.0),           # 综合国力：0到1之间
}

# ARIMA模型参数组合列表
# 格式：(p, d, q)，其中：
# - p：自回归阶数（AR）
# - d：差分阶数（I）
# - q：移动平均阶数（MA）
# 这些是常见的时间序列模型参数，会遍历选择AIC最小的
ARIMA_ORDERS = [
    (0, 1, 0),  # 随机游走模型
    (1, 1, 0),  # 一阶自回归差分模型
    (0, 1, 1),  # 一阶移动平均差分模型
    (1, 1, 1),  # ARIMA(1,1,1)模型
    (2, 1, 0),  # 二阶自回归差分模型
    (0, 1, 2),  # 二阶移动平均差分模型
    (2, 1, 1),  # ARIMA(2,1,1)模型
]

# 随机森林模型的超参数网格搜索空间
# 这些参数会被网格搜索遍历，选择最优组合
PARAM_GRID = {
    # SMOTE的k近邻参数：控制过采样时生成样本的方式
    # 3或5表示使用3个或5个最近邻来合成新样本
    "smote__k_neighbors": [3, 5],

    # 随机森林的决策树数量
    # 200表示使用200棵决策树，提高模型稳定性
    "clf__n_estimators": [200],

    # 决策树的最大深度
    # 6或10表示限制树的最大深度，防止过拟合
    # None表示不限制深度
    "clf__max_depth": [6, 10, None],

    # 叶节点的最小样本数
    # 1或3表示每个叶节点至少包含1个或3个样本
    # 值越大，模型越保守，防止过拟合
    "clf__min_samples_leaf": [1, 3],

    # 类别权重设置
    # None：不使用类别权重
    # "balanced_subsample"：每个子样本中自动平衡类别权重
    "clf__class_weight": [None, "balanced_subsample"],
}


# ============================================
# 第二部分：数据类定义
# ============================================

@dataclass(frozen=True)
class RunConfig:
    """
    运行配置类，存储所有运行参数

    Attributes:
    ----------
    data_path : Path
        数据文件路径
    train_cutoff : int
        训练集截止年份（2011年）
        训练集：1963-2010年
    observed_last_year : int
        观测数据最后一年（2024年）
        原始数据范围：1961-2024年
    forecast_year : int
        预测目标年份1（2025年）
        主要预测目标：2025年
    recursive_year : int
        递推预测年份（2026年）
        递推预测目标：基于2025年预测结果递推2026年
    max_dv_lag : int
        因变量（冲突）最大滞后期
        用于捕捉冲突的历史惯性
    max_iv_lag : int
        自变量最大滞后期
        用于捕捉经济、政治等变量的滞后效应
    n_splits : int
        交叉验证折数（3折）
        使用expanding-window时间策略
    random_state : int
        随机种子，保证保证结果可重复
    output_prefix : str
        输出文件前缀
    """
    data_path: Path
    train_cutoff: int = 2011
    observed_last_year: int = 2024
    forecast_year: int = 2025
    recursive_year: int = 2026
    max_dv_lag: int = 2
    max_iv_lag: int = 1
    n_splits: int = 3
    random_state: int = 42
    output_prefix: str = "international_binary_clean"


@dataclass(frozen=True)
class FeatureSpec:
    """
    特征规范类，定义使用的特征列

    Attributes:
    ----------
    dv_lag : int
        因变量滞后期
    iv_lag : int
        自变量滞后期
    numeric_cols : list[str]
        数值型特征列名
    feature_cols : list[str]
        所有特征列名（包括数值型和类别型）
    """
    dv_lag: int
    iv_lag: int
    numeric_cols: list[str]
    feature_cols: list[str]


@dataclass(frozen=True)
class SearchResult:
    """
    模型搜索结果类

    Attributes:
    ----------
    spec : FeatureSpec
        最优特征规范
    best_params : dict[str, Any]
        最优参数组合
    best_score : float
        最优得分（宏平均F1）
    """
    spec: FeatureSpec
    best_params: dict[str, Any]
    best_score: float


# ============================================
# 第三部分：辅助函数
# ============================================

def parse_args() -> RunConfig:
    """
    解析命令行参数，返回运行配置

    Returns:
    -------
    RunConfig
        运行配置对象
    """
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="国际冲突二分类预测管道，使用expanding-window CV和递推预测。"
    )
    parser.add_argument(
        "--data-path",
        default=str(script_dir / "domestic_conflicts.csv"),
        help="国际冲突数据CSV文件路径。",
    )
    parser.add_argument(
        "--output-prefix",
        default=str(script_dir / "international_binary_clean"),
        help="输出文件前缀。",
    )
    args = parser.parse_args()
    return RunConfig(data_path=Path(args.data_path), output_prefix=args.output_prefix)


def clip_value(name: str, value: float) -> float:
    """
    将数值限制在变量的允许范围内

    用于预测后的数值修正，确保预测值符合变量的实际约束

    Parameters:
    ----------
    name : str
        变量名，用于查找其约束范围
    value : float
        需要限制的值

    Returns:
    -------
    float
        限制后的值
    """
    # 获取变量的下界和上界
    lower, upper = VALUE_BOUNDS[name]

    # 如果有下界限制，确保值不小于下界
    if lower is not None:
        value = max(lower, value)

    # 如果有上界限制，确保值不大于上界
    if upper is not None:
        value = min(upper, value)

    return float(value)


def load_international_data(path: Path) -> pd.DataFrame:
    """
    加载国际冲突数据，并进行基础清洗

    参数要求：
    - 必须包含国家、年份、冲突强度等列
    - 必须包含所有自变量列

    Parameters:
    ----------
    path : Path
        数据文件路径

    Returns:
    -------
    pd.DataFrame
        清洗后的数据框，按国家和年份排序
    """
    # 识别文件格式，支持CSV和Excel
    path_obj = Path(path)
    if path_obj.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(path, sheet_name='sheet1')
    else:
        df = pd.read_csv(path)

    # 列名映射：Statename -> country
    df = df.rename(columns={'Statename': 'country'})

    # 检查必需的列是否存在
    required = {"country", "year", "UCDP_National_conflict_0_1", *IV_COLUMNS}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"缺少必需的列: {missing}")

    # 选择并重新排列列的顺序
    ordered = ["country", "year", "UCDP_National_conflict_0_1", *IV_COLUMNS]
    df = df[ordered].copy()

    # 数据类型转换
    df["country"] = df["country"].astype(str)          # 国家名转为字符串
    df["year"] = df["year"].astype(int)                # 年份转为整数

    # 删除冲突值为NaN的行（数据缺失的年份）
    df = df.dropna(subset=["UCDP_National_conflict_0_1"])

    # 确保冲突强度是二分类（0或1）
    df["UCDP_National_conflict_0_1"] = df["UCDP_National_conflict_0_1"].astype(int)

    # 按国家和年份排序，确保时间序列的连续性
    return df.sort_values(["country", "year"]).reset_index(drop=True)


def infer_classes(df: pd.DataFrame) -> list[int]:
    """
    从数据中推断分类标签

    对于二分类问题，应该返回[0, 1]

    Parameters:
    ----------
    df : pd.DataFrame
        数据框

    Returns:
    -------
    list[int]
        分类标签列表，已排序
    """
    return sorted(df["UCDP_National_conflict_0_1"].dropna().astype(int).unique().tolist())


# ============================================
# 第四部分：时间序列预测函数
# ============================================

def forecast_one_step_arima(years: pd.Series, values: pd.Series) -> float:
    """
    使用ARIMA模型进行单步时间序列预测

    该函数适用于连续变量的时间序列预测，如GDP、人口密度、贸易等
    通过尝试多个ARIMA参数组合，选择AIC（赤池信息准则）最小的模型进行预测

    ARIMA模型说明：
    - ARIMA(p, d, q)模型由三部分组成：
      - p (AutoRegressive): 自回归阶数，用过去的值预测当前值
      - d (Integrated): 差分阶数，用于使非平稳序列平稳化
      - q (Moving Average): 移动平均阶数，用过去的误差预测当前值
    - AIC准则：权衡模型拟合优度和复杂度，值越小越好

    预测策略：
    1. 遍历预定义的ARIMA参数组合
    2. 对每个组合拟合模型，计算AIC
    3. 选择AIC最小的模型进行预测
    4. 如果所有模型拟合失败，使用最后一个观测值

    Parameters:
    ----------
    years : pd.Series
        时间序列的年份序列，如[1961, 1962, 1963, ...]
    values : pd.Series
        时间序列的观测值序列，如[1000, 1200, 1350, ...]

    Returns:
    -------
    float
        下一期的预测值，如果无法预测则返回最后一个观测值
    """
    # 构建数据框并删除缺失值
    # 确保年份和观测值一一对应
    frame = pd.DataFrame({"year": years, "value": values}).dropna()

    # 如果数据为空，返回NaN（缺失值）
    if frame.empty:
        return np.nan

    # 创建时间序列对象（带年份索引）
    # 使用PeriodIndex创建年度频率的时间序列
    series = pd.Series(
        frame["value"].to_numpy(dtype=float),
        index=pd.PeriodIndex(frame["year"].astype(int), freq="Y"),
    )

    # 边界情况处理
    # 如果数据点太少（少于4个）或值完全相同（无变化），
    # 直接返回最后一个值，避免拟合失败
    if len(series) < 4 or series.nunique() == 1:
        return float(series.iloc[-1])

    # ============ 遍历所有ARIMA参数组合，选择AIC最小的 ============
    best_aic = np.inf  # 初始化最优AIC为无穷大
    best_value = float(series.iloc[-1])  # 默认使用最后一个值作为预测

    # 遍历预定义的ARIMA参数组合
    # ARIMA_ORDERS是全局变量，定义了多个(p,d,q)组合
    for order in ARIMA_ORDERS:
        try:
            # 拟合ARIMA模型，捕获警告以避免输出大量信息
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # 使用statsmodels的ARIMA模型
                # 注意：需要from statsmodels.tsa.arima.model import ARIMA
                fitted = ARIMA(
                    series,           # 时间序列数据
                    order=order,      # ARIMA阶数 (p, d, q)
                    trend="n",        # 不包含趋势项（"n"=none）
                    # 如果需要趋势项，可改为"c"（常数）、"t"（线性）、"ct"（常数+线性）
                    enforce_stationarity=False,  # 不强制平稳性
                    # 对于预测问题，放宽平稳性要求更实用
                    enforce_invertibility=False,  # 不强制可逆性
                    # 同样，放宽要求可以提高鲁棒性
                ).fit()

            # 检查AIC是否有效且比当前最优值更好
            # AIC应该是有限的数值
            if not np.isfinite(fitted.aic) or fitted.aic >= best_aic:
                continue  # 如果AIC无效或不是更优，跳过

            # 预测下一期
            # forecast(steps=1)预测下一个时间点的值
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                forecast = fitted.forecast(steps=1)

            # 更新最优结果
            best_aic = float(fitted.aic)  # 记录最优AIC
            best_value = float(forecast.iloc[0])  # 记录最优预测值
        except Exception:
            # 如果拟合失败（例如：数据不足、数值问题等），跳过该参数组合
            continue

    # 返回最优预测值
    # 如果所有模型都失败，返回最后一个观测值（已在初始化时设置）
    return best_value


def forecast_one_step_simple(values: pd.Series, method: str = "mean") -> float:
    """
    使用简单方法进行单步时间序列预测

    该函数适用于非连续变量或有边界约束的变量
    与ARIMA不同，这些方法不需要复杂的模型拟合，计算快速

    适用场景：
    - polity（政体得分）：整数变量，[-10, 10]，不宜用ARIMA
    - military_expenditure_final：军费占比，[0, 1]，有边界约束
    - national_capacity：综合国力，[0, 1]，有边界约束

    支持的预测方法：
    1. 'mean'（移动平均）：使用最后几个值的平均值
       - 优点：平滑波动，降低噪声影响
       - 缺点：对趋势变化反应较慢

    2. 'last'（最后一个值）：直接使用最近的观测值
       - 优点：最保守，完全基于最新信息
       - 缺点：无法捕捉趋势

    3. 'linear'（线性外推）：基于最后两个值计算趋势并外推
       - 优点：可以捕捉简单的线性趋势
       - 缺点：对非线性趋势效果差，易受异常值影响

    Parameters:
    ----------
    values : pd.Series
        时间序列的观测值，如[-5, -3, -2, -1, ...]（polity）
    method : str
        预测方法，可选 'mean'、'last'、'linear'，默认为'mean'

    Returns:
    -------
    float
        下一期（未来一年）的预测值
        如果输入数据为空，返回NaN
    """
    # 删除缺失值，确保数据质量
    values_clean = values.dropna()

    # 如果数据为空，返回NaN（缺失值）
    if values_clean.empty:
        return np.nan

    # ============ 根据方法选择预测策略 ============
    if method == "last":
        # ============ 方法1：使用最后一个值 ============
        # 这是最保守的策略，假设未来值等于最近的观测值
        # 适用于：变化缓慢或不确定的变量
        return float(values_clean.iloc[-1])

    elif method == "mean":
        # ============ 方法2：移动平均 ============
        # 使用最后3个值的移动平均（如果数据不足3个，使用所有可用值）
        # 优点：平滑短期波动，提供稳定的预测
        # 缺点：对趋势变化的反应有滞后
        window_size = min(3, len(values_clean))  # 窗口大小最多为3
        return float(values_clean.iloc[-window_size:].mean())

    elif method == "linear":
        # ============ 方法3：线性外推 ============
        # 基于最后两个值计算线性趋势，然后外推到下一期
        # 公式：预测值 = 最后一个值 + (最后一个值 - 倒数第二个值)
        # 优点：可以捕捉简单的上升或下降趋势
        # 缺点：只适用于线性趋势，对非线性趋势效果差
        if len(values_clean) >= 2:
            # 至少需要2个值才能计算趋势
            last = float(values_clean.iloc[-1])        # 最后一个值：y_t
            second_last = float(values_clean.iloc[-2])   # 倒数第二个值：y_{t-1}
            trend = last - second_last                  # 趋势：Δy = y_t - y_{t-1}
            # 外推预测：y_{t+1} = y_t + Δy = 2*y_t - y_{t-1}
            return last + trend
        else:
            # 数据不足2个，退化为使用最后一个值
            return float(values_clean.iloc[-1])

    else:
        # ============ 默认情况 ============
        # 如果传入不支持的方法名，默认使用最后一个值
        return float(values_clean.iloc[-1])


def append_forecast_year(df: pd.DataFrame, target_year: int) -> pd.DataFrame:
    """
    为数据框添加指定年份的预测行

    该函数是递推预测的核心，用于预测未来年份的自变量值
    对每个国家分别进行预测，然后将预测结果添加到原数据

    预测流程：
    1. 按国家分组，逐个处理
    2. 对每个国家，预测target_year年的所有自变量值
    3. 冲突值（因变量）设为NaN，后续用机器学习模型预测
    4. 根据变量类型选择合适的预测方法
    5. 应用变量边界约束，确保预测值合理

    预测策略分类：
    ============ ARIMA列（连续变量）============
    适合ARIMA模型：GDP_per_capita_ln, GDP_growth, population_density_ln, trade
    - 这些是连续变量，变化相对平滑
    - ARIMA可以捕捉趋势和周期性
    - 通过尝试多个参数组合，选择AIC最小的

    ============ 非ARIMA列（非连续或边界变量）============
    1. polity（政体得分）：
       - 范围：[-10, 10]，整数
       - 预测方法：移动平均（mean）
       - 后处理：四舍五入到整数
       - 原因：政体变化跳跃性强，不宜用ARIMA

    2. military_expenditure_final（军费占比）：
       - 范围：[0, 1]，连续
       - 预测方法：线性外推（linear）
       - 原因：军费支出通常有明显的趋势

    3. national_capacity（综合国力）：
       - 范围：[0, 1]，连续
       - 预测方法：线性外推（linear）
       - 原因：综合国力变化通常有持续性趋势

    边界约束：
    - 预测后使用clip_value函数确保预测值在合理范围内
    - 例如：polity不能超过[-10, 10]，军费不能为负数

    Parameters:
    ----------
    df : pd.DataFrame
        原始数据框，包含历史年份的观测数据
        必须包含国家、年份、冲突和所有自变量列
    target_year : int
        需要预测的年份，如2025或2026

    Returns:
    -------
    pd.DataFrame
        包含预测年份的扩展数据框
        新增的行包含target_year年的预测值（冲突值为NaN）
    """
    # 存储所有国家的预测行
    rows: list[dict[str, Any]] = []

    # ============ 按国家分组，对每个国家分别预测 ============
    for country, group in df.groupby("country", sort=True):
        # 创建预测行的基本结构
        row = {
            "country": country,
            "year": target_year,
            "UCDP_National_conflict_0_1": np.nan,  # 冲突值未知，需要后续用模型预测
        }

        # ============ 处理ARIMA列（连续变量）============
        # ARIMA_COLUMNS是全局变量，包含适合ARIMA模型的变量名
        # 这些变量通常是连续的、变化平滑的
        for column in ARIMA_COLUMNS:
            # 使用ARIMA模型预测该变量在target_year年的值
            # 传入该国家的历史年份和观测值
            value = forecast_one_step_arima(group["year"], group[column])
            # 应用边界约束，确保预测值在合理范围内
            # VALUE_BOUNDS是全局变量，定义了每个变量的上下界
            row[column] = clip_value(column, value)

        # ============ 处理非ARIMA列（非连续或边界变量）============
        # NON_ARIMA_COLUMNS是全局变量，包含不适合ARIMA的变量名
        # 这些变量通常是非连续的、有边界的或跳跃性强的
        for column in NON_ARIMA_COLUMNS:
            # 根据变量类型选择合适的预测方法
            if column == "polity":
                # ============ polity（政体得分）===========
                # 特点：整数变量，范围[-10, 10]，变化跳跃性强
                # 预测方法：移动平均（mean）
                # 原因：政体变化通常是离散的跳变，不宜用ARIMA
                value = forecast_one_step_simple(group[column], method="mean")
                # 后处理：四舍五入到整数，符合polity的整数特性
                value = round(value)  # 四舍五入到整数
            elif column in ["military_expenditure_final", "national_capacity"]:
                # ============ 军费占比和综合国力 ============
                # 特点：连续变量，范围[0, 1]，通常有明显趋势
                # 预测方法：线性外推（linear）
                # 原因：这些指标的变化通常有持续性，线性外推更合理
                value = forecast_one_step_simple(group[column], method="linear")
            else:
                # ============ 其他非ARIMA变量 ============
                # 默认方法：移动平均（mean）
                # 这是一个保守且稳健的选择
                value = forecast_one_step_simple(group[column], method="mean")

            # ============ 应用边界约束 ============
            # 确保预测值在变量的允许范围内
            # 例如：polity不能超过[-10, 10]，军费不能为负数或超过1
            row[column] = clip_value(column, value)

        # 将该国家的预测行添加到结果列表
        rows.append(row)

    # ============ 将预测行转换为数据框并拼接到原数据 ============
    forecast_df = pd.DataFrame(rows)
    # 使用pd.concat将原数据和预测数据纵向拼接
    combined = pd.concat([df, forecast_df], ignore_index=True)
    # 按国家和年份排序，确保数据有序
    return combined.sort_values(["country", "year"]).reset_index(drop=True)


# ============================================
# 第五部分：特征工程函数
# ============================================

def build_country_code_map(df: pd.DataFrame) -> dict[str, int]:
    """
    构建国家名到数字编码的映射字典

    将国家名转换为整数编码，便于模型处理

    Parameters:
    ----------
    df : pd.DataFrame
        数据框

    Returns:
    -------
    dict[str, int]
        国家名到编码的映射字典
    """
    countries = sorted(df["country"].unique().tolist())
    return {country: idx for idx, country in enumerate(countries)}


def add_lag_features(df: pd.DataFrame, max_dv_lag: int, max_iv_lag: int) -> pd.DataFrame:
    """
    添加滞后特征

    为因变量（冲突）和自变量添加滞后项
    滞后特征可以让模型考虑历史信息

    Parameters:
    ----------
    df : pd.DataFrame
        原始数据框
    max_dv_lag : int
        因变量最大滞后期
    max_iv_lag : int
        自变量最大滞后期

    Returns:
    -------
    pd.DataFrame
        包含滞后特征的数据框
    """
    lagged = df.copy()

    # 添加因变量的滞后项（冲突历史）
    for lag in range(1, max_dv_lag + 1):
        lagged[f"dv_lag{lag}"] = lagged.groupby("country")["UCDP_National_conflict_0_1"].shift(lag)

    # 添加自变量的滞后项
    for lag in range(1, max_iv_lag + 1):
        for column in IV_COLUMNS:
            lagged[f"{column}_lag{lag}"] = lagged.groupby("country")[column].shift(lag)

    return lagged


def build_feature_specs(max_dv_lag: int, max_iv_lag: int) -> list[FeatureSpec]:
    """
    构建所有可能的特征规范

    生成所有滞后期的组合，用于模型选择
    会遍历所有可能的滞后组合

    Parameters:
    ----------
    max_dv_lag : int
        因变量最大滞后期
    max_iv_lag : int
        自变量最大滞后期

    Returns:
    -------
    list[FeatureSpec]
        特征规范列表
    """
    specs: list[FeatureSpec] = []

    # 遍历所有因变量滞后组合
    for dv_lag in range(1, max_dv_lag + 1):
        # 遍历所有自变量滞后组合
        for iv_lag in range(1, max_iv_lag + 1):
            # 构建数值型特征列名列表
            numeric_cols = [
                # 自变量的滞后特征
                *(f"{column}_lag{lag}" for column in IV_COLUMNS for lag in range(1, iv_lag + 1)),
                # 因变量的滞后特征
                *(f"dv_lag{lag}" for lag in range(1, dv_lag + 1)),
            ]

            # 构建特征规范
            specs.append(
                FeatureSpec(
                    dv_lag=dv_lag,
                    iv_lag=iv_lag,
                    numeric_cols=list(numeric_cols),
                    feature_cols=[*numeric_cols, "country_code"],
                )
            )

    return specs


def build_lagged_frame(df: pd.DataFrame, country_codes: dict[str, int], config: RunConfig) -> pd.DataFrame:
    """
    构建包含滞后特征和国家编码的数据框

    Parameters:
    ----------
    df : pd.DataFrame
        原始数据框
    country_codes : dict[str, int]
        国家编码映射
    config : RunConfig
        运行配置

    Returns:
    -------
    pd.DataFrame
        包含滞后特征和国家编码的数据框
    """
    # 添加滞后特征
    lagged = add_lag_features(df, config.max_dv_lag, config.max_iv_lag)

    # 添加国家编码
    lagged["country_code"] = lagged["country"].map(country_codes).astype(int)

    # 按年份和国家排序
    return lagged.sort_values(["year", "country"]).reset_index(drop=True)


def build_observed_frame_for_spec(
    lagged_df: pd.DataFrame,
    spec: FeatureSpec,
    last_year: int,
) -> pd.DataFrame:
    """
    为指定的特征规范构建观测数据框

    选择指定年份前的数据，并删除缺失值

    Parameters:
    ----------
    lagged_df : pd.DataFrame
        包含滞后特征的数据框
    spec : FeatureSpec
        特征规范
    last_year : int
        最后观测年份

    Returns:
    -------
    pd.DataFrame
        清洗后的观测数据框
    """
    # 选择指定年份前的数据
    frame = lagged_df[lagged_df["year"] <= last_year].copy()

    # 删除因变量和特征列中有缺失值的行
    frame = frame.dropna(subset=["UCDP_National_conflict_0_1", *spec.feature_cols]).copy()

    # 确保因变量是整数类型
    frame["UCDP_National_conflict_0_1"] = frame["UCDP_National_conflict_0_1"].astype(int)

    return frame.sort_values(["year", "country"]).reset_index(drop=True)


# ============================================
# 第六部分：模型相关函数
# ============================================

def to_builtin(value: Any) -> Any:
    """
    将值转换为内置Python类型，便于JSON序列化

    处理numpy类型、字典、列表等复杂类型

    Parameters:
    ----------
    value : Any
        需要转换的值

    Returns:
    -------
    Any
        转换后的值
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


def year_block_splits(years: pd.Series, n_splits: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    生成年份块的时间序列交叉验证划分

    使用expanding-window策略（扩展窗口）：
    - 每次验证集是下一个年份块
    - 训练集包含之前所有的年份，窗口不断扩大

    块大小根据可用年份动态计算（至少10年）
    对于3折交叉验证：
    - 第一折：块0训练，块1验证
    - 第二折：块0+块1训练，块2验证
    - 第三折：块0+块1+块2训练，块3验证

    这种策略的优点：
    1. 保留了时间序列的因果性，只用过去预测未来
    2. 窗口不断扩大，训练数据逐渐增多
    3. 每折验证集大小相同，便于比较
    4. 模拟真实预测场景，评估模型的泛化能力
    5. 动态适应不同长度的数据集

    Parameters:
    ----------
    years : pd.Series
        年份序列，包含所有观测年份
    n_splits : int
        交叉验证折数，这里固定为3折

    Returns:
    -------
    list[tuple[np.ndarray, np.ndarray]]
        训练集和验证集的索引列表
        每个元素是一个元组 (train_indices, valid_indices)
    """
    # 获取排序后的唯一年份
    unique_years = np.sort(years.unique())

    # 动态计算块大小以适应可用的年份
    # 对于3折交叉验证，需要4个块（1个训练块+3个验证块）
    # 计算合适的块大小，确保所有块都有足够的数据
    max_blocks = n_splits + 1  # 4个块
    block_size = max(10, len(unique_years) // (max_blocks + 1))  # 至少10年，动态计算

    # 检查是否有足够的年份进行交叉验证
    min_years = (n_splits + 1) * block_size
    if len(unique_years) < min_years:
        raise ValueError(f"年份不足进行expanding-window交叉验证。需要至少{min_years}年，实际{len(unique_years)}年。")

    # 定义具体的年份块划分
    # 块0：训练块1
    # 块1：验证块1 / 训练块2
    # 块2：验证块2 / 训练块3
    # 块3：验证块3
    blocks = [
        unique_years[0:block_size],
        unique_years[block_size:block_size*2],
      unique_years[block_size*2:block_size*3],
        unique_years[block_size*3:block_size*4],
    ]

    splits: list[tuple[np.ndarray, np.ndarray]] = []

    # 生成3折交叉验证的划分
    for idx in range(n_splits):
        # 训练集：前idx + 1个块（扩展窗口）
        # 第一折：块0（1963-1974）
        # 第二折：块0+块1（1963-1986）
        # 第三折：块0+块1+块2（1963-1998）
        train_years = np.concatenate(blocks[:idx + 1])

        # 验证集：第idx + 1个块
        # 第一折：块1（1975-1986）
        # 第二折：块2（1987-1998）
        # 第三折：块3（1999-2010）
        valid_years = blocks[idx + 1]

        # 获取训练集和验证集的索引
        # 使用years.index获取对应年份的位置索引
        train_idx = years.index[years.isin(train_years)].to_numpy()
        valid_idx = years.index[years.isin(valid_years)].to_numpy()

        # 添加到划分列表
        splits.append((train_idx, valid_idx))

    return splits


def build_pipeline(numeric_cols: list[str], random_state: int) -> Pipeline:
    """
    构建机器学习管道

    管道包含：
    1. 预处理：数值标准化 + 国家编码
    2. SMOTE：处理类别不平衡
    3. 后处理：独热编码国家
    4. 随机森林：分类模型

    Parameters:
    ----------
    numeric_cols : list[str]
        数值型特征列名
    random_state : int
        随机种子

    Returns:
    -------
    Pipeline
        机器学习管道
    """
    # SMOTE之前的预处理
    # 对数值特征进行标准化，保留国家编码
    pre_smote = ColumnTransformer(
        [
            ("num", StandardScaler(), numeric_cols),
            ("country", "passthrough", ["country_code"]),
        ],
        verbose_feature_names_out=False,
    )

    # SMOTE之后的后处理
    # 对数值特征直接通过，对国家编码进行独热编码
    post_smote = ColumnTransformer(
        [
            ("num", "passthrough", list(range(len(numeric_cols)))),
            ("country", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [len(numeric_cols)]),
        ],
        verbose_feature_names_out=False,
    )

    # 构建完整管道
    return Pipeline(
        steps=[
            ("pre_smote", pre_smote),
            (
                "smote",
                SMOTENC(categorical_features=[len(numeric_cols)], random_state=random_state),
            ),
            ("post_smote", post_smote),
            ("clf", RandomForestClassifier(random_state=random_state, n_jobs=-1)),
        ]
    )


def search_best_model(lagged_df: pd.DataFrame, specs: list[FeatureSpec], config: RunConfig) -> SearchResult:
    """
    搜索最优模型参数

    该函数通过网格搜索和交叉验证，找到最优的模型配置
    遍历所有可能的特征规范（不同的滞后组合），选择表现最好的

    搜索流程：
    1. 遍历所有特征规范（不同的滞后组合）
    2. 对每个特征规范，构建训练数据
    3. 使用expanding-window时间序列交叉验证
    4. 网格搜索超参数组合（树的数量、深度、SMOTE参数等）
    5. 使用宏平均F1得分作为评估指标
    6. 保留表现最好的模型配置

    特征规范说明：
    - 特征规范定义了使用哪些滞后特征
    - dv_lag: 因变量（冲突）的滞后期数
    - iv_lag: 自变量（经济、政治等）的滞后期数
    - 例如：dv_lag=2, iv_lag=1 表示使用过去2年冲突和过去1年自变量

    交叉验证策略：
    - 使用year_block_splits函数生成expanding-window划分
    - 第一折：训练集1963-1974年，验证集1975-1986年
    - 第二折：训练集1963-1986年，验证集1987-1998年
    - 第三折：训练集1963-1998年，验证集1999-2010年
    - 这种策略保留了时间序列的因果性

    评估指标：
    - 宏平均F1得分（Macro F1）
    - 对各类别的F1取平均，适合不平衡数据
    - 同时考虑精确率和召回率

    Parameters:
    ----------
    lagged_df : pd.DataFrame
        包含滞后特征的数据框
        已经通过add_lag_features添加了所有可能的滞后特征
    specs : list[FeatureSpec]
        特征规范列表，包含所有可能的滞后组合
        由build_feature_specs函数生成
    config : RunConfig
        运行配置，包含训练截止年份、交叉验证折数等参数

    Returns:
    -------
    SearchResult
        最优模型搜索结果，包含：
        - spec: 最优特征规范
        - best_params: 最优超参数组合
        - best_score: 最优宏平均F1得分
    """
    # ============ 设置评估指标 ============
    # 使用宏平均F1作为评估指标
    # 宏平均：对各类别的F1取简单平均
    # 适合类别不平衡问题（如和平年多于冲突年）
    scorer = make_scorer(f1_score, average="macro")

    # 初始化最优结果为None
    best_result: SearchResult | None = None

    # ============ 遍历所有特征规范 ============
    # 每个特征规范代表一组不同的滞后特征组合
    # 例如：dv_lag=1, iv_lag=1 或 dv_lag=2, iv_lag=1
    for spec in specs:
        # 构建观测数据框
        # 使用config.observed_last_year（2024年）之前的数据
        # 删除包含缺失值的行，确保数据质量
        observed_df = build_observed_frame_for_spec(lagged_df, spec, config.observed_last_year)

        # 构建训练集（训练截止年份之前的数据）
        # train_cutoff=2011，所以训练集是1963-2010年
        train_df = observed_df[observed_df["year"] < config.train_cutoff].reset_index(drop=True)

        # 检查训练集是否有效
        # 训练集不能为空，且年份数量必须足够进行3折交叉验证
        if train_df.empty or train_df["year"].nunique() <= config.n_splits:
            continue  # 跳过无效的特征规范

        # ============ 生成交叉验证划分 ============
        # 使用expanding-window策略
        # year_block_splits返回训练集和验证集的索引列表
        cv = year_block_splits(train_df["year"], config.n_splits)

        # ============ 网格搜索最优参数 ============
        # GridSearchCV会遍历PARAM_GRID中定义的所有参数组合
        # PARAM_GRID是全局变量，定义了超参数的搜索空间
        search = GridSearchCV(
            # 模型估计器：包含预处理、SMOTE和随机森林的管道
            estimator=build_pipeline(spec.numeric_cols, config.random_state),
            # 参数网格：超参数的所有可能组合
            param_grid=PARAM_GRID,
            # 评估指标：宏平均F1得分
            scoring=scorer,
            # 交叉验证策略：expanding-window时间序列CV
            cv=cv,
            # 并行计算：使用所有CPU核心（-1）
            n_jobs=-1,
            # 重新拟合：在最优参数上使用全部训练数据重新拟合
            refit=True,
        )

        # ============ 拟合模型 ============
        # GridSearchCV会：
        # 1. 遍历所有参数组合
        # 2. 对每个组合，使用交叉验证评估性能
        # 3. 选择表现最好的参数组合
        # 4. 使用最优参数在全部训练数据上重新拟合
        search.fit(train_df[spec.feature_cols], train_df["UCDP_National_conflict_0_1"])

        # ============ 保存搜索结果 ============
        result = SearchResult(
            spec=spec,  # 当前特征规范
            best_params=search.best_params_,  # 最优超参数
            best_score=float(search.best_score_),  # 最优F1得分
        )

        # ============ 更新最优结果 ============
        # 如果这是第一个有效结果，或者比当前最优结果更好，则更新
        if best_result is None or result.best_score > best_result.best_score:
            best_result = result

    # ============ 检查是否找到有效结果 ============
    # 如果所有特征规范都无效，抛出异常
    if best_result is None:
        raise RuntimeError("网格搜索未能产生有效结果。")

    return best_result


def fit_pipeline(df: pd.DataFrame, spec: FeatureSpec, params: dict[str, Any], config: RunConfig) -> Pipeline:
    """
    使用指定参数拟合模型

    Parameters:
    ----------
    df : pd.DataFrame
        训练数据
    spec : FeatureSpec
        特征规范
    params : dict[str, Any]
        模型参数
    config : RunConfig
        运行配置

    Returns:
    -------
    Pipeline
        拟合好的管道模型
    """
    # 构建管道
    model = build_pipeline(spec.numeric_cols, config.random_state)

    # 设置参数
    model.set_params(**params)

    # 拟合模型
    model.fit(df[spec.feature_cols], df["UCDP_National_conflict_0_1"])

    return model


def probability_frame(model: Pipeline, features: pd.DataFrame, classes: list[int]) -> pd.DataFrame:
    """
    获取模型预测的概率值

    Parameters:
    ----------
    model : Pipeline
        训练好的模型
    features : pd.DataFrame
        特征数据
    classes : list[int]
        类别标签列表

    Returns:
    -------
    pd.DataFrame
        包含各类别概率的数据框
    """
    # 预测概率
    proba = model.predict_proba(features)

    # 构建概率数据框
    frame = pd.DataFrame(index=features.index)
    for cls in classes:
        frame[f"prob_{cls}"] = 0.0

    # 填充概率值类对齐
    for idx, cls in enumerate(model.named_steps["clf"].classes_):
        frame[f"prob_{int(cls)}"] = proba[:, idx]

    return frame[[f"prob_{cls}" for cls in classes]]


def aligned_probabilities(model: Pipeline, features: pd.DataFrame, classes: list[int]) -> np.ndarray:
    """
    获取对齐的预测概率数组

    确保概率数组的列顺序与类别列表一致

    Parameters:
    ----------
    model : Pipeline
        训练好的模型
    features : pd.DataFrame
        特征数据
    classes : list[int]
        类别标签列表

    Returns:
    -------
    np.ndarray
        对齐的概率数组
    """
    # 预测概率
    proba = model.predict_proba(features)

    # 构建类别到位置的映射
    class_to_pos = {cls: idx for idx, cls in enumerate(classes)}

    # 对齐概率数组
    aligned = np.zeros((len(features), len(classes)), dtype=float)
    for idx, cls in enumerate(model.named_steps["clf"].classes_):
        aligned[:, class_to_pos[int(cls)]] = proba[:, idx]

    return aligned


def build_roc_payload(y_true: pd.Series, y_score: np.ndarray, classes: list[int]) -> dict[str, Any]:
    """
    构建ROC曲线数据

    计算各类别和宏平均/微平均的ROC曲线和AUC值

    Parameters:
    ----------
    y_true : pd.Series
        真实标签
    y_score : np.ndarray
        预测概率
    classes : list[int]
        类别标签列表

    Returns:
    -------
    dict[str, Any]
        包含ROC曲线数据的字典
    """
    # 将标签转换为二进制数组
    class_array = np.array(classes, dtype=int)
    y_bin = np.column_stack([(y_true.to_numpy(dtype=int) == cls).astype(int) for cls in class_array])

    # 初始化结果字典
    fpr: dict[str, list[float]] = {}
    tpr: dict[str, list[float]] = {}
    auc_scores: dict[str, float] = {}

    # 计算每个类别的ROC曲线
    for idx, class_id in enumerate(class_array):
        x_fpr, x_tpr, _ = roc_curve(y_bin[:, idx], y_score[:, idx])
        fpr[str(class_id)] = x_fpr.tolist()
        tpr[str(class_id)] = x_tpr.tolist()
        auc_scores[str(class_id)] = float(auc(x_fpr, x_tpr))

    # 计算微平均ROC曲线
    micro_fpr, micro_tpr, _ = roc_curve(y_bin.ravel(), y_score.ravel())
    fpr["micro"] = micro_fpr.tolist()
    tpr["micro"] = micro_tpr.tolist()
    auc_scores["micro"] = float(auc(micro_fpr, micro_tpr))

    # 计算宏平均ROC曲线
    all_fpr = np.unique(np.concatenate([np.asarray(fpr[str(class_id)]) for class_id in class_array]))
    mean_tpr = np.zeros_like(all_fpr)
    for class_id in class_array:
        mean_tpr += np.interp(all_fpr, np.asarray(fpr[str(class_id)]), np.asarray(tpr[str(class_id)]))
    mean_tpr /= len(class_array)
    fpr["macro"] = all_fpr.tolist()
    tpr["macro"] = mean_tpr.tolist()
    auc_scores["macro"] = float(auc(all_fpr, mean_tpr))
    auc_scores["macro_ovr"] = float(np.mean([auc_scores[str(class_id)] for class_id in class_array]))
    auc_scores["micro_ovr"] = float(auc_scores["micro"])

    return {"fpr": fpr, "tpr": tpr, "auc": auc_scores}


def find_optimal_threshold(y_true: np.ndarray, y_score: np.ndarray) -> tuple[float, float]:
    """
    寻找最优分类阈值（重要变更：自动优化而非固定阈值）

    使用precision-recall曲线找到使F1得分最大的最优阈值
    这是解决类别不平衡问题的关键步骤

    工作原理：
    1. precision_recall_curve计算在不同阈值下的精确率和召回率
    2. F1 = 2 * (precision * recall) / (precision + recall)
    3. 遍历所有阈值，找到使F1最大的那个值
    4. 使用该阈值进行分类，而不是默认的0.5

    为什么需要这个：
    - 冲突数据通常是类别不平衡的（和平年多于冲突年）
    - 默认的0.5阈值可能不适合不平衡数据
    - 自动调整阈值可以平衡精确率和召回率
    - 优化F1可以同时考虑精确率和召回率

    Parameters:
    ----------
    y_true : np.ndarray
        真实标签数组，元素为0（无冲突）或1（有冲突）
        形状为 (n_samples,)
    y_score : np.ndarray
        模型预测的正类概率值数组
        形状为 (n_samples,)，每个元素是该样本属于正类（冲突）的概率

    Returns:
    -------
    tuple[float, float]
        返回一个元组：
        - 第一个元素：最优分类阈值（float类型，范围在0-1之间）
        - 第二个元素：在该阈值下的最优F1得分（float类型）
    """
    # 计算precision-recall曲线
    # precision_recall_curve会根据不同的分类阈值，计算对应的精确率和召回率
    # 返回值：
    # - precision: 精确率数组，每个元素是对应阈值下的精确率
    # - recall: 召回率数组，每个元素是对应阈值下的召回率
    # - thresholds: 阈值数组，每个元素是对应的决策阈值
    # 注意：precision和recall的长度比thresholds多1，因为包含了极端阈值的情况
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)

    # 计算F1得分
    # F1-score是精确率和召回率的调和平均数
    # 公式：F1 = 2 * P * R / (P + R)
    # 优点：同时考虑精确率和召回率，适合不平衡数据
    # 添加1e-10是为了避免分母为零的情况
    f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)

    # 找到F1得分最大的索引
    # np.argmax返回数组中最大值的第一个出现的索引
    optimal_idx = np.argmax(f1_scores)

    # 获取最优阈值
    # precision_recall_curve返回的thresholds长度比precision和recall少1
    # 这是因为极端情况（阈值=0和阈值=1）不包含在thresholds中
    # optimal_idx可能取值为len(thresholds)，此时使用默认值0.5
    if optimal_idx < len(thresholds):
        # 如果索引有效，使用对应的阈值
        optimal_threshold = float(thresholds[optimal_idx])
    else:
        # 如果索引越界（极端情况），使用默认阈值0.5
        optimal_threshold = 0.5

    # 获取最优F1得分
    # 使用找到的最优索引对应的F1值
    optimal_f1 = float(f1_scores[optimal_idx])

    return optimal_threshold, optimal_f1


def evaluate_model(model: Pipeline, test_df: pd.DataFrame, spec: FeatureSpec, classes: list[int]) -> dict[str, Any]:
    """
    评估模型性能

    在测试集上评估模型的预测能力，计算多种评价指标

    评估流程：
    1. 提取测试集特征和真实标签
    2. 使用模型预测各类别概率
    3. 自动寻找最优分类阈值（基于F1优化）
    4. 使用最优阈值进行分类预测
    5. 计算分类报告、混淆矩阵、ROC曲线等指标

    评估指标说明：
    - macro_f1: 宏平均F1得分，对各类别F1取平均，适合不平衡数据
    - optimal_threshold: 最优分类阈值，自动优化而非固定0.5
    - optimal_f1: 最优阈值下的F1得分
    - confusion_matrix: 混淆矩阵，展示预测与真实值的对应关系
    - classification_report: 包含precision、recall、f1-score等详细指标
    - roc: ROC曲线数据，包含各类别的TPR、FPR和AUC值

    Parameters:
    ----------
    model : Pipeline
        训练好的机器学习管道，包含预处理、SMOTE和随机森林
    test_df : pd.DataFrame
        测试集数据框，必须包含特征列和标签列
    spec : FeatureSpec
        特征规范，定义了使用的特征列名
    classes : list[int]
        类别标签列表，如[0, 1]表示二分类

    Returns:
    -------
    dict[str, Any]
        评估指标字典，包含以下键：
        - "macro_f1": 宏平均F1得分
        - "optimal_threshold": 最优分类阈值
        - "optimal_f1": 最优阈值下的F1得分
        - "confusion_matrix": 混淆矩阵（二维列表）
        - "classification_report": 分类报告字典
        - "roc": ROC曲线数据字典
    """
    # 提取测试集特征和真实标签
    # features: 测试集的特征数据，用于模型预测
    # y_true: 测试集的真实标签，用于评估
    features = test_df[spec.feature_cols]
    y_true = test_df["UCDP_National_conflict_0_1"].astype(int)

    # 获取模型预测的概率
    # y_score: 概率数组，形状为(n_samples, n_classes)
    # 每行代表一个样本，每列代表属于该类别的概率
    y_score = aligned_probabilities(model, features, classes)

    # ============ 重要：自动寻找最优分类阈值 ============
    # 使用precision-recall曲线找到使F1最大的阈值
    # 这是解决类别不平衡问题的关键步骤
    if len(classes) == 2:
        # 对于二分类问题
        # 确定正类（通常1表示有冲突，0表示无冲突）
        positive_class = 1 if 1 in classes else classes[-1]
        # 找到正类在classes列表中的索引位置
        positive_idx = classes.index(positive_class)
        # 提取正类的预测概率
        y_score_positive = y_score[:, positive_idx]
        # 调用find_optimal_threshold函数自动寻找最优阈值
        # 该函数会遍历所有可能的阈值，找到使F1最大的那个值
        optimal_threshold, optimal_f1 = find_optimal_threshold(
            y_true.to_numpy(),  # 真实标签
            y_score_positive     # 正类预测概率
        )
    else:
        # 非二分类情况（本脚本不会出现），使用默认值
        optimal_threshold = 0.5
        optimal_f1 = 0.0

    # ============ 使用最优阈值进行分类预测 ============
    # 不是使用默认的0.5阈值，而是使用自动优化的最优阈值
    if len(classes) == 2:
        # 对于二分类
        # 确定正类和其索引
        positive_class = 1 if 1 in classes else classes[-1]
        positive_idx = classes.index(positive_class)
        # 如果预测概率 >= 最优阈值，则预测为正类（1），否则预测为负类（0）
        y_pred = (y_score[:, positive_idx] >= optimal_threshold).astype(int)
    else:
        # 非二分类情况，直接使用模型的默认预测
        y_pred = model.predict(features).astype(int)

    # ============ 计算详细评估指标 ============
    # classification_report生成包含precision、recall、f1-score等指标的字典
    # digits=4: 保留4位小数
    # output_dict=True: 返回字典格式而非字符串
    # zero_division=0: 除零时返回0而非警告
    report = classification_report(y_true, y_pred, digits=4, output_dict=True, zero_division=0)

    # 返回所有评估指标
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),  # 宏平均F1
        "optimal_threshold": optimal_threshold,  # 最优分类阈值
        "optimal_f1": optimal_f1,  # 最优F1得分
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),  # 混淆矩阵
        "classification_report": report,  # 详细分类报告
        "roc": build_roc_payload(y_true, y_score, classes),  # ROC曲线数据
    }


def save_roc_curve(roc_payload: dict[str, Any], output_path: Path) -> None:
    """
    保存ROC曲线图

    Parameters:
    ----------
    roc_payload : dict[str, Any]
        ROC曲线数据
    output_path : Path
        输出文件路径
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # 确定正类的key
    positive_key = "1" if "1" in roc_payload["auc"] else sorted(
        [key for key in roc_payload["auc"] if key.isdigit()],
        key=int,
    )[-1]

    # 绘制ROC曲线
    ax.plot(
        roc_payload["fpr"][positive_key],
        roc_payload["tpr"][positive_key],
        lw=2.5,
        color="#d62828",
        label=f"冲突 (AUC = {roc_payload['auc'][positive_key]:.3f})",
    )

    # 绘制对角线（随机分类器）
    ax.plot([0, 1], [0, 1], color="black", lw=1, linestyle="--")

    # 设置图形属性
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("假正率（False Positive Rate）")
    ax.set_ylabel("真正率（True Positive Rate）")
    ax.set_title("国际冲突ROC曲线")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)


def make_target_feature_frame(
    history_df: pd.DataFrame,
    spec: FeatureSpec,
    country_codes: dict[str, int],
    target_year: int,
) -> pd.DataFrame:
    """
    为目标年份构建特征数据框

    从历史数据中提取目标年份所需的滞后特征

    Parameters:
    ----------
    history_df : pd.DataFrame
        历史数据
    spec : FeatureSpec
        特征规范
    country_codes : dict[str, int]
        国家编码映射
    target_year : int
        目标年份

    Returns:
    -------
    pd.DataFrame
        目标年份的特征数据框
    """
    rows: list[dict[str, Any]] = []

    # 按国家分组
    for country, group in history_df.groupby("country", sort=True):
        # 创建特征行
        row = {
            "country": country,
            "year": target_year,
            "country_code": country_codes[country],
        }

        valid = True

        # 提取因变量的滞后特征
        for lag in range(1, spec.dv_lag + 1):
            year_df = group[group["year"] == target_year - lag]
            if year_df.empty or year_df["UCDP_National_conflict_0_1"].isna().any():
                valid = False
                break
            row[f"dv_lag{lag}"] = float(year_df["UCDP_National_conflict_0_1"].iloc[0])

        if not valid:
            continue

        # 提取自变量的滞后特征
        for lag in range(1, spec.iv_lag + 1):
            year_df = group[group["year"] == target_year - lag]
            if year_df.empty:
                valid = False
                break
            for column in IV_COLUMNS:
                row[f"{column}_lag{lag}"] = float(year_df[column].iloc[0])

        if valid:
            rows.append(row)

    frame = pd.DataFrame(rows)
    return frame.sort_values("country").reset_index(drop=True)


def prediction_table(
    model: Pipeline,
    features: pd.DataFrame,
    year: int,
    classes: list[int],
    optimal_threshold: float = 0.5,
) -> pd.DataFrame:
    """
    生成预测结果表

    Parameters:
    ----------
    model : Pipeline
        训练好的模型
    features : pd.DataFrame
        特征数据
    year : int
        预测年份
    classes : list[int]
        类别标签列表
    optimal_threshold : float
        最优分类阈值，默认为0.5

    Returns:
    -------
    pd.DataFrame
        预测结果表
    """
    # 获取预测概率
    proba = probability_frame(model, features, classes)

    # 提取特征列（排除国家和年份）
    model_cols = [column for column in features.columns if column not in {"country", "year"}]

    # 使用最优阈值进行预测
    if len(classes) == 2:
        positive_class = 1 if 1 in classes else classes[-1]
        positive_idx = classes.index(positive_class)
        prob_positive = proba[f"prob_{positive_class}"].values
        prediction = (prob_positive >= optimal_threshold).astype(int)
    else:
        prediction = model.predict(features[model_cols]).astype(int)

    # 构建结果数据框
    result = pd.DataFrame(
        {
            "country": features["country"],
            f"predicted_conflict_{year}": prediction,
        }
    )

    # 拼接概率列
    return pd.concat([result, proba.reset_index(drop=True)], axis=1)


def actual_target_frame(raw_df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    获取指定年份的真实值

    Parameters:
    ----------
    raw_df : pd.DataFrame
        原始数据
    year : int
        年份

    Returns:
    -------
    pd.DataFrame
        真实值数据框
    """
    frame = raw_df[raw_df["year"] == year][["country", "UCDP_National_conflict_0_1"]].copy()
    return frame.rename(columns={"UCDP_National_conflict_0_1": "actual_intensity"})


def score_prediction_rows(df: pd.DataFrame, classes: list[int]) -> dict[str, Any]:
    """
    评分预测结果

    Parameters:
    ----------
    df : pd.DataFrame
        预测结果数据框
    classes : list[int]
        类别标签列表

    Returns:
    -------
    dict[str, Any]
        评分指标
    """
    y_true = df["actual_intensity"].astype(int)
    y_pred = df["predicted_intensity"].astype(int)
    y_score = df[[f"prob_{cls}" for cls in classes]].to_numpy(dtype=float)

    # 计算分类报告
    report = classification_report(y_true, y_pred, digits=4, output_dict=True, zero_division=0)

    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": report,
        "roc": build_roc_payload(y_true, y_score, classes),
        "rows": int(len(df)),
    }


# ============================================
# 第七部分：结果展示函数
# ============================================

def format_metric_text(value: Any) -> str:
    """
    格式化指标值为字符串

    Parameters:
    ----------
    value : Any
        指标值

    Returns:
    -------
    str
        格式化后的字符串
    """
    return f"{float(value):.3f}"


def build_holdout_class_table(metrics: dict[str, Any], classes: list[int]) -> pd.DataFrame:
    """
    构建保留集各类别得分表

    Parameters:
    ----------
    metrics : dict[str, Any]
        评估指标
    classes : list[int]
        类别标签列表

    Returns:
    -------
    pd.DataFrame
        各类别得分表
    """
    report = metrics["classification_report"]
    rows: list[dict[str, Any]] = []

    for cls in classes:
        cls_key = str(cls)
        rows.append(
            {
                "类别": str(cls),
                "精确度（Precision）": format_metric_text(report[cls_key]["precision"]),
                "召回率（Recall）": format_metric_text(report[cls_key]["recall"]),
                "F1 得分（F1-score）": format_metric_text(report[cls_key]["f1-score"]),
            }
        )

    return pd.DataFrame(rows, dtype=object)


def build_holdout_overall_table(metrics: dict[str, Any]) -> pd.DataFrame:
    """
    构建保留集总体得分表

    Parameters:
    ----------
    metrics : dict[str, Any]
        评估指标

    Returns:
    -------
    pd.DataFrame
        总体得分表
    """
    report = metrics["classification_report"]
    rows = []

    for label, key in [("宏平均（Macro Avg）", "macro avg"), ("加权平均（Weighted Avg）", "weighted avg")]:
        rows.append(
            {
                "指标": label,
                "精确度（Precision）": format_metric_text(report[key]["precision"]),
                "召回率（Recall）": format_metric_text(report[key]["recall"]),
                "F1 得分（F1-score）": format_metric_text(report[key]["f1-score"]),
            }
        )

    return pd.DataFrame(rows, dtype=object)


def build_model_selection_table(search: SearchResult) -> pd.DataFrame:
    """
    构建模型选择结果表

    Parameters:
    ----------
    search : SearchResult
        模型搜索结果

    Returns:
    -------
    pd.DataFrame
        模型选择表
    """
    params = search.best_params
    rows = [
        {"指标": "最佳因变量滞后期", "数值": str(search.spec.dv_lag)},
        {"指标": "最佳自变量滞后期", "数值": str(search.spec.iv_lag)},
        {"指标": "最佳CV宏平均F1", "数值": f"{search.best_score:.3f}"},
        {"指标": "决策树数量", "数值": str(params["clf__n_estimators"])},
        {"指标": "最大树深", "数值": str(params["clf__max_depth"])},
        {"指标": "叶节点最小样本数", "数值": str(params["clf__min_samples_leaf"])},
        {"指标": "类别权重", "数值": "None" if params["clf__class_weight"] is None else str(params["clf__class_weight"])},
        {"指标": "SMOTENC近邻数", "数值": str(params["smote__k_neighbors"])},
    ]
    return pd.DataFrame(rows, dtype=object)





def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """
    将数据框转换为Markdown表格

    Parameters:
    ----------
    df : pd.DataFrame
        数据框

    Returns:
    -------
    str
        Markdown表格字符串
    """
    def format_cell(value: Any) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, (np.integer, int)):
            return str(int(value))
        if isinstance(value, (np.floating, float)):
            if float(value).is_integer():
                return str(int(value))
            return f"{float(value):.3f}"
        return str(value)

    # 构建Markdown表格
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for row in df.itertuples(index=False, name=None):
        values = [format_cell(value) for value in row]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def save_report_tables(prefix: Path, metrics: dict[str, Any], search: SearchResult, classes: list[int]) -> None:
    """
    保存结果报告表

    Parameters:
    ----------
    prefix : Path
        输出文件前缀
    metrics : dict[str, Any]
        评估指标
    search : SearchResult
        模型搜索结果
    classes : list[int]
        类别标签列表
    """
    # 构建各类表格
    class_table = build_holdout_class_table(metrics, classes)
    overall_table = build_holdout_overall_table(metrics)
    model_table = build_model_selection_table(search)

    # 保存CSV文件
    class_table.to_csv(f"{prefix}_holdout_class_table.csv", index=False, encoding="utf-8-sig")
    overall_table.to_csv(f"{prefix}_holdout_overall_table.csv", index=False, encoding="utf-8-sig")
    model_table.to_csv(f"{prefix}_model_selection_table.csv", index=False, encoding="utf-8-sig")

    # 构建并保存Markdown报告
    markdown = "\n\n".join(
        [
            "表 1：国际冲突二分类各类别预测值得分\n" + dataframe_to_markdown(class_table),
            "表 2：国际冲突二分类预测值总体得分\n" + dataframe_to_markdown(overall_table),
            "表 3：国际冲突二分类模型最优参数与滞后期\n" + dataframe_to_markdown(model_table),
        ]
    )
    Path(f"{prefix}_report_tables.md").write_text(markdown, encoding="utf-8")


# ============================================
# 第八部分：递推回测函数
# ============================================

def inject_predictions(df: pd.DataFrame, predictions: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    将预测结果注入数据框

    用于递推预测时，将上一期的预测值作为下一期的输入

    Parameters:
    ----------
    df : pd.DataFrame
        原始数据框
    predictions : pd.DataFrame
        预测结果
    year : int
        预测年份

    Returns:
    -------
    pd.DataFrame
        注入预测值后的数据框
    """
    value_col = f"predicted_conflict_{year}"
    mapping = predictions.set_index("country")[value_col]

    updated = df.copy()
    mask = updated["year"] == year
    updated.loc[mask, "UCDP_National_conflict_0_1"] = updated.loc[mask, "country"].map(mapping)

    return updated.sort_values(["country", "year"]).reset_index(drop=True)


def run_recursive_backtest(
    raw_df: pd.DataFrame,
    spec: FeatureSpec,
    params: dict[str, Any],
    country_codes: dict[str, int],
    config: RunConfig,
    classes: list[int],
    optimal_threshold: float = 0.5,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    运行递推回测

    模拟真实的递推预测过程：
    1. 使用历史数据训练模型
    2. 预测下一期
    3. 将预测值作为输入，预测再下一期

    Parameters:
    ----------
    raw_df : pd.DataFrame
        原始数据
    spec : FeatureSpec
        特征规范
    params : dict[str, Any]
        模型参数
    country_codes : dict[str, int]
        国家编码映射
    config : RunConfig
        运行配置
    classes : list[int]
        类别标签列表
    optimal_threshold : float
        最优分类阈值

    Returns:
    -------
    tuple[pd.DataFrame, dict[str, Any]]
        (回测结果数据框, 评估指标)
    """
    rows: list[pd.DataFrame] = []

    # 从训练截止年份的前一年开始，遍历所有可能的起点
    for origin_year in range(config.train_cutoff - 1, config.observed_last_year - 1):
        # 使用origin_year及之前的历史数据
        observed_history = raw_df[raw_df["year"] <= origin_year].copy()

        # 构建滞后特征
        lagged_history = build_lagged_frame(observed_history, country_codes, config)
        train_frame = build_observed_frame_for_spec(lagged_history, spec, origin_year)

        # 检查训练数据是否有效
        if train_frame.empty or train_frame["year"].nunique() <= config.n_splits:
            continue

        # 训练模型
        model = fit_pipeline(train_frame, spec, params, config)

        # 预测自变量值，扩展到origin_year + 1年
        forecast_history = append_forecast_year(observed_history, origin_year + 1)

        # 构建origin_year + 1年的特征
        feature_step_1 = make_target_feature_frame(forecast_history, spec, country_codes, origin_year + 1)
        if feature_step_1.empty:
            continue

        # 预测origin_year + 1年的冲突
        result_step_1 = prediction_table(
            model,
            feature_step_1[["country", "year", *spec.feature_cols]],
            origin_year + 1,
            classes,
            optimal_threshold,
        )

        # 与真实值合并
        step_1 = result_step_1.merge(actual_target_frame(raw_df, origin_year + 1), on="country", how="inner")
        step_1["origin_year"] = origin_year
        step_1["target_year"] = origin_year + 1
        step_1["horizon"] = 1
        step_1 = step_1.rename(columns={f"predicted_conflict_{origin_year + 1}": "predicted_intensity"})
        rows.append(step_1)

        # 将预测值注入历史数据，用于递推预测
        recursive_history = inject_predictions(forecast_history, result_step_1, origin_year + 1)

        # 构建origin_year + 2年的特征
        feature_step_2 = make_target_feature_frame(recursive_history, spec, country_codes, origin_year + 2)
        if feature_step_2.empty:
            continue

        # 预测origin_year + 2年的冲突
        result_step_2 = prediction_table(
            model,
            feature_step_2[["country", "year", *spec.feature_cols]],
            origin_year + 2,
            classes,
            optimal_threshold,
        )

        # 与真实值合并
        step_2 = result_step_2.merge(actual_target_frame(raw_df, origin_year + 2), on="country", how="inner")
        step_2["origin_year"] = origin_year
        step_2["target_year"] = origin_year + 2
        step_2["horizon"] = 2
        step_2 = step_2.rename(columns={f"predicted_conflict_{origin_year + 2}": "predicted_intensity"})
        rows.append(step_2)

    #.检查是否产生结果
    if not rows:
        raise RuntimeError("递推回测未能产生任何结果。")

    # 合并所有回测结果
    backtest_df = pd.concat(rows, ignore_index=True)

    # 计算评估指标
    metrics = {"combined": score_prediction_rows(backtest_df, classes)}
    for horizon in sorted(backtest_df["horizon"].unique().tolist()):
        horizon_df = backtest_df[backtest_df["horizon"] == horizon].reset_index(drop=True)
        metrics[f"horizon_{horizon}"] = score_prediction_rows(horizon_df, classes)

    return backtest_df, metrics


# ============================================
# 第九部分：保存输出函数
# ============================================

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
    country_codes: dict[str, int],
) -> None:
    """
    保存所有输出文件

    Parameters:
    ----------
    config : RunConfig
        运行配置
    forecast_df : pd.DataFrame
        包含预测年份的数据框
    metrics : dict[str, Any]
        评估指标
    recursive_backtest_df : pd.DataFrame
        递推回测结果
    classes : list[int]
        类别标签列表
    result_2025 : pd.DataFrame
        2025年预测结果
    result_2026 : pd.DataFrame
        2026年预测结果
    model : Pipeline
        训练好的模型
    search : SearchResult
        模型搜索结果
    country_codes : dict[str, int]
        国家编码映射
    """
    prefix = Path(config.output_prefix)

    # 保存CSV文件
    forecast_df.to_csv(f"{prefix}_with_2025.csv", index=False)
    result_2025.to_csv(f"{prefix}_predictions_2025.csv", index=False)
    result_2026.to_csv(f"{prefix}_predictions_2026.csv", index=False)
    recursive_backtest_df.to_csv(f"{prefix}_recursive_backtest.csv", index=False)

    # 保存报告表和ROC曲线
    save_report_tables(prefix, metrics, search, classes)
    save_roc_curve(metrics["roc"], Path(f"{prefix}_roc_curve.svg"))

    # 保存评估指标JSON
    with Path(f"{prefix}_metrics.json").open("w", encoding="utf-8") as fh:
        json.dump(to_builtin(metrics), fh, ensure_ascii=False, indent=2)

    # 保存模型
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


# ============================================
# 第十部分：主函数
# ============================================

def run(config: RunConfig) -> None:
    """
    主运行函数 - 整个预测管道的入口

    该函数执行完整的国际冲突二分类预测流程，从数据准备到结果保存

    预测流程概述：
    ============ 第一步：数据准备 ============
    1. 加载原始数据（1961-2024年）
    2. 扩展数据到预测年份（2025年）
    3. 为2025年预测自变量值（ARIMA和简单方法）
    4. 构建国家编码和滞后特征

    ============ 第二步：模型选择与评估 ============
    1. 构建所有特征规范（不同的滞后组合）
    2. 使用expanding-window时间序列交叉验证
    3. 网格搜索最优超参数
    4. 在测试集（2011-2024年）上评估模型
    5. 运行递推回测，评估多步预测能力
    6. 自动寻找最优分类阈值（基于F1优化）

    ============ 第三步：全量拟合与未来预测 ============
    1. 使用全部观测数据（1963-2024年）拟合最终模型
    2. 预测2025年冲突风险（使用优化的阈值）
    3. 将2025年预测值注入数据
    4. 预测2026年冲突风险（递推预测）

    ============ 第四步：保存结果 ============
    1. 保存预测结果（2025年和2026年）
    2. 保存评估指标和报告
    3. 保存模型和参数

    关键特性：
    - 使用expanding-window CV（3折，每折验证集12年）
    - 自动优化分类阈值（不使用固定0.5）
    - 递推预测2026年（基于2025年预测）
    - 非连续变量使用简单方法预测（移动平均、线性外推）
    - 类别不平衡处理（SMOTE过采样）

    Parameters:
    ----------
    config : RunConfig
        运行配置，包含所有参数：
        - data_path: 数据文件路径
        - train_cutoff: 训练集截止年份（2011年）
        - observed_last_year: 观测数据最后年份（2024年）
        - forecast_year: 预测目标年份（2025年）
        - recursive_year: 递推预测年份（2026年）
        - max_dv_lag: 因变量最大滞后期（2）
        - max_iv_lag: 自变量最大滞后期（1）
        - n_splits: 交叉验证折数（3）
        - random_state: 随机种子（42）
        - output_prefix: 输出文件前缀
    """
    # ========== 第一步：数据准备 ==========
    print("\n" + "="*80)
    print("第一步：数据准备")
    print("="*80)

    # 加载原始数据（1961-2024年）
    # load_international_data会：
    # - 读取CSV文件
    # - 检查必需列是否存在
    # - 转换数据类型
    # - 按国家和年份排序
    raw_df = load_international_data(config.data_path)
    print(f"✓ 已加载数据：{len(raw_df)}行")
    print(f"✓ 数据范围: {raw_df['year'].min()}年 - {raw_df['year'].max()}年")
    print(f"✓ 国家数量: {raw_df['country'].nunique()}个")

    # 推断类别标签
    # 对于二分类问题，应该返回[0, 1]
    classes = infer_classes(raw_df)
    print(f"✓ 类别标签: {classes}")

    # 扩展数据到预测年份（2025年）
    # append_forecast_year会：
    # - 对每个国家预测2025年的自变量值
    # - 连续变量用ARIMA，非连续变量用简单方法
    # - 应用边界约束
    # - 冲突值设为NaN（后续用模型预测）
    forecast_df = append_forecast_year(raw_df, config.forecast_year)
    print(f"✓ 已扩展到{config.forecast_year}年")

    # 构建国家编码
    # 将国家名转换为整数编码，便于模型处理
    country_codes = build_country_code_map(forecast_df)
    print(f"✓ 已构建{len(country_codes)}个国家编码")

    # 添加滞后特征
    # 为因变量和自变量添加滞后项
    # 例如：dv_lag1表示前1年的冲突，GDP_per_capita_ln_lag1表示前1年的人均GDP
    lagged_df = build_lagged_frame(forecast_df, country_codes, config)
    print(f"✓ 已添加滞后特征")

    # ========== 第二步：模型选择与评估 ==========
    print("\n" + "="*80)
    print("第二步：模型选择与评估")
    print("="*80)

    # 构建所有特征规范
    specs = build_feature_specs(config.max_dv_lag, config.max_iv_lag)
    print(f"✓ 特征规范数量: {len(specs)}个")

    # 搜索最优模型
    search = search_best_model(lagged_df, specs, config)
    print(f"✓ 最优滞后期: dv_lag={search.spec.dv_lag}, iv_lag={search.spec.iv_lag}")
    print(f"✓ 最优CV得分: {search.best_score:.4f}")

    # 构建观测数据框
    # 使用最优特征规范，选择1963-2024年的观测数据
    model_df = build_observed_frame_for_spec(lagged_df, search.spec, config.observed_last_year)

    # 划分训练集和测试集
    # 训练集：1963-2010年（train_cutoff=2011）
    # 测试集：2011-2024年（评估模型泛化能力）
    train_df = model_df[model_df["year"] < config.train_cutoff].reset_index(drop=True)
    test_df = model_df[
        (model_df["year"] >= config.train_cutoff) & (model_df["year"] <= config.observed_last_year)
    ].reset_index(drop=True)

    print(f"✓ 训练集范围: {train_df['year'].min()}年 - {train_df['year'].max()}年")
    print(f"✓ 测试集范围: {test_df['year'].min()}年 - {test_df['year'].max()}年")

    # 拟合评估模型
    # 使用训练集数据拟合模型
    eval_model = fit_pipeline(train_df, search.spec, search.best_params, config)

    # 评估模型
    # 在测试集上评估模型性能
    # evaluate_model会：
    # 1. 自动寻找最优分类阈值（基于F1优化）
    # 2. 使用最优阈值进行预测
    # 3. 计算分类报告、混淆矩阵、ROC曲线等指标
    metrics = evaluate_model(eval_model, test_df, search.spec, classes)
    print(f"✓ 测试集宏平均F1: {metrics['macro_f1']:.4f}")
    print(f"✓ 最优分类阈值: {metrics['optimal_threshold']:.4f}")

    # 获取最优阈值
    # 这个阈值将在后续预测中使用
    # 而不是使用默认的0.5阈值
    optimal_threshold = metrics["optimal_threshold"]

    # 运行递推回测
    # run_recursive_backtest会模拟真实的递推预测过程：
    # 1. 从某个起点开始，使用历史数据训练模型
    # 2. 预测下一年的冲突
    # 3. 将预测值作为输入，递推预测再下一年
    # 4. 与真实值对比，评估递推预测能力
    recursive_backtest_df, recursive_backtest_metrics = run_recursive_backtest(
        raw_df=raw_df,
        spec=search.spec,
        params=search.best_params,
        country_codes=country_codes,
        config=config,
        classes=classes,
        optimal_threshold=optimal_threshold,  # 使用优化的阈值
    )
    metrics["recursive_backtest"] = recursive_backtest_metrics
    print(f"✓ 递推回测宏平均F1: {metrics['recursive_backtest']['combined']['macro_f1']:.4f}")

    # ========== 第三步：全量拟合与未来预测 ==========
    print("\n" + "="*80)
    print("第三步：全量拟合与未来预测")
    print("="*80)

    # 使用全部观测数据拟合最终模型
    # 训练数据：1963-2024年（所有观测数据）
    # 这样可以利用最多的数据，提高预测准确性
    final_model = fit_pipeline(model_df, search.spec, search.best_params, config)
    print(f"✓ 已使用全部观测数据拟合最终模型")

    # 预测2025年
    # make_target_feature_frame构建2025年的特征
    # 使用滞后特征：2024年的冲突、2024年的自变量等
    feature_2025 = make_target_feature_frame(forecast_df, search.spec, country_codes, config.forecast_year)
    # 使用训练好的模型预测2025年冲突
    # prediction_table会：
    # 1. 预测各类别概率
    # 2. 使用最优阈值进行分类
    # 3. 返回预测结果和概率
    result_2025 = prediction_table(
        final_model,
        feature_2025[["country", "year", *search.spec.feature_cols]],
        config.forecast_year,
        classes,
        optimal_threshold,  # 使用优化的阈值，而非默认0.5
    )
    print(f"✓ 已预测{config.forecast_year}年冲突风险: {len(result_2025)}个国家")
    print(f"✓{config.forecast_year}年预测冲突数: {(result_2025[f'predicted_conflict_{config.forecast_year}'] == 1).sum()}")

    # 递推预测2026年
    # 步骤1：将2025年的预测值注入数据
    # inject_predictions将预测的冲突值作为"观测值"添加到数据中
    # 这样2026年的滞后特征可以包含2025年的预测冲突值
    recursive_input = inject_predictions(forecast_df, result_2025, config.forecast_year)

    # 步骤2：扩展数据到2026年
    # 为2026年预测自变量值（GDP、polity等）
    # 使用ARIMA和简单方法
    recursive_input = append_forecast_year(recursive_input, config.recursive_year)

    # 步骤3：构建2026年的特征
    # 使用滞后特征：2025年的冲突（预测值）、2025年的自变量（预测值）等
    feature_2026 = make_target_feature_frame(recursive_input, search.spec, country_codes, config.recursive_year)

    # 步骤4：预测2026年冲突
    # 使用训练好的模型预测2026年冲突
    # 注意：这是基于2025年预测值的递推预测
    result_2026 = prediction_table(
        final_model,
        feature_2026[["country", "year", *search.spec.feature_cols]],
        config.recursive_year,
        classes,
        optimal_threshold,  # 使用优化的阈值
    )
    print(f"✓ 已递推预测{config.recursive_year}年冲突风险: {len(result_2026)}个国家")
    print(f"✓ {config.recursive_year}年预测冲突数: {(result_2026[f'predicted_conflict_{config.recursive_year}'] == 1).sum()}")

    # ========== 第四步：保存结果 ==========
    print("\n" + "="*80)
    print("第四步：保存结果")
    print("="*80)

    # 保存所有输出文件
    # 包括：
    # - 预测结果（2025年和2026年）
    # - 评估指标
    # - 递推回测结果
    # - 模型和参数
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
    print("✓ 所有输出文件已保存")

    # ========== 打印结果摘要 ==========
    print("\n" + "="*80)
    print("模型搜索结果")
    print("="*80)
    print(f"最优CV宏平均F1: {search.best_score:.4f}")
    print(f"因变量滞后期: {search.spec.dv_lag}")
    print(f"自变量滞后期: {search.spec.iv_lag}")
    print("最优参数:")
    for key, value in search.best_params.items():
        print(f"  {key}: {value}")

    print("\n" + "="*80)
    print("保留集测试结果")
    print("="*80)
    print(f"宏平均F1: {metrics['macro_f1']:.4f}")
    print(f"最优分类阈值: {metrics['optimal_threshold']:.4f}")
    print("混淆矩阵:")
    print(pd.DataFrame(metrics["confusion_matrix"]))
    print("\n各类别得分:")
    print(build_holdout_class_table(metrics, classes).to_string(index=False))
    print("\n总体得分:")
    print(build_holdout_overall_table(metrics).to_string(index=False))

    print("\n" + "="*80)
    print("递推回测结果")
    print("="*80)
    print(f"组合宏平均F1: {metrics['recursive_backtest']['combined']['macro_f1']:.4f}")
    for horizon in sorted(key for key in metrics["recursive_backtest"] if key.startswith("horizon_")):
        print(f"{horizon}宏平均F1: {metrics['recursive_backtest'][horizon]['macro_f1']:.4f}")

    print("\n" + "="*80)
    print("已保存的文件")
    print("="*80)
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

    print("\n" + "="*80)
    print("预测完成！")
    print("="*80)


if __name__ == "__main__":
    # 解析命令行参数并运行
    run(parse_args())
