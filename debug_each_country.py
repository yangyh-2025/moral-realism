#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐个国家测试ARIMA预测 - 找出哪个国家卡住了
"""

import pandas as pd
import numpy as np
import sys

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

def forecast_one_step(years, values):
    """ARIMA单步预测"""
    from statsmodels.tsa.arima.model import ARIMA
    import warnings

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

def test_country(country, group):
    """测试单个国家的所有ARIMA预测"""
    results = {}

    for col in ARIMA_COLUMNS:
        if col not in group.columns:
            results[col] = None
            continue

        try:
            result = forecast_one_step(group["year"], group[col])
            results[col] = result
        except Exception as e:
            print(f"    ❌ {col}: 错误 - {type(e).__name__}: {str(e)[:50]}")
            return False

    return True

if __name__ == "__main__":
    print("\n逐个国家测试ARIMA预测...")
    print("=" * 70)

    # 加载数据
    df = pd.read_excel("data.xlsx")
    df["country"] = df["ccode"].astype(str)
    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    # 按国家分组
    countries = list(df.groupby("country", sort=True))
    total_countries = len(countries)

    print(f"总共 {total_countries} 个国家需要测试\n")

    failed_countries = []

    for idx, (country, group) in enumerate(countries, 1):
        print(f"[{idx}/{total_countries}] 测试国家 {country}...", end="", flush=True)

        try:
            success = test_country(country, group)
            if success:
                print(" ✓")
            else:
                print(" ❌ 失败")
                failed_countries.append(country)
        except Exception as e:
            print(f" ❌ 异常 - {type(e).__name__}: {str(e)[:50]}")
            failed_countries.append(country)

        # 每10个国家显示一次进度
        if idx % 10 == 0:
            print(f"  已完成: {idx}/{total_countries} ({idx/total_countries*100:.1f}%)")

    print("\n" + "=" * 70)
    if failed_countries:
        print(f"❌ 失败的国家 ({len(failed_countries)}个):")
        for c in failed_countries:
            print(f"  - {c}")
    else:
        print(f"✓ 所有 {total_countries} 个国家测试通过")
    print("=" * 70)
