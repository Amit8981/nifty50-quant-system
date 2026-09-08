"""
Performance Metrics and KPI Calculations.
Computes Win Rate, Risk-to-Reward Ratio, Sharpe, Sortino, Drawdown, CAGR, etc.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd


def calculate_kpis(
    equity_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    initial_capital: float = 1_000_000.0,
    risk_free_rate: float = 0.065,  # 6.5% standard Indian 10y G-Sec / Repo rate
) -> Dict[str, Any]:
    """
    Computes a comprehensive dictionary of financial KPIs and performance metrics.
    """
    if equity_df.empty:
        return {}

    # Equity series
    strat_equity = equity_df["Strategy_Equity"]
    bench_equity = equity_df["Benchmark_Equity"]

    # Basic Returns
    final_strat_val = strat_equity.iloc[-1]
    final_bench_val = bench_equity.iloc[-1]

    strat_total_return_pct = ((final_strat_val - initial_capital) / initial_capital) * 100.0
    bench_total_return_pct = ((final_bench_val - initial_capital) / initial_capital) * 100.0

    # Duration & CAGR
    days_total = max(1, (equity_df.index[-1] - equity_df.index[0]).days)
    years = days_total / 365.25

    strat_cagr = ((final_strat_val / initial_capital) ** (1.0 / max(years, 0.1)) - 1.0) * 100.0
    bench_cagr = ((final_bench_val / initial_capital) ** (1.0 / max(years, 0.1)) - 1.0) * 100.0

    # Drawdown calculations
    strat_peak = strat_equity.cummax()
    strat_dd = (strat_equity - strat_peak) / strat_peak * 100.0
    max_dd = strat_dd.min()

    bench_peak = bench_equity.cummax()
    bench_dd = (bench_equity - bench_peak) / bench_peak * 100.0
    bench_max_dd = bench_dd.min()

    # Max Drawdown Duration (days)
    is_underwater = strat_equity < strat_peak
    dd_durations = []
    current_dd_len = 0
    for under in is_underwater:
        if under:
            current_dd_len += 1
        else:
            if current_dd_len > 0:
                dd_durations.append(current_dd_len)
            current_dd_len = 0
    if current_dd_len > 0:
        dd_durations.append(current_dd_len)
    max_dd_duration_days = max(dd_durations) if dd_durations else 0

    # Daily returns for Sharpe & Sortino
    daily_returns = strat_equity.pct_change().dropna()
    trading_days_per_year = 252

    if len(daily_returns) > 1 and daily_returns.std() > 0:
        daily_rf = (1.0 + risk_free_rate) ** (1.0 / trading_days_per_year) - 1.0
        excess_returns = daily_returns - daily_rf
        sharpe_ratio = (excess_returns.mean() / daily_returns.std()) * np.sqrt(trading_days_per_year)

        # Sortino Ratio (downside deviation only)
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 1 else daily_returns.std()
        sortino_ratio = (excess_returns.mean() / (downside_std + 1e-10)) * np.sqrt(trading_days_per_year)
    else:
        sharpe_ratio = 0.0
        sortino_ratio = 0.0

    # Trade statistics
    if trades_df is not None and not trades_df.empty:
        total_trades = len(trades_df)
        winning_trades = trades_df[trades_df["Net PnL (₹)"] > 0]
        losing_trades = trades_df[trades_df["Net PnL (₹)"] <= 0]

        num_wins = len(winning_trades)
        num_losses = len(losing_trades)
        win_rate_pct = (num_wins / total_trades) * 100.0 if total_trades > 0 else 0.0

        avg_win_amt = winning_trades["Net PnL (₹)"].mean() if num_wins > 0 else 0.0
        avg_loss_amt = abs(losing_trades["Net PnL (₹)"].mean()) if num_losses > 0 else 0.0

        realized_rr = (avg_win_amt / avg_loss_amt) if avg_loss_amt > 0 else (avg_win_amt if avg_win_amt > 0 else 0.0)
        planned_rr = trades_df["Planned R:R"].mean() if "Planned R:R" in trades_df.columns else 0.0

        gross_profit = winning_trades["Net PnL (₹)"].sum() if num_wins > 0 else 0.0
        gross_loss = abs(losing_trades["Net PnL (₹)"].sum()) if num_losses > 0 else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)

        # Expectancy per trade: (P_win * Avg Win) - (P_loss * Avg Loss)
        p_win = num_wins / total_trades
        p_loss = num_losses / total_trades
        expectancy_inr = (p_win * avg_win_amt) - (p_loss * avg_loss_amt)

        avg_duration_days = trades_df["Duration (Days)"].mean()

        # Streaks
        outcomes = (trades_df["Net PnL (₹)"] > 0).astype(int).values
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        cur_w, cur_l = 0, 0
        for out in outcomes:
            if out == 1:
                cur_w += 1
                cur_l = 0
                max_consecutive_wins = max(max_consecutive_wins, cur_w)
            else:
                cur_l += 1
                cur_w = 0
                max_consecutive_losses = max(max_consecutive_losses, cur_l)

        best_trade_pct = trades_df["Return (%)"].max()
        worst_trade_pct = trades_df["Return (%)"].min()
        best_trade_inr = trades_df["Net PnL (₹)"].max()
        worst_trade_inr = trades_df["Net PnL (₹)"].min()
    else:
        total_trades = 0
        num_wins = 0
        num_losses = 0
        win_rate_pct = 0.0
        realized_rr = 0.0
        planned_rr = 0.0
        profit_factor = 0.0
        expectancy_inr = 0.0
        avg_win_amt = 0.0
        avg_loss_amt = 0.0
        avg_duration_days = 0.0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        best_trade_pct = 0.0
        worst_trade_pct = 0.0
        best_trade_inr = 0.0
        worst_trade_inr = 0.0

    return {
        "Initial Capital (₹)": initial_capital,
        "Final Strategy Equity (₹)": round(final_strat_val, 2),
        "Final Benchmark Equity (₹)": round(final_bench_val, 2),
        "Strategy Total Return (%)": round(strat_total_return_pct, 2),
        "Benchmark Total Return (%)": round(bench_total_return_pct, 2),
        "Strategy CAGR (%)": round(strat_cagr, 2),
        "Benchmark CAGR (%)": round(bench_cagr, 2),
        "Overall Accuracy (Win Rate %)": round(win_rate_pct, 2),
        "Total Trades": total_trades,
        "Winning Trades": num_wins,
        "Losing Trades": num_losses,
        "Planned R:R": round(planned_rr, 2),
        "Realized R:R": round(realized_rr, 2),
        "Profit Factor": round(profit_factor, 2),
        "Expectancy (₹/Trade)": round(expectancy_inr, 2),
        "Average Win (₹)": round(avg_win_amt, 2),
        "Average Loss (₹)": round(avg_loss_amt, 2),
        "Max Drawdown (%)": round(max_dd, 2),
        "Benchmark Max Drawdown (%)": round(bench_max_dd, 2),
        "Max Drawdown Duration (Days)": int(max_dd_duration_days),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Sortino Ratio": round(sortino_ratio, 2),
        "Average Trade Duration (Days)": round(avg_duration_days, 1),
        "Max Consecutive Wins": max_consecutive_wins,
        "Max Consecutive Losses": max_consecutive_losses,
        "Best Trade (₹)": round(best_trade_inr, 2),
        "Worst Trade (₹)": round(worst_trade_inr, 2),
        "Best Trade (%)": round(best_trade_pct, 2),
        "Worst Trade (%)": round(worst_trade_pct, 2),
    }
