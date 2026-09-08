"""
Verification script for 10-Year In-Sample Development (2015-2025)
and 1-Year Out-of-Sample Validation (2025-2026).
"""

import os
import pandas as pd
from data.download_data import download_nifty50_data
from strategy.backtester import BacktestEngine
from strategy.strategies import (
    bollinger_mean_reversion_strategy,
    connors_rsi2_strategy,
)
from utils.metrics import calculate_kpis

SPLIT_DATE = "2025-09-01"


def evaluate_split(name, strategy_func, df, **params):
    print(f"\n{'='*65}")
    print(f" STRATEGY: {name}")
    print(f"{'='*65}")

    engine_full = BacktestEngine(df, initial_capital=1_000_000.0, sizing_mode="capital_alloc", allocation_pct=0.95)
    res_full = engine_full.run(strategy_func, **params)
    eq_full = res_full["equity_df"]
    tr_full = res_full["trades_df"]

    # 1. In-Sample Development Period (2015-01 to 2025-08)
    in_sample_mask = eq_full.index < pd.to_datetime(SPLIT_DATE)
    eq_in = eq_full.loc[in_sample_mask]
    tr_in = tr_full[tr_full["Entry Date"] < SPLIT_DATE] if not tr_full.empty else pd.DataFrame()
    kpi_in = calculate_kpis(eq_in, tr_in, initial_capital=1_000_000.0)

    # 2. Out-of-Sample Validation Period (2025-09 to Present)
    out_sample_mask = eq_full.index >= pd.to_datetime(SPLIT_DATE)
    eq_out = eq_full.loc[out_sample_mask]
    tr_out = tr_full[tr_full["Entry Date"] >= SPLIT_DATE] if not tr_full.empty else pd.DataFrame()
    start_out_cap = eq_in["Strategy_Equity"].iloc[-1] if not eq_in.empty else 1_000_000.0
    kpi_out = calculate_kpis(eq_out, tr_out, initial_capital=start_out_cap)

    print(f"--- 1. IN-SAMPLE DEVELOPMENT (2015 - 2025, ~10 Years) ---")
    print(f"Accuracy (Win Rate %):    {kpi_in.get('Overall Accuracy (Win Rate %)', 0)}% (Target >=60%)")
    print(f"Total Trades:            {kpi_in.get('Total Trades', 0)} (Wins: {kpi_in.get('Winning Trades', 0)} | Losses: {kpi_in.get('Losing Trades', 0)})")
    print(f"Planned Risk:Reward:     1 : {kpi_in.get('Planned R:R', 0):.2f}")
    print(f"Realized Risk:Reward:    1 : {kpi_in.get('Realized R:R', 0):.2f}")
    print(f"Profit Factor:           {kpi_in.get('Profit Factor', 0)}")
    print(f"Max Drawdown:            {kpi_in.get('Max Drawdown (%)', 0)}% (vs Benchmark: {kpi_in.get('Benchmark Max Drawdown (%)', 0)}%)")

    print(f"\n--- 2. OUT-OF-SAMPLE VALIDATION (2025 - 2026, Last 1 Year) ---")
    print(f"Validation Accuracy:     {kpi_out.get('Overall Accuracy (Win Rate %)', 0)}%")
    print(f"Validation Trades:       {kpi_out.get('Total Trades', 0)} (Wins: {kpi_out.get('Winning Trades', 0)} | Losses: {kpi_out.get('Losing Trades', 0)})")
    print(f"Realized Risk:Reward:    1 : {kpi_out.get('Realized R:R', 0):.2f}")
    print(f"Profit Factor:           {kpi_out.get('Profit Factor', 0)}")
    print(f"Validation Drawdown:     {kpi_out.get('Max Drawdown (%)', 0)}% (vs Benchmark: {kpi_out.get('Benchmark Max Drawdown (%)', 0)}%)")

    return kpi_in, kpi_out


def main():
    df = download_nifty50_data()
    print(f"Loaded {len(df)} daily trading bars from {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}.")

    # Evaluate Bollinger Mean Reversion
    evaluate_split(
        "Bollinger Band Mean-Reversion in Bull Trend",
        bollinger_mean_reversion_strategy,
        df,
        trend_ema_period=200,
        bb_period=20,
        bb_std=2.0,
        sl_atr_multiplier=1.5,
        tp_atr_multiplier=1.2,
        rsi_filter_max=65.0,
    )

    # Evaluate Connors RSI
    evaluate_split(
        "Connors 2-Period RSI Pullback Strategy",
        connors_rsi2_strategy,
        df,
        trend_sma_period=200,
        rsi_period=2,
        rsi_oversold_threshold=15.0,
        exit_sma_period=10,
        sl_pct=0.03,
        tp_pct=0.04,
    )


if __name__ == "__main__":
    main()
