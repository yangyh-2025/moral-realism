#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际冲突二分类预测管道 - International Conflict Binary Prediction Pipeline

这个脚本实现了一个完整的机器学习管道，用于预测国家间冲突的发生（二分类问题）。
主要功能包括：
1. 数据加载和预处理
2. 时间序列特征工程（ARIMA预测）
3. 滞后特征生成（用于时间序列预测）
4. 模型训练和优化（随机森林 + SMOTE处理不平衡数据）
5. 模型评估和验证（交叉验证、ROC曲线、F1分数）
6. 未来冲突预测（递归预测）

使用的技术：
- 随机森林分类器（Random Forest）：用于二分类预测
- SMOTE-NC：用于处理不平衡数据集（包含数值和分类特征）
- ARIMA：用于时间序列预测特征
- 交叉验证：用于模型选择和评估
"""

from __future__ import annotations

# 标准库导入
import argparse
import json
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# 第三方库导入
import joblib
import matplotlib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTENC  # SMOTE-NC：处理不平衡数据的算法
from imblearn.pipeline import Pipeline  # 用于构建机器学习工作流
from sklearn.compose import ColumnTransformer  # 用于特征预处理
from sklearn.ensemble import RandomForestClassifier  # 随机森林分类器
from sklearn.metrics import (
    auc, classification_report, confusion_matrix, f1_score, make_scorer,
    roc_curve
)
from sklearn.model_selection import GridSearchCV  # 网格搜索优化模型参数
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # 数据预处理工具
from statsmodels.tsa.arima.model import ARIMA  # ARIMA时间序列预测模型

# 配置matplotlib使用非交互式后端，避免GUI问题
matplotlib.use("Agg")

from matplotlib import pyplot as plt

# 导入阈值优化工具
from threshold_optimizer import find_optimal_threshold_f1_binary

# 导入简单的日志式进度监控模块
try:
    from simple_progress import SimpleProgressTracker, task_context
    TRACKER_AVAILABLE = True
    ProgressTracker = SimpleProgressTracker
except ImportError:
    TRACKER_AVAILABLE = False
    ProgressTracker = None
    task_context = None

# 全局进度跟踪器
tracker = None


"""
全局常量定义
"""

# 自变量（解释变量）列表 - 用于预测国际冲突的特征
IV_COLUMNS = [
    "polity",                    # 政体分数（-10到10，民主到专制）
    "GDP_per_capita_ln",         # 人均GDP对数
    "GDP_growth",                # GDP增长率
    "population_density_ln",     # 人口密度对数
    "trade",                     # 贸易指标
    "military_expenditure_final",# 军事支出
    "national_capacity",         # 国家能力
]

# polity是离散整数 [-10, 10] - 使用最后观测值，不需要ARIMA预测
# military_expenditure_final和national_capacity范围[0,1] - ARIMA预测后需要裁剪
ARIMA_COLUMNS = [
    "GDP_per_capita_ln",
    "GDP_growth",
    "population_density_ln",
    "trade",
    "military_expenditure_final",
    "national_capacity",
]

# 需要整数化的列
INTEGER_COLUMNS = ["polity"]

# 各特征的取值范围限制（用于数据清洗和预测值裁剪）
VALUE_BOUNDS = {
    "polity": (-10.0, 10.0),            # 政体分数范围
    "GDP_per_capita_ln": (0.0, None),   # 人均GDP对数必须非负
    "GDP_growth": (None, None),         # GDP增长率无限制
    "population_density_ln": (0.0, None),# 人口密度对数必须非负
    "trade": (0.0, None),               # 贸易指标必须非负
    "military_expenditure_final": (0.0, 1.0),  # 军事支出0-1
    "national_capacity": (0.0, 1.0),    # 国家能力0-1
}

# ARIMA模型的可能参数组合（用于网格搜索）
# ARIMA(p,d,q)：p=自回归项数，d=差分阶数，q=移动平均项数
ARIMA_ORDERS = [
    (0, 1, 0),  # 简单差分（无自回归或移动平均）
    (1, 1, 0),  # 1阶自回归+差分
    (0, 1, 1),  # 差分+1阶移动平均
    (1, 1, 1),  # 1阶自回归+差分+1阶移动平均
    (2, 1, 0),  # 2阶自回归+差分
    (0, 1, 2),  # 差分+2阶移动平均
    (2, 1, 1),  # 2阶自回归+差分+1阶移动平均
]

# 模型超参数搜索网格 - 用于GridSearchCV优化
PARAM_GRID = {
    "smote__k_neighbors": [3, 5],              # SMOTE-NC的邻居数量
    "clf__n_estimators": [200],                # 随机森林的决策树数量
    "clf__max_depth": [6, 10, None],           # 决策树最大深度
    "clf__min_samples_leaf": [1, 3],           # 叶节点最小样本数
    "clf__class_weight": [None, "balanced_subsample"],  # 类别权重
}


@dataclass(frozen=True)
class RunConfig:
    """运行配置参数类 - 包含所有可配置的参数

    这个类使用Python的dataclass装饰器，创建一个不可变（frozen=True）的配置对象，
    确保在运行过程中参数不会被意外修改，从而保证实验的可重现性。
    """
    data_path: Path              # 数据文件路径（Excel格式）
    train_cutoff: int = 2011     # 训练集截止年份：2011年之前的数据用于训练
    observed_last_year: int = 2024  # 最后观测年：数据的最后可用年份
    forecast_year: int = 2025    # 待预测年份：主要预测目标年份
    recursive_year: int = 2026   # 递归预测年份：基于2025年预测结果再预测2026年
    max_dv_lag: int = 2          # 因变量最大滞后期：最多使用前2年的冲突数据作为特征
    max_iv_lag: int = 1          # 自变量最大滞后期：最多使用前1年的经济/政治数据作为特征
    n_splits: int = 3            # 交叉验证折数：将训练集分成3份进行交叉验证
    random_state: int = 42       # 随机种子：确保每次运行结果完全一致
    output_prefix: str = "international_binary_clean"  # 输出文件前缀：所有输出文件的统一前缀


@dataclass(frozen=True)
class FeatureSpec:
    """特征规格类 - 定义用于模型训练的特征集合"""
    dv_lag: int                  # 因变量滞后期
    iv_lag: int                  # 自变量滞后期
    numeric_cols: list[str]      # 数值特征列
    feature_cols: list[str]      # 所有特征列（包含数值和分类）


@dataclass(frozen=True)
class SearchResult:
    """模型搜索结果类 - 包含最佳模型的参数和性能"""
    spec: FeatureSpec            # 最佳特征规格
    best_params: dict[str, Any]  # 最佳模型参数
    best_score: float            # 最佳模型分数


def parse_args() -> RunConfig:
    """解析命令行参数并返回配置对象"""
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="国际冲突二分类预测管道 - 包含无泄漏交叉验证和递归预测"
    )
    parser.add_argument(
        "--data-path",
        default=str(script_dir / "data.xlsx"),
        help="国际冲突数据的Excel文件路径",
    )
    parser.add_argument(
        "--output-prefix",
        default=str(script_dir / "international_binary_clean"),
        help="输出文件前缀（保存在当前目录）",
    )
    args = parser.parse_args()
    return RunConfig(data_path=Path(args.data_path), output_prefix=args.output_prefix)


def clip_value(name: str, value: float) -> float:
    """
    将值限制在预定义的范围内（用于数据清洗和预测值裁剪）

    参数:
        name: 特征名称
        value: 需要裁剪的值

    返回:
        裁剪后的值
    """
    lower, upper = VALUE_BOUNDS[name]
    # 如果有下限，确保值不小于下限
    if lower is not None:
        value = max(lower, value)
    # 如果有上限，确保值不大于上限
    if upper is not None:
        value = min(upper, value)
    return float(value)


def load_international_data(path: Path) -> pd.DataFrame:
    """
    加载并预处理国际冲突数据

    数据来源说明：
    - 数据文件是Excel格式（.xlsx）
    - 文件应包含至少以下列：
      - ccode: 国家代码（唯一标识）
      - Statename: 国家名称
      - year: 年份
      - UCDP_National_conflict_0_1: 冲突强度（0或1）
      - IV_COLUMNS中的7个自变量（GDP、政体、贸易等）

    参数:
        path: Excel文件的路径（Path对象）

    返回:
        预处理后的DataFrame，包含以下额外列：
        - country: 国家代码（字符串格式）
        - intensity_level: 冲突强度（整数格式，与UCDP_National_conflict_0_1相同）

    处理步骤:
        1. 加载Excel数据
        2. 验证所需列是否全部存在
        3. 重排列顺序以符合约定
        4. 数据类型转换（确保数据格式正确）
        5. 按国家和年份排序，方便后续处理
    """
    # 步骤1：读取Excel文件
    df = pd.read_excel(path)

    # 步骤2：验证数据完整性
    # 检查是否包含所有必要的列
    required = {"ccode", "Statename", "UCDP_National_conflict_0_1", *IV_COLUMNS}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"缺少列: {missing}")

    # 步骤3：重排列顺序
    # 按固定顺序排列列，方便读取和调试
    ordered = ["ccode", "Statename", "year", "UCDP_National_conflict_0_1", *IV_COLUMNS]
    df = df[ordered].copy()

    # 步骤4：数据类型转换
    df["country"] = df["ccode"].astype(str)  # 国家代码转换为字符串
    df["Statename"] = df["Statename"].astype(str)  # 国家名称确保是字符串
    df["year"] = df["year"].astype(int)  # 年份转换为整数
    df["intensity_level"] = df["UCDP_National_conflict_0_1"].astype(int)  # 冲突强度转换为整数

    # 步骤5：排序
    # 按国家代码和年份排序，确保时间序列的连续性
    return df.sort_values(["country", "year"]).reset_index(drop=True)


def infer_classes(df: pd.DataFrame) -> list[int]:
    """
    从数据中推断冲突强度等级的类别（二分类）

    参数:
        df: 包含intensity_level列的DataFrame

    返回:
        排序后的类别列表（整数）
    """
    return sorted(df["intensity_level"].dropna().astype(int).unique().tolist())


def forecast_one_step(years: pd.Series, values: pd.Series) -> float:
    """
    使用ARIMA模型进行单步时间序列预测（预测下一年的值）

    什么是ARIMA模型？
    - ARIMA（AutoRegressive Integrated Moving Average）是一种经典的时间序列预测模型
    - ARIMA(p,d,q)有三个参数：
      p = 自回归项数（AR）：用过去多少期的值来预测现在
      d = 差分阶数（I）：需要做几次差分才能让数据平稳
      q = 移动平均项数（MA）：用过去多少期的预测误差来预测现在

    参数:
        years: 年份序列（pandas Series，如[2000, 2001, 2002, ...]）
        values: 对应的值序列（如GDP、政体分数等，与年份一一对应）

    返回:
        预测值（浮点数），如果无法预测则返回NaN

    工作流程:
        1. 数据清洗：删除缺失值
        2. 边界情况处理：数据太少或值恒定时直接返回最后一个值
        3. 模型选择：尝试多种ARIMA参数组合，选择AIC最小的模型
        4. 预测：使用最佳模型预测下一期值
    """
    # 步骤1：数据清洗 - 创建数据框并删除缺失值
    # 将年份和值配对，删除任一列有缺失值的行
    frame = pd.DataFrame({"year": years, "value": values}).dropna()

    # 如果没有有效数据，返回NaN（Not a Number，表示缺失值）
    if frame.empty:
        return np.nan  # 无数据时返回NaN

    # 步骤2：创建时间序列对象
    # pandas的Series对象，索引是年份（PeriodIndex表示年度周期）
    series = pd.Series(
        frame["value"].to_numpy(dtype=float),  # 值转换为浮点数数组
        index=pd.PeriodIndex(frame["year"].astype(int), freq="Y"),  # 索引是年份，频率为年（Y）
    )

    # 步骤3：处理边界情况
    # 如果数据点太少（少于4年）或者所有值都相同（nunique() == 1）
    # 就不进行复杂的ARIMA预测，直接返回最后一个观测值
    if len(series) < 4 or series.nunique() == 1:
        return float(series.iloc[-1])  # 返回最后一个值

    # 步骤4：尝试多种ARIMA参数，选择最佳模型
    best_aic = np.inf  # 初始化最佳AIC值为无穷大（AIC越小越好）
    best_value = float(series.iloc[-1])  # 默认预测值为最后一个观测值

    # 什么是AIC？
    # AIC（Akaike Information Criterion）是模型选择准则
    # 它平衡了模型的拟合质量和模型复杂度
    # AIC越小，表示模型在拟合数据和避免过拟合之间的平衡越好

    # 尝试预定义的所有ARIMA参数组合
    for order in ARIMA_ORDERS:
        try:
            # 忽略ARIMA拟合过程中的警告（很多时候是收敛警告，不影响结果）
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # 拟合ARIMA模型
                fitted = ARIMA(
                    series,
                    order=order,  # ARIMA(p,d,q)参数
                    trend="n",  # "n"表示不包含趋势项（无常数项、无线性趋势）
                    enforce_stationarity=False,  # 不强制要求数据平稳（放宽条件）
                    enforce_invertibility=False,  # 不强制要求模型可逆（放宽条件）
                ).fit()

            # 如果AIC值不是有限值（比如NaN或无穷大），或者不比当前最佳AIC更小，就跳过
            if not np.isfinite(fitted.aic) or fitted.aic >= best_aic:
                continue

            # 使用拟合好的模型预测下一期（steps=1表示预测1步）
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                forecast = fitted.forecast(steps=1)

            # 更新最佳结果：记录当前最佳AIC和对应的预测值
            best_aic = float(fitted.aic)
            best_value = float(forecast.iloc[0])
        except Exception:
            # 如果某个参数组合出错（比如模型无法收敛），捕获异常并继续尝试下一个
            continue  # 捕获并忽略所有异常

    # 返回最佳模型的预测值
    return best_value


def append_forecast_year(df: pd.DataFrame, target_year: int, progress_tracker=None) -> pd.DataFrame:
    """
    向数据中添加预测年份的数据行

    参数:
        df: 原始数据框
        target_year: 待预测的年份
        progress_tracker: 可选的进度跟踪器

    返回:
        包含预测年份的完整数据框

    功能:
        1. 为每个国家添加目标年份的数据
        2. 非连续变量使用最后观测值
        3. 连续变量使用ARIMA进行预测
    """
    rows: list[dict[str, Any]] = []

    # 获取国家列表用于进度跟踪
    countries = list(df.groupby("country", sort=True))
    total_countries = len(countries)

    for idx, (country, group) in enumerate(countries, 1):
        # 创建基础行
        row = {
            "country": country,
            "year": target_year,
            "intensity_level": np.nan,
        }
        # 保留国家名称信息
        if "Statename" in group.columns:
            row["Statename"] = group["Statename"].iloc[-1]
        if "ccode" in group.columns:
            row["ccode"] = group["ccode"].iloc[-1]

        # polity是离散变量，使用最后观测值
        row["polity"] = float(group["polity"].iloc[-1])

        # 处理ARIMA列（连续变量）
        arima_success = True
        for column in (col for col in ARIMA_COLUMNS if col in group.columns):
            try:
                value = forecast_one_step(group["year"], group[column])
                row[column] = clip_value(column, value)
            except Exception as e:
                # ARIMA预测失败，使用最后观测值
                if progress_tracker and arima_success:
                    ccode = group["ccode"].iloc[-1] if "ccode" in group.columns else "N/A"
                    progress_tracker.set_task_detail(
                        f"  警告: {country} (ccode={ccode})\n"
                        f"  ARIMA预测失败，使用最后观测值\n"
                        f"  错误: {type(e).__name__}"
                    )
                    arima_success = False
                row[column] = float(group[column].iloc[-1])

        # 更新进度
        if progress_tracker:
            ccode = row.get("ccode", "N/A")
            progress_tracker.update_stage_progress(idx / total_countries)
            progress_tracker.set_task_detail(
                f"处理国家: {country} (ccode={ccode})\n"
                f"已完成: {idx}/{total_countries} 国家"
            )

        rows.append(row)

    forecast_df = pd.DataFrame(rows)
    combined = pd.concat([df, forecast_df], ignore_index=True)
    return combined.sort_values(["country", "year"]).reset_index(drop=True)


def build_country_code_map(df: pd.DataFrame) -> dict[str, int]:
    """
    创建国家名称到数字编码的映射字典（用于独热编码）

    参数:
        df: 包含国家名称的DataFrame

    返回:
        {国家名称: 数字编码}的字典
    """
    countries = sorted(df["country"].unique().tolist())
    return {country: idx for idx, country in enumerate(countries)}


def add_lag_features(df: pd.DataFrame, max_dv_lag: int, max_iv_lag: int) -> pd.DataFrame:
    """
    为数据添加滞后特征（Lag Features）- 时间序列预测的核心技术

    什么是滞后特征？
    - 在时间序列预测中，我们用过去的数据来预测未来
    - "滞后"就是指"前几期"的数据
    - 例如：要预测2025年的冲突，我们可以用2024年（滞后1期）、2023年（滞后2期）的数据作为特征

    举例说明：
    假设我们有某国的数据：
    - 2023年：冲突=0, GDP=1000
    - 2024年：冲突=1, GDP=1100
    - 2025年：冲突=?, GDP=?

    当max_dv_lag=2、max_iv_lag=1时：
    - 2025年的dv_lag1 = 2024年的冲突 = 1
    - 2025年的dv_lag2 = 2023年的冲突 = 0
    - 2025年的GDP_lag1 = 2024年的GDP = 1100

    为什么要按国家分组（groupby("country")）？
    - 每个国家是独立的时间序列
    - 中国的历史数据不能用来预测美国，反之亦然
    - 所以我们要对每个国家单独计算滞后特征

    参数:
        df: 原始数据框
        max_dv_lag: 因变量（dv = dependent variable，即冲突强度）的最大滞后期数
        max_iv_lag: 自变量（iv = independent variable，即GDP、政体等）的最大滞后期数

    返回:
        包含滞后特征的数据框（新增列名格式：dv_lag1、dv_lag2、GDP_per_capita_ln_lag1 等）
    """
    # 创建数据的副本，避免修改原始数据
    lagged = df.copy()

    # 步骤1：添加因变量（冲突强度）的滞后特征
    # dv = dependent variable（因变量，我们要预测的变量）
    for lag in range(1, max_dv_lag + 1):
        # 对每个国家，将intensity_level列向下移动lag个位置
        # shift(lag)：将数据向下移动，前lag行变成NaN
        # groupby("country")：确保每个国家的滞后特征只来自自己的历史
        lagged[f"dv_lag{lag}"] = lagged.groupby("country")["intensity_level"].shift(lag)

    # 步骤2：添加自变量的滞后特征
    # iv = independent variable（自变量，用来预测的特征）
    for lag in range(1, max_iv_lag + 1):
        for column in IV_COLUMNS:
            # 对每个国家，将该自变量列向下移动lag个位置
            lagged[f"{column}_lag{lag}"] = lagged.groupby("country")[column].shift(lag)

    # 返回包含所有滞后特征的数据框
    return lagged


def build_feature_specs(max_dv_lag: int, max_iv_lag: int) -> list[FeatureSpec]:
    """
    构建所有可能的特征规格组合（用于网格搜索最佳配置）

    参数:
        max_dv_lag: 因变量最大滞后期数
        max_iv_lag: 自变量最大滞后期数

    返回:
        FeatureSpec对象列表，包含所有可能的滞后期组合
    """
    specs: list[FeatureSpec] = []
    for dv_lag in range(1, max_dv_lag + 1):
        for iv_lag in range(1, max_iv_lag + 1):
            numeric_cols = [
                *(f"{column}_lag{lag}" for column in IV_COLUMNS for lag in range(1, iv_lag + 1)),
                *(f"dv_lag{lag}" for lag in range(1, dv_lag + 1)),
            ]
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
    构建包含滞后特征的完整数据框

    参数:
        df: 原始数据框
        country_codes: 国家编码映射
        config: 运行配置

    返回:
        包含滞后特征和国家编码的数据框
    """
    lagged = add_lag_features(df, config.max_dv_lag, config.max_iv_lag)
    lagged["country_code"] = lagged["country"].map(country_codes).astype(int)
    return lagged.sort_values(["year", "country"]).reset_index(drop=True)


