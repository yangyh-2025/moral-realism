#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIMA预测阶段诊断脚本
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

# ARIMA预测列
ARIMA_COLUMNS = [
    "GDP_per_capita_ln",
    "GDP_growth",
    "population_density_ln",
    "trade",
    "military_expenditure_final",
    "national_capacity",
]

# ARIMA参数组合
ARIMA_ORDERS = [
    (0, 1, 0), (1, 1, 0), (0, 1, 1), (1, 1, 1),
    (2, 1, 0), (0, 1, 2), (2, 1, 1),
]

def check_data_issues():
    """检查数据问题"""
    print("=" * 60)
    print("检查数据文件...")
    print("=" * 60)

    df = pd.read_excel("data.xlsx")
    print(f"总行数: {len(df)}")
    print(f"总国家数: {df['ccode'].nunique()}")
    print(f"年份范围: {df['year'].min()} - {df['year'].max()}")

    # 检查ARIMA列的缺失值和异常值
    print("\n检查ARIMA列的数据质量...")
    for col in ARIMA_COLUMNS:
        if col not in df.columns:
            print(f"  ❌ 列 {col} 不存在!")
            continue

        total = len(df)
        null_count = df[col].isna().sum()
        inf_count = np.isinf(df[col]).sum()
        unique_count = df[col].nunique()

        print(f"  {col}:")
        print(f"    - 缺失值: {null_count}/{total} ({null_count/total*100:.1f}%)")
        print(f"    - 无穷值: {inf_count}")
        print(f"    - 唯一值数量: {unique_count}")

        # 检查每个国家的时间序列长度
        min_years = df.groupby('ccode')[col].count().min()
        max_years = df.groupby('ccode')[col].count().max()
        print(f"    - 国家年份数范围: {min_years} - {max_years}")

def test_arima_on_one_country():
    """测试一个国家的ARIMA拟合"""
    print("\n" + "=" * 60)
    print("测试ARIMA拟合（用第一个国家）...")
    print("=" * 60)

    from statsmodels.tsa.arima.model import ARIMA

    df = pd.read_excel("data.xlsx")
    df["country"] = df["ccode"].astype(str)

    # 获取第一个国家
    first_country = df["country"].iloc[0]
    print(f"\n测试国家: {first_country}")

    group = df[df["country"] == first_country].sort_values("year")
    print(f"年份数: {len(group)}")
    print(f"年份范围: {group['year'].min()} - {group['year'].max()}")

    # 测试每个ARIMA列
    for col in ARIMA_COLUMNS:
        if col not in group.columns:
            continue

        print(f"\n测试列: {col}")

        # 准备数据
        frame = pd.DataFrame({"year": group["year"], "value": group[col]}).dropna()
        series = pd.Series(
            frame["value"].to_numpy(dtype=float),
            index=pd.PeriodIndex(frame["year"].astype(int), freq="Y"),
        )

        print(f"  有效数据点: {len(series)}")

        if len(series) < 4:
            print(f"  ⚠️ 数据点太少，跳过ARIMA测试")
            continue

        if series.nunique() == 1:
            print(f"  ⚠️ 所有值相同，跳过ARIMA测试")
            continue

        # 测试每个ARIMA参数组合
        for order in ARIMA_ORDERS:
            print(f"  测试 ARIMA{order}...", end="", flush=True)

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fitted = ARIMA(
                        series,
                        order=order,
                        trend="n",
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                    ).fit()
                    print(f" ✓ AIC={fitted.aic:.2f}")
            except Exception as e:
                print(f" ❌ 错误: {type(e).__name__}: {str(e)[:50]}")
                break  # 如果出错就停止测试这个列

def test_full_forecast_one_step():
    """完全复制forecast_one_step函数进行测试"""
    print("\n" + "=" * 60)
    print("测试forecast_one_step函数（前5个国家）...")
    print("=" * 60)

    from statsmodels.tsa.arima.model import ARIMA

    df = pd.read_excel("data.xlsx")
    df["country"] = df["ccode"].astype(str)

    def forecast_one_step(years, values):
        frame = pd.DataFrame({"year": years, "value": values}).dropna()
        if frame.empty:
            return np.nan

        series = pd.Series(
            frame["value"].to_numpy(dtype=float),
            index=pd.PeriodIndex(frame["year"].astype(int), freq="Y"),
        )

        if len(series) < 4 or series.nunique() == 1:
            return float(series.iloc[-1])

        best_aic = np.inf
        best_value = float(series.iloc[-1])

        for order in ARIMA_ORDERS:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fitted = ARIMA(series, order=order, trend="n",
                                 enforce_stationarity=False,
                                 enforce_invertibility=False).fit()

                if not np.isfinite(fitted.aic) or fitted.aic >= best_aic:
                    continue

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    forecast = fitted.forecast(steps=1)

                best_aic = float(fitted.aic)
                best_value = float(forecast.iloc[0])
            except Exception:
                continue

        return best_value

    # 测试前5个国家
    countries_to_test = list(df.groupby("country", sort=True))[:5]

    for idx, (country, group) in enumerate(countries_to_test, 1):
        print(f"\n[{idx}/5] 国家: {country}")

        for col in ARIMA_COLUMNS:
            if col not in group.columns:
                continue

            print(f"  {col}...", end="", flush=True)

            try:
                result = forecast_one_step(group["year"], group[col])
                print(f" ✓ 结果: {result:.4f}")
            except Exception as e:
                print(f" ❌ 错误: {type(e).__name__}")
                print(f"      详情: {str(e)[:100]}")
                break

if __name__ == "__main__":
    print("\nARIMA预测诊断工具\n")

    try:
        check_data_issues()
        test_arima_on_one_country()
        test_full_forecast_one_step()
        print("\n" + "=" * 60)
        print("✓ 诊断完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