def build_observed_frame_for_spec(
    lagged_df: pd.DataFrame,
    spec: FeatureSpec,
    last_year: int,
) -> pd.DataFrame:
    """
    构建用于模型训练的观测数据框

    参数:
        lagged_df: 包含滞后特征的数据框
        spec: 特征规格
        last_year: 最后观测年份

    返回:
        清洗后的观测数据框
    """
    frame = lagged_df[lagged_df["year"] <= last_year].copy()
    frame = frame.dropna(subset=["intensity_level", *spec.feature_cols]).copy()
    frame["intensity_level"] = frame["intensity_level"].astype(int)
    return frame.sort_values(["year", "country"]).reset_index(drop=True)


def to_builtin(value: Any) -> Any:
    """
    将NumPy类型转换为Python内置类型（用于JSON序列化）

    参数:
        value: 需要转换的值

    返回:
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
    创建基于年份的时间序列交叉验证分割（Time Series Cross Validation）

    概念说明：
    时间序列交叉验证与普通交叉验证的重要区别：
    - 普通K折交叉验证：随机打乱所有数据，分成K份，轮流用1份做验证，K-1份做训练
    - 时间序列交叉验证：不能打乱数据！因为时间有先后顺序，未来的数据不能用于训练过去的模型

    这里使用的是 expanding-window（扩展窗口）方法，也叫"滚动窗口"或"前向验证"：
    - 训练集从最早年份开始，不断扩展（包含更多历史数据）
    - 验证集始终在训练集之后，模拟真实的预测场景
    - 这样可以避免"数据泄露"（Data Leakage）：不会用未来信息预测过去

    举例说明（假设数据是1990-2020年）：
    - Fold 1: 训练1990-1997，验证1998-2004
    - Fold 2: 训练1990-2004，验证2005-2012
    - Fold 3: 训练1990-2012，验证2013-2020

    参数:
        years: 年份序列（pandas Series，每行一个年份）
        n_splits: 交叉验证折数（当前实现只支持3折）

    返回:
        分割索引列表 [(训练集索引数组, 验证集索引数组), ...]
        每个元素是一个元组，包含训练集和验证集在原始数据中的行索引
    """
    # 步骤1：获取数据中的年份范围
    unique_years = np.sort(years.unique())  # 所有不重复的年份，按升序排列
    min_year = int(unique_years.min())      # 最早年份
    max_year = int(unique_years.max())      # 最晚年份

    # 步骤2：验证数据是否足够进行交叉验证
    # 需要至少 2*n_splits + 1 年的数据才能保证每折都有合理的训练和验证数据
    if len(unique_years) <= n_splits * 2:
        raise ValueError(f"数据年份不足，至少需要 {n_splits * 2 + 1} 年才能进行 {n_splits} 折交叉验证")

    # 当前实现只支持3折交叉验证（硬编码逻辑）
    if n_splits != 3:
        raise ValueError(f"当前实现仅支持 n_splits=3，收到 {n_splits}")

    # 步骤3：计算时间段长度
    # 将数据分为4个大致相等的时间段，每段约占总年数的1/4
    total_years = max_year - min_year + 1  # 总年数（包括首尾）
    segment_size = total_years // 4         # 每段的年数（整数除法）

    # 步骤4：定义3折交叉验证的年份范围
    # 格式：(训练开始年, 训练结束年, 验证开始年, 验证结束年)
    cv_splits = [
        # 第一折: 用第1段训练，第2段验证
        (min_year, min_year + segment_size - 1, min_year + segment_size, min_year + 2 * segment_size - 1),
        # 第二折: 用前2段训练，第3段验证
        (min_year, min_year + 2 * segment_size - 1, min_year + 2 * segment_size, min_year + 3 * segment_size - 1),
        # 第三折: 用前3段训练，第4段（剩余所有年）验证
        (min_year, min_year + 3 * segment_size - 1, min_year + 3 * segment_size, max_year),
    ]

    # 步骤5：将年份范围转换为实际的数据索引
    splits: list[tuple[np.ndarray, np.ndarray]] = []
    for train_start, train_end, valid_start, valid_end in cv_splits[:n_splits]:
        # 确保年份范围不会超出实际数据范围
        train_start = max(train_start, min_year)
        train_end = min(train_end, max_year)
        valid_start = max(valid_start, min_year)
        valid_end = min(valid_end, max_year)

        # 如果验证集起始年大于结束年，说明这折没有验证数据，跳过
        if valid_start > valid_end:
            continue

        # 使用布尔掩码选择训练集和验证集的行索引
        # years >= train_start 且 years <= train_end → 训练集
        # years >= valid_start 且 years <= valid_end → 验证集
        train_mask = (years >= train_start) & (years <= train_end)
        valid_mask = (years >= valid_start) & (years <= valid_end)

        # 获取对应的行索引（numpy数组格式）
        train_idx = years.index[train_mask].to_numpy()
        valid_idx = years.index[valid_mask].to_numpy()

        # 确保验证集不为空
        if len(valid_idx) == 0:
            continue

        # 添加到结果列表
        splits.append((train_idx, valid_idx))

    # 最后检查：确保生成了指定数量的折
    if len(splits) != n_splits:
        raise ValueError(f"无法生成 {n_splits} 折交叉验证，实际生成了 {len(splits)} 折")

    return splits


def build_pipeline(numeric_cols: list[str], random_state: int) -> Pipeline:
    """
    构建完整的机器学习管道

    管道工作流程（Pipeline Architecture）：
    1. 预处理（SMOTE前）：标准化数值特征，保持国家编码不变
    2. SMOTE-NC：处理不平衡数据，生成合成样本
    3. 后处理（SMOTE后）：对国家编码进行独热编码
    4. 随机森林分类器：使用处理后的特征进行预测

    为什么要这样设计管道？
    - SMOTE-NC需要原始的分类特征（国家编码）来生成合理的合成样本
    - 如果先独热编码，国家编码会变成多个二进制列，SMOTE-NC无法有效利用
    - 因此我们分两步处理：先保持国家编码用于SMOTE，之后再独热编码用于模型训练

    概念说明：
    - 数据不平衡（Class Imbalance）：某些类别的样本远少于其他类别
      例如：没有冲突的国家（0类）远多于有冲突的国家（1类），这会导致模型偏向于预测"无冲突"
    - SMOTE-NC（Synthetic Minority Over-sampling Technique for Nominal and Continuous）：
      用于处理包含数值和分类特征的不平衡数据
      通过在少数类样本之间插值生成合成样本来平衡各类别的数量
    - 独热编码（One-Hot Encoding）：将分类变量转换为二进制向量，使机器学习模型能够处理类别数据
    - 标准化（Standardization）：将数值特征缩放到均值为0、标准差为1的范围，提高模型训练稳定性

    参数:
        numeric_cols: 数值特征列列表（如GDP、政体分数等滞后特征）
        random_state: 随机种子（保证每次运行结果一致）

    返回:
        完整的Pipeline对象（可以直接调用fit和predict方法）
    """
    # 第一步：SMOTE前的预处理
    # - 数值特征：标准化（StandardScaler），使各特征尺度一致
    # - 国家编码：直接通过（passthrough），保留原始格式供SMOTE使用
    pre_smote = ColumnTransformer(
        [
            ("num", StandardScaler(), numeric_cols),  # 数值特征标准化
            ("country", "passthrough", ["country_code"]),  # 国家编码保持不变
        ],
        verbose_feature_names_out=False,  # 不生成冗长的特征名称
    )

    # 第二步：SMOTE后的处理
    # - 数值特征：已经处理好了，直接通过
    # - 国家编码：现在进行独热编码（OneHotEncoder），因为随机森林需要数值输入
    #   注意：此时国家编码在第 len(numeric_cols) 列的位置
    post_smote = ColumnTransformer(
        [
            ("num", "passthrough", list(range(len(numeric_cols)))),  # 数值特征直接通过
            ("country", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [len(numeric_cols)]),  # 国家编码独热编码
        ],
        verbose_feature_names_out=False,
    )

    # 组装完整的机器学习管道
    # Pipeline按顺序执行各个步骤：
    # 1. pre_smote: 预处理
    # 2. smote: 生成合成样本平衡数据
    # 3. post_smote: 独热编码国家
    # 4. clf: 随机森林分类器训练
    return Pipeline(
        steps=[
            ("pre_smote", pre_smote),  # 步骤1：SMOTE前预处理
            (
                "smote",
                SMOTENC(categorical_features=[len(numeric_cols)], random_state=random_state),  # 步骤2：SMOTE-NC处理
            ),
            ("post_smote", post_smote),  # 步骤3：SMOTE后处理（独热编码）
            ("clf", RandomForestClassifier(random_state=random_state, n_jobs=-1)),  # 步骤4：随机森林分类器（n_jobs=-1使用所有CPU核心）
        ]
    )


def search_best_model(lagged_df: pd.DataFrame, specs: list[FeatureSpec], config: RunConfig, progress_tracker=None) -> SearchResult:
    """
    使用网格搜索（Grid Search）寻找最佳模型配置

    什么是网格搜索？
    - 超参数（Hyperparameters）：在训练前手动设置的参数，不是模型从数据中学到的
      例如：随机森林中树的数量、树的最大深度、SMOTE的邻居数量等
    - 网格搜索：系统地尝试所有超参数组合，像在网格上遍历每个点一样
    - 对于每种组合，使用交叉验证评估模型性能
    - 最终选择性能最好的那一组参数

    为什么需要网格搜索？
    - 不同的超参数组合会导致模型性能差异很大
    - 通过系统地搜索，可以找到相对最优的参数组合
    - 避免手动调参的主观性和随机性

    概念说明：
    - 宏平均F1分数（Macro F1 Score）：先对每个类别分别计算F1分数，然后取平均
      这样可以平衡各类别的性能，不会被样本多的类别主导

    参数:
        lagged_df: 包含滞后特征的数据框
        specs: 特征规格列表（不同的滞后期组合）
        config: 运行配置
        progress_tracker: 可选的进度跟踪器

    返回:
        包含最佳特征规格、最佳参数和最佳分数的SearchResult对象
    """
    # 步骤1：定义评分指标
    # 使用宏平均F1分数作为模型性能的评价标准
    # make_scorer将f1_score函数转换为scikit-learn可用的评分器对象
    scorer = make_scorer(f1_score, average="macro")

    # 初始化最佳结果为None
    best_result: SearchResult | None = None

    # 步骤2：遍历所有特征规格（不同的滞后期组合）
    total_specs = len(specs)  # 总共有多少种特征规格
    for idx, spec in enumerate(specs, 1):
        # 更新进度显示
        if progress_tracker:
            progress_tracker.update_stage_progress(idx / total_specs)
            progress_tracker.set_task_detail(
                f"测试特征规格: dv_lag={spec.dv_lag}, iv_lag={spec.iv_lag}\n"
                f"进度: {idx}/{total_specs} 特征规格\n"
                f"参数空间: {len(PARAM_GRID)}种RF参数 × {config.n_splits}折CV = {len(PARAM_GRID) * config.n_splits}次训练"
            )

        # 步骤3：准备训练数据
        # 构建观测数据框（包含特征和标签，且没有缺失值）
        observed_df = build_observed_frame_for_spec(lagged_df, spec, config.observed_last_year)

        # 只使用训练截止年份之前的数据进行训练和验证
        train_df = observed_df[observed_df["year"] < config.train_cutoff].reset_index(drop=True)

        # 如果训练数据为空，或者年份不足以进行交叉验证，跳过这个特征规格
        if train_df.empty or train_df["year"].nunique() <= config.n_splits:
            continue

        # 创建时间序列交叉验证的分割
        cv = year_block_splits(train_df["year"], config.n_splits)

        # 步骤4：设置网格搜索
        search = GridSearchCV(
            estimator=build_pipeline(spec.numeric_cols, config.random_state),  # 要优化的模型管道
            param_grid=PARAM_GRID,  # 超参数网格（定义要搜索的参数范围）
            scoring=scorer,  # 评分指标
            cv=cv,  # 交叉验证分割方式
            n_jobs=-1,  # 使用所有CPU核心并行计算
            refit=True,  # 找到最佳参数后，用全部数据重新训练一个最终模型
        )

        # 步骤5：执行网格搜索
        # 这会尝试PARAM_GRID中定义的所有超参数组合
        search.fit(train_df[spec.feature_cols], train_df["intensity_level"])

        # 步骤6：记录当前特征规格的最佳结果
        result = SearchResult(
            spec=spec,  # 当前的特征规格
            best_params=search.best_params_,  # 这个特征规格下的最佳超参数
            best_score=float(search.best_score_),  # 这个特征规格下的最佳分数
        )

        # 步骤7：更新全局最佳结果
        # 如果还没有最佳结果，或者当前结果比之前的最佳结果更好
        if best_result is None or result.best_score > best_result.best_score:
            best_result = result

    # 如果所有特征规格都失败了（没有产生有效结果），抛出异常
    if best_result is None:
        raise RuntimeError("Grid search did not produce a result.")

    # 打印最佳结果摘要
    if progress_tracker:
        progress_tracker.set_task_detail(
            f"最佳配置: dv_lag={best_result.spec.dv_lag}, iv_lag={best_result.spec.iv_lag}\n"
            f"最佳 CV F1 分数: {best_result.best_score:.4f}"
        )

    # 返回全局最佳结果
    return best_result


def fit_pipeline(df: pd.DataFrame, spec: FeatureSpec, params: dict[str, Any], config: RunConfig) -> Pipeline:
    """
    使用指定参数训练模型管道

    参数:
        df: 训练数据
        spec: 特征规格
        params: 模型参数
        config: 运行配置

    返回:
        训练好的Pipeline对象
    """
    model = build_pipeline(spec.numeric_cols, config.random_state)
    model.set_params(**params)
    model.fit(df[spec.feature_cols], df["intensity_level"])
    return model


def probability_frame(model: Pipeline, features: pd.DataFrame, classes: list[int]) -> pd.DataFrame:
    """
    获取模型的预测概率，并整理成数据框格式

    概念说明：
    预测概率（Predicted Probability）：模型认为样本属于每个类别的概率
    对于二分类问题，0类通常表示无冲突，1类表示有冲突

    参数:
        model: 训练好的模型
        features: 特征数据
        classes: 类别列表

    返回:
        包含各类别预测概率的数据框
    """
    proba = model.predict_proba(features)
    frame = pd.DataFrame(index=features.index)
    for cls in classes:
        frame[f"prob_{cls}"] = 0.0
    for idx, cls in enumerate(model.named_steps["clf"].classes_):
        frame[f"prob_{int(cls)}"] = proba[:, idx]
    return frame[[f"prob_{cls}" for cls in classes]]


def aligned_probabilities(model: Pipeline, features: pd.DataFrame, classes: list[int]) -> np.ndarray:
    """
    获取对齐的预测概率数组（用于ROC计算）

    参数:
        model: 训练好的模型
        features: 特征数据
        classes: 类别列表

    返回:
        对齐的预测概率数组
    """
    proba = model.predict_proba(features)
    class_to_pos = {cls: idx for idx, cls in enumerate(classes)}
    aligned = np.zeros((len(features), len(classes)), dtype=float)
    for idx, cls in enumerate(model.named_steps["clf"].classes_):
        aligned[:, class_to_pos[int(cls)]] = proba[:, idx]
    return aligned


def build_roc_payload(y_true: pd.Series, y_score: np.ndarray, classes: list[int]) -> dict[str, Any]:
    """
    构建ROC曲线数据（二分类专用）

    参数:
        y_true: 真实标签
        y_score: 预测概率
        classes: 类别列表

    返回:
        包含FPR、TPR和AUC的字典
    """
    class_array = np.array(classes, dtype=int)
    y_bin = np.column_stack([(y_true.to_numpy(dtype=int) == cls).astype(int) for cls in class_array])

    fpr: dict[str, list[float]] = {}
    tpr: dict[str, list[float]] = {}
    auc_scores: dict[str, float] = {}

    for idx, class_id in enumerate(class_array):
        x_fpr, x_tpr, _ = roc_curve(y_bin[:, idx], y_score[:, idx])
        fpr[str(class_id)] = x_fpr.tolist()
        tpr[str(class_id)] = x_tpr.tolist()
        auc_scores[str(class_id)] = float(auc(x_fpr, x_tpr))

    micro_fpr, micro_tpr, _ = roc_curve(y_bin.ravel(), y_score.ravel())
    fpr["micro"] = micro_fpr.tolist()
    tpr["micro"] = micro_tpr.tolist()
    auc_scores["micro"] = float(auc(micro_fpr, micro_tpr))

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


def evaluate_model(model: Pipeline, test_df: pd.DataFrame, spec: FeatureSpec, classes: list[int], threshold: float | None = None) -> dict[str, Any]:
    """
    在测试集上评估模型性能（二分类）

    概念说明：
    混淆矩阵（Confusion Matrix）：显示预测类别与真实类别的对应关系
    F1分数：精确率和召回率的调和平均，综合评价模型性能
    宏平均（Macro Average）：对每个类别分别计算指标，然后取平均
    加权平均（Weighted Average）：按类别样本数加权平均

    参数:
        model: 训练好的模型
        test_df: 测试数据
        spec: 特征规格
        classes: 类别列表
        threshold: 分类阈值，如果为None则自动计算最优阈值

    返回:
        包含各种评估指标的字典，包括最优阈值
    """
    features = test_df[spec.feature_cols]
    y_true = test_df["intensity_level"].astype(int)
    proba_array = model.predict_proba(features)
    class_1_index = list(model.named_steps["clf"].classes_).index(1)

    # 如果没有提供阈值，自动计算最优阈值
    if threshold is None:
        threshold, optimal_f1 = find_optimal_threshold_f1_binary(
            y_true=y_true.to_numpy(),
            y_proba=proba_array[:, class_1_index],
            class_positive=1,
            threshold_range=(0.01, 0.99),
            step=0.01,
        )

    # 使用计算出的阈值进行分类
    y_pred = (proba_array[:, class_1_index] >= threshold).astype(int)
    y_score = aligned_probabilities(model, features, classes)
    report = classification_report(y_true, y_pred, digits=4, output_dict=True, zero_division=0)
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": report,
        "roc": build_roc_payload(y_true, y_score, classes),
        "optimal_threshold": float(threshold),
    }


def save_roc_curve(roc_payload: dict[str, Any], output_path: Path) -> None:
    """
    保存ROC曲线为SVG文件（二分类专用）

    参数:
        roc_payload: 包含ROC数据的字典（由build_roc_payload返回）
        output_path: 输出文件路径

    返回:
        无
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    positive_key = "1" if "1" in roc_payload["auc"] else sorted(
        [key for key in roc_payload["auc"] if key.isdigit()],
        key=int,
    )[-1]
    ax.plot(
        roc_payload["fpr"][positive_key],
        roc_payload["tpr"][positive_key],
        lw=2.5,
        color="#d62828",
        label=f"Conflict (AUC = {roc_payload['auc'][positive_key]:.3f})",
    )
    ax.plot([0, 1], [0, 1], color="black", lw=1, linestyle="--")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("International Conflict ROC Curve")
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
    为目标年份创建特征数据框（用于生成预测输入）

    参数:
        history_df: 历史数据
        spec: 特征规格
        country_codes: 国家编码映射
        target_year: 目标年份

    返回:
        包含目标年份特征的数据框
    """
    rows: list[dict[str, Any]] = []
    for country, group in history_df.groupby("country", sort=True):
        row = {"country": country, "year": target_year, "country_code": country_codes[country]}
        valid = True

        for lag in range(1, spec.dv_lag + 1):
            year_df = group[group["year"] == target_year - lag]
            if year_df.empty or year_df["intensity_level"].isna().any():
                valid = False
                break
            row[f"dv_lag{lag}"] = float(year_df["intensity_level"].iloc[0])

        if not valid:
            continue

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


def prediction_table(model: Pipeline, features: pd.DataFrame, year: int, classes: list[int], threshold: float = 0.5) -> pd.DataFrame:
    """
    生成包含国家名称、预测类别和各类别概率的数据框

    参数:
        model: 训练好的模型
        features: 特征数据
        year: 预测年份（用于列名）
        classes: 类别列表
        threshold: 分类阈值（默认0.5，建议使用自动计算的最优阈值）

    返回:
        包含预测结果的数据框
    """
    proba = probability_frame(model, features, classes)
    model_cols = [column for column in features.columns if column not in {"country", "year"}]
    # 使用指定阈值进行分类（对于二分类问题，我们关注类别 1 的概率）
    proba_array = model.predict_proba(features[model_cols])
    # 找到类别 1 对应的索引
    class_1_index = list(model.named_steps["clf"].classes_).index(1)
    prediction = (proba_array[:, class_1_index] >= threshold).astype(int)
    result = pd.DataFrame(
        {
            "country": features["country"],
            f"predicted_conflict_{year}": prediction,
        }
    )
    return pd.concat([result, proba.reset_index(drop=True)], axis=1)


def actual_target_frame(raw_df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    从原始数据中提取目标年份的实际冲突强度数据

    参数:
        raw_df: 原始数据框
        year: 目标年份

    返回:
        包含国家和实际冲突强度的数据框
    """
    frame = raw_df[raw_df["year"] == year][["country", "intensity_level"]].copy()
    return frame.rename(columns={"intensity_level": "actual_intensity"})


def score_prediction_rows(df: pd.DataFrame, classes: list[int], threshold: float = 0.5) -> dict[str, Any]:
    """
    计算预测结果的评分（用于递归回测）

    参数:
        df: 包含实际值和预测值的数据框
        classes: 类别列表
        threshold: 分类阈值

    返回:
        包含各种评估指标的字典
    """
    y_true = df["actual_intensity"].astype(int)
    y_score = df[[f"prob_{cls}" for cls in classes]].to_numpy(dtype=float)

    # 使用预测概率重新应用阈值逻辑（确保与评估时一致）
    class_1_index = classes.index(1)
    y_pred = (y_score[:, class_1_index] >= threshold).astype(int)

    report = classification_report(y_true, y_pred, digits=4, output_dict=True, zero_division=0)
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": report,
        "roc": build_roc_payload(y_true, y_score, classes),
        "rows": int(len(df)),
        "optimal_threshold": float(threshold),
    }


def format_metric_text(value: Any) -> str:
    """格式化指标数值，保留3位小数"""
    return f"{float(value):.3f}"


def build_holdout_class_table(metrics: dict[str, Any], classes: list[int]) -> pd.DataFrame:
    """
    构建各类别的性能指标表格

    参数:
        metrics: 评估指标字典
        classes: 类别列表

    返回:
        包含各类别性能指标的数据框
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
    构建总体性能指标表格（宏平均和加权平均）

    参数:
        metrics: 评估指标字典

    返回:
        包含总体性能指标的数据框
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
    构建模型选择参数表格（包含最佳参数设置）

    参数:
        search: 搜索结果对象

    返回:
        包含模型选择参数的数据框
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
    """将数据框转换为Markdown表格格式"""
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
    保存评估报告表格为CSV和Markdown格式

    参数:
        prefix: 输出文件前缀
        metrics: 评估指标字典
        search: 搜索结果对象
        classes: 类别列表

    返回:
        无
    """
    class_table = build_holdout_class_table(metrics, classes)
    overall_table = build_holdout_overall_table(metrics)
    model_table = build_model_selection_table(search)

    class_table.to_csv(f"{prefix}_holdout_class_table.csv", index=False, encoding="utf-8-sig")
    overall_table.to_csv(f"{prefix}_holdout_overall_table.csv", index=False, encoding="utf-8-sig")
    model_table.to_csv(f"{prefix}_model_selection_table.csv", index=False, encoding="utf-8-sig")

    markdown = "\n\n".join(
        [
            "表 1：国际冲突二分类各类别预测值得分\n" + dataframe_to_markdown(class_table),
            "表 2：国际冲突二分类预测值总体得分\n" + dataframe_to_markdown(overall_table),
            "表 3：国际冲突二分类模型最优参数与滞后期\n" + dataframe_to_markdown(model_table),
        ]
    )
    Path(f"{prefix}_report_tables.md").write_text(markdown, encoding="utf-8")


def run_recursive_backtest(
    raw_df: pd.DataFrame,
    spec: FeatureSpec,
    params: dict[str, Any],
    country_codes: dict[str, int],
    config: RunConfig,
    classes: list[int],
    threshold: float = 0.5,
    progress_tracker=None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    运行递归回测（Recursive Backtest）

    为什么要做递归回测？
    在真实预测场景中，我们无法同时看到未来多年的数据。递归回测模拟了这种真实场景：
    - 先用历史数据训练模型
    - 预测下一年
    - 将预测结果作为特征，再预测下下一年
    - 这样可以评估模型在多期预测中的表现，而不是只看单期表现

    回测原理（以2020年为起点为例）：
    1. 使用1961-2020年数据训练模型
    2. 预测2021年冲突 → 结果A
    3. 将结果A作为特征，预测2022年冲突 → 结果B
    4. 用真实的2021-2022年数据验证结果A和B

    这与普通交叉验证不同，因为普通交叉验证假设可以同时看到未来所有数据。

    参数:
        raw_df: 原始数据
        spec: 特征规格
        params: 最佳模型参数
        country_codes: 国家编码映射
        config: 运行配置
        classes: 类别列表
        threshold: 分类阈值
        progress_tracker: 可选的进度跟踪器

    返回:
        (回测结果数据框, 评估指标字典)
    """
    # 用于存储所有回测结果的列表
    rows: list[pd.DataFrame] = []

    # 步骤1：确定回测的起始年份范围
    # origin_year 是每一轮回测的"当前年份"
    # 从 config.train_cutoff - 1 到 config.observed_last_year - 1
    # 因为需要至少有数据来训练和验证（预测1年和2年）
    origin_years = list(range(config.train_cutoff - 1, config.observed_last_year - 1))
    total_years = len(origin_years)  # 总共有多少轮回测

    # 步骤2：执行每一轮回测
    for idx, origin_year in enumerate(origin_years, 1):
        # 更新进度显示
        if progress_tracker:
            progress_tracker.update_stage_progress(idx / total_years)
            progress_tracker.set_task_detail(
                f"评估 origin_year={origin_year}\n"
                f"训练集: 1961-{origin_year}\n"
                f"测试集: {origin_year+1}-{origin_year+2}\n"
                f"已完成: {idx}/{total_years} 起始年份"
            )

        # 步骤2.1：获取当前origin_year的历史数据（用于训练）
        observed_history = raw_df[raw_df["year"] <= origin_year].copy()

        # 步骤2.2：准备训练数据（添加滞后特征）
        lagged_history = build_lagged_frame(observed_history, country_codes, config)
        train_frame = build_observed_frame_for_spec(lagged_history, spec, origin_year)

        # 如果训练数据为空或年份不足，跳过这一轮回测
        if train_frame.empty or train_frame["year"].nunique() <= config.n_splits:
            continue

        # 步骤2.3：训练模型
        model = fit_pipeline(train_frame, spec, params, config)

        # 步骤2.4：预测第1年（origin_year + 1）
        # 1. 为第1年生成ARIMA预测特征
        forecast_history = append_forecast_year(observed_history, origin_year + 1)

        # 2. 构建第1年的特征数据框
        feature_step_1 = make_target_feature_frame(forecast_history, spec, country_codes, origin_year + 1)
        if feature_step_1.empty:
            continue

        # 3. 使用模型进行预测
        result_step_1 = prediction_table(
            model,
            feature_step_1[["country", "year", *spec.feature_cols]],
            origin_year + 1,
            classes,
            threshold=threshold,
        )

        # 4. 将预测结果与真实值合并
        step_1 = result_step_1.merge(actual_target_frame(raw_df, origin_year + 1), on="country", how="inner")
        step_1["origin_year"] = origin_year  # 回测起始年份
        step_1["target_year"] = origin_year + 1  # 预测年份
        step_1["horizon"] = 1  # 预测 horizon（1年）
        step_1 = step_1.rename(columns={f"predicted_conflict_{origin_year + 1}": "predicted_intensity"})
        rows.append(step_1)

        # 步骤2.5：递归预测第2年（origin_year + 2）
        # 将第1年的预测结果注入到历史数据中，作为第2年的特征
        recursive_history = inject_predictions(forecast_history, result_step_1, origin_year + 1)

        # 构建第2年的特征数据框（使用第1年的预测值作为滞后特征）
        feature_step_2 = make_target_feature_frame(recursive_history, spec, country_codes, origin_year + 2)
        if feature_step_2.empty:
            continue

        # 使用同一模型进行预测
        result_step_2 = prediction_table(
            model,
            feature_step_2[["country", "year", *spec.feature_cols]],
            origin_year + 2,
            classes,
            threshold=threshold,
        )

        # 将预测结果与真实值合并
        step_2 = result_step_2.merge(actual_target_frame(raw_df, origin_year + 2), on="country", how="inner")
        step_2["origin_year"] = origin_year  # 回测起始年份
        step_2["target_year"] = origin_year + 2  # 预测年份
        step_2["horizon"] = 2  # 预测 horizon（2年）
        step_2 = step_2.rename(columns={f"predicted_conflict_{origin_year + 2}": "predicted_intensity"})
        rows.append(step_2)

    # 步骤3：处理回测结果
    if not rows:
        raise RuntimeError("Recursive backtest did not produce any rows.")

    # 合并所有回测结果
    backtest_df = pd.concat(rows, ignore_index=True)

    # 计算评估指标
    metrics = {"combined": score_prediction_rows(backtest_df, classes, threshold)}
    for horizon in sorted(backtest_df["horizon"].unique().tolist()):
        horizon_df = backtest_df[backtest_df["horizon"] == horizon].reset_index(drop=True)
        metrics[f"horizon_{horizon}"] = score_prediction_rows(horizon_df, classes, threshold)

    return backtest_df, metrics


def inject_predictions(df: pd.DataFrame, predictions: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    将预测结果注入到数据框中，用作递归预测的输入

    参数:
        df: 原始数据框
        predictions: 包含预测结果的数据框
        year: 预测年份

    返回:
        更新后的数据框（其中intensity_level被替换为预测值）
    """
    value_col = f"predicted_conflict_{year}"
    mapping = predictions.set_index("country")[value_col]
    updated = df.copy()
    mask = updated["year"] == year
    updated.loc[mask, "intensity_level"] = updated.loc[mask, "country"].map(mapping)
    return updated.sort_values(["country", "year"]).reset_index(drop=True)


def save_outputs(
    config: RunConfig,
    forecast_df: pd.DataFrame,
    metrics: dict[str, Any],
    recursive_backtest: pd.DataFrame,
    classes: list[int],
    result_forecast: pd.DataFrame,
    result_recursive: pd.DataFrame,
    model: Pipeline,
    search: SearchResult,
    country_codes: dict[str, int],
) -> None:
    """
    保存所有输出文件

    参数:
        config: 运行配置
        forecast_df: 包含预测年份的数据框
        metrics: 评估指标字典
        recursive_backtest: 递归回测结果
        classes: 类别列表
        result_forecast: 2025年预测结果
        result_recursive: 2026年递归预测结果
        model: 训练好的模型
        search: 搜索结果对象
        country_codes: 国家编码映射

    返回:
        无
    """
    prefix = Path(config.output_prefix)
    forecast_df.to_csv(f"{prefix}_with_2025.csv", index=False)
    result_forecast.to_csv(f"{prefix}_predictions_2025.csv", index=False)
    result_recursive.to_csv(f"{prefix}_predictions_2026.csv", index=False)
    recursive_backtest.to_csv(f"{prefix}_recursive_backtest.csv", index=False)
    save_report_tables(prefix, metrics, search, classes)
    save_roc_curve(metrics["roc"], Path(f"{prefix}_roc_curve.svg"))
    with Path(f"{prefix}_metrics.json").open("w", encoding="utf-8") as fh:
        json.dump(to_builtin(metrics), fh, ensure_ascii=False, indent=2)
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


def run(config: RunConfig) -> None:
    """
    主函数 - 协调整个国际冲突预测流程（中央指挥中心）

    这是整个脚本的"控制塔"，按照正确的顺序调用各个功能模块，
    完成从数据加载到最终预测的全部工作。

    完整工作流程图（从上到下执行）：

    ┌─────────────────────────────────────────────────────────────┐
    │ 阶段1: 数据准备阶段                                          │
    ├─────────────────────────────────────────────────────────────┤
    │ 1.1 加载Excel数据，验证数据完整性                            │
    │ 1.2 为2025年生成ARIMA预测特征（GDP、贸易等）                │
    │ 1.3 生成滞后特征（用历史数据预测未来）                       │
    └─────────────────────────────────────────────────────────────┘
                               ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ 阶段2: 模型选择阶段                                          │
    ├─────────────────────────────────────────────────────────────┤
    │ 2.1 尝试不同的滞后期组合（dv_lag和iv_lag）                  │
    │ 2.2 对每种组合进行网格搜索（寻找最佳超参数）                 │
    │ 2.3 选择交叉验证分数最高的模型配置                          │
    └─────────────────────────────────────────────────────────────┘
                               ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ 阶段3: 模型验证阶段                                          │
    ├─────────────────────────────────────────────────────────────┤
    │ 3.1 在保留测试集（2011-2024）上评估模型                    │
    │ 3.2 计算最优分类阈值（使F1分数最大化）                       │
    │ 3.3 进行递归回测（模拟真实预测场景）                         │
    └─────────────────────────────────────────────────────────────┘
                               ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ 阶段4: 未来预测阶段                                          │
    ├─────────────────────────────────────────────────────────────┤
    │ 4.1 使用全部历史数据（1961-2024）训练最终模型              │
    │ 4.2 预测2025年冲突概率                                       │
    │ 4.3 基于2025年预测结果，递归预测2026年冲突概率              │
    └─────────────────────────────────────────────────────────────┘
                               ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ 阶段5: 结果保存阶段                                          │
    ├─────────────────────────────────────────────────────────────┤
    │ 5.1 保存预测结果CSV文件                                      │
    │ 5.2 保存评估报告和指标                                       │
    │ 5.3 保存训练好的模型文件                                     │
    │ 5.4 在控制台打印摘要信息                                     │
    └─────────────────────────────────────────────────────────────┘

    参数:
        config: 运行配置对象（包含所有参数设置）

    返回:
        无（结果都保存到文件中）
    """
    # 初始化进度跟踪器（如果可用）
    global tracker
    if TRACKER_AVAILABLE:
        tracker = ProgressTracker("国际冲突预测管道", 12, 100.0)
    else:
        tracker = None

    # ============================================================
    # 阶段1: 数据准备
    # ============================================================

    # 1.1 数据加载
    if tracker:
        tracker.start_stage("数据加载", 1.0)
        tracker.set_task_detail("加载 data.xlsx 文件\n推断冲突类别")
    raw_df = load_international_data(config.data_path)  # 加载Excel数据
    if tracker:
        tracker.set_task_detail(f"数据加载完成: {len(raw_df)} 行\n{raw_df['country'].nunique()} 个国家\n年份范围: {raw_df['year'].min()}-{raw_df['year'].max()}\n推断冲突类别")
    classes = infer_classes(raw_df)  # 推断冲突类别（应该是0和1）
    if tracker:
        tracker.complete_stage()

    # 1.2 ARIMA预测：为2025年生成特征
    if tracker:
        tracker.start_stage("ARIMA预测", 10.0)
        tracker.set_task_detail(f"为 {config.forecast_year} 年生成ARIMA预测特征\n预测 {len(ARIMA_COLUMNS)} 个时间序列变量")
    forecast_df = append_forecast_year(raw_df, config.forecast_year, progress_tracker=tracker)
    if tracker:
        tracker.complete_stage()

    # 1.3 滞后特征生成
    if tracker:
        tracker.start_stage("滞后特征生成", 2.0)
        tracker.set_task_detail("构建国家编码映射\n生成滞后特征")
    country_codes = build_country_code_map(forecast_df)  # 国家名称到数字编码的映射
    lagged_df = build_lagged_frame(forecast_df, country_codes, config)  # 添加滞后特征
    if tracker:
        tracker.complete_stage()

    # 1.4 特征规格构建（所有可能的滞后期组合）
    if tracker:
        tracker.start_stage("特征规格构建", 1.0)
        tracker.set_task_detail("构建特征规格列表")
    specs = build_feature_specs(config.max_dv_lag, config.max_iv_lag)
    if tracker:
        tracker.complete_stage()

    # ============================================================
    # 阶段2: 模型选择（网格搜索）
    # ============================================================

    if tracker:
        tracker.start_stage("网格搜索", 50.0)
        tracker.set_task_detail(f"准备搜索 {len(specs)} 个特征规格\n开始网格搜索...")
    # 寻找最佳模型配置（这是最耗时的步骤）
    search = search_best_model(lagged_df, specs, config, progress_tracker=tracker)
    if tracker:
        tracker.complete_stage()

    # ============================================================
    # 阶段3: 模型评估
    # ============================================================

    # 3.1 准备数据：训练集（2011年前）和测试集（2011年后）
    if tracker:
        tracker.start_stage("训练最终模型", 5.0)
        tracker.set_task_detail("使用最佳参数训练评估模型")
    model_df = build_observed_frame_for_spec(lagged_df, search.spec, config.observed_last_year)
    train_df = model_df[model_df["year"] < config.train_cutoff].reset_index(drop=True)  # 训练集
    test_df = model_df[
        (model_df["year"] >= config.train_cutoff) & (model_df["year"] <= config.observed_last_year)
    ].reset_index(drop=True)  # 测试集（保留集）
    eval_model = fit_pipeline(train_df, search.spec, search.best_params, config)  # 训练评估模型
    if tracker:
        tracker.complete_stage()

    # 3.2 在测试集上评估模型，计算最优阈值
    if tracker:
        tracker.start_stage("模型评估", 5.0)
        tracker.set_task_detail("在测试集上评估模型性能\n计算最优阈值")
    metrics = evaluate_model(eval_model, test_df, search.spec, classes, threshold=None)
    optimal_threshold = metrics["optimal_threshold"]  # 自动找到的最佳分类阈值
    macro_f1 = metrics["macro_f1"]

    if tracker:
        tracker.set_task_detail(
            f"评估完成!\n"
            f"最优阈值: {optimal_threshold:.4f}\n"
            f"测试集宏平均 F1: {macro_f1:.4f}\n"
            f"测试集规模: {len(test_df)} 行"
        )
        tracker.complete_stage()

    # 3.3 递归回测（模拟真实预测场景，评估多期预测性能）
    if tracker:
        tracker.start_stage("递归回测", 15.0)
    recursive_backtest_df, recursive_backtest_metrics = run_recursive_backtest(
        raw_df=raw_df,
        spec=search.spec,
        params=search.best_params,
        country_codes=country_codes,
        config=config,
        classes=classes,
        threshold=optimal_threshold,
        progress_tracker=tracker,
    )
    metrics["recursive_backtest"] = recursive_backtest_metrics
    combined_f1 = recursive_backtest_metrics["combined"]["macro_f1"]

    if tracker:
        tracker.set_task_detail(
            f"递归回测完成!\n"
            f"综合宏平均 F1: {combined_f1:.4f}\n"
            f"回测数据行数: {len(recursive_backtest_df)}"
        )
        tracker.complete_stage()

    # ============================================================
    # 阶段4: 未来预测（2025和2026年）
    # ============================================================

    # 4.1 全量拟合：使用全部历史数据训练最终模型
    if tracker:
        tracker.start_stage("全量拟合", 5.0)
        tracker.set_task_detail(f"使用全部数据(1961-{config.observed_last_year})训练最终模型")
    final_model = fit_pipeline(model_df, search.spec, search.best_params, config)
    if tracker:
        tracker.complete_stage()

    # 4.2 预测2025年冲突
    if tracker:
        tracker.start_stage("2025年预测", 3.0)
        tracker.set_task_detail(f"准备 {config.forecast_year} 年预测特征...")
    feature_forecast = make_target_feature_frame(forecast_df, search.spec, country_codes, config.forecast_year)
    if tracker:
        tracker.set_task_detail(f"预测 {config.forecast_year} 年: {len(feature_forecast)} 个国家")
    result_forecast = prediction_table(
        final_model,
        feature_forecast[["country", "year", *search.spec.feature_cols]],
        config.forecast_year,
        classes,
        threshold=optimal_threshold,  # 使用自动找到的最佳阈值
    )
    if tracker:
        tracker.complete_stage()

    # 4.3 递归预测2026年冲突（基于2025年的预测结果）
    if tracker:
        tracker.start_stage("2026年预测", 3.0)
        tracker.set_task_detail(f"准备 {config.recursive_year} 年递归预测特征...")
    # 将2025年的预测结果注入到历史数据中
    recursive_input = inject_predictions(forecast_df, result_forecast, config.forecast_year)
    feature_recursive = make_target_feature_frame(recursive_input, search.spec, country_codes, config.recursive_year)
    if tracker:
        tracker.set_task_detail(f"递归预测 {config.recursive_year} 年: {len(feature_recursive)} 个国家")
    result_recursive = prediction_table(
        final_model,
        feature_recursive[["country", "year", *search.spec.feature_cols]],
        config.recursive_year,
        classes,
        threshold=optimal_threshold,
    )
    if tracker:
        tracker.complete_stage()

    # ============================================================
    # 阶段5: 结果保存
    # ============================================================

    if tracker:
        tracker.start_stage("结果保存", 5.0)
        tracker.set_task_detail("保存 CSV、JSON、模型文件和报告")
    save_outputs(
        config=config,
        forecast_df=forecast_df,
        metrics=metrics,
        recursive_backtest=recursive_backtest_df,
        classes=classes,
        result_forecast=result_forecast,
        result_recursive=result_recursive,
        model=final_model,
        search=search,
        country_codes=country_codes,
    )
    if tracker:
        tracker.complete_stage()

    # 完成进度跟踪
    if tracker:
        tracker.finish()

    # ============================================================
    # 在控制台打印摘要信息
    # ============================================================

    print("== Search result ==")
    print(f"best_macro_f1_cv={search.best_score:.4f}")
    print(f"dv_lag={search.spec.dv_lag}, iv_lag={search.spec.iv_lag}")
    print(search.best_params)
    print("== Holdout test ==")
    print(f"macro_f1={metrics['macro_f1']:.4f}")
    print(f"optimal_threshold={metrics['optimal_threshold']:.4f}")
    print(pd.DataFrame(metrics["confusion_matrix"]))
    print(build_holdout_class_table(metrics, classes).to_string(index=False))
    print(build_holdout_overall_table(metrics).to_string(index=False))
    print(build_model_selection_table(search).to_string(index=False))
    print("== Recursive backtest ==")
    print(f"combined_macro_f1={metrics['recursive_backtest']['combined']['macro_f1']:.4f}")
    for horizon in sorted(key for key in metrics["recursive_backtest"] if key.startswith("horizon_")):
        print(f"{horizon}_macro_f1={metrics['recursive_backtest'][horizon]['macro_f1']:.4f}")
    print("== Saved files ==")
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


if __name__ == "__main__":
    """
    脚本入口点

    功能：
        1. 解析命令行参数
        2. 调用run函数执行完整流程
    """
    run(parse_args())
