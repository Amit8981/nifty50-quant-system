"""
Plotting and Visualization Utilities using Plotly.
Provides interactive financial charts with In-Sample and Out-of-Sample demarcation.
"""

from typing import Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_equity_curve(
    equity_df: pd.DataFrame,
    initial_capital: float = 1_000_000.0,
    split_date: Optional[str] = "2025-09-01",
) -> go.Figure:
    """
    Plots cumulative portfolio equity curve vs NIFTY 50 Buy & Hold benchmark,
    with an explicit vertical line demarcating In-Sample vs Validation.
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=equity_df.index,
            y=equity_df["Strategy_Equity"],
            name="Strategy Equity",
            line=dict(color="#00D084", width=2.5),
            hovertemplate="Date: %{x|%Y-%m-%d}<br>Strategy: ₹%{y:,.2f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=equity_df.index,
            y=equity_df["Benchmark_Equity"],
            name="NIFTY 50 Buy & Hold",
            line=dict(color="#8892B0", width=1.8, dash="dot"),
            hovertemplate="Date: %{x|%Y-%m-%d}<br>Benchmark: ₹%{y:,.2f}<extra></extra>",
        )
    )

    fig.add_hline(
        y=initial_capital,
        line_dash="dash",
        line_color="#4A5568",
        annotation_text="Starting Capital (₹10L)",
        annotation_position="bottom right",
    )

    # In-Sample vs Validation Demarcation Line
    if split_date:
        split_dt = pd.to_datetime(split_date)
        if equity_df.index[0] < split_dt < equity_df.index[-1]:
            fig.add_vline(
                x=split_dt,
                line_width=2,
                line_dash="dash",
                line_color="#FFD700",
                annotation_text="👈 In-Sample (2015-2025) | Out-of-Sample (Validation) 👉",
                annotation_position="top left",
                annotation_font_color="#FFD700",
            )

    fig.update_layout(
        title="<b>Cumulative Equity Curve vs Benchmark (Development & Validation)</b>",
        xaxis_title="Date",
        yaxis_title="Portfolio Value (₹ INR)",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=40, r=40, t=50, b=40),
        height=450,
    )

    return fig


def plot_drawdown(equity_df: pd.DataFrame, split_date: Optional[str] = "2025-09-01") -> go.Figure:
    """
    Plots underwater drawdown curve (%) for Strategy and Benchmark.
    """
    strat_peak = equity_df["Strategy_Equity"].cummax()
    strat_dd = (equity_df["Strategy_Equity"] - strat_peak) / strat_peak * 100.0

    bench_peak = equity_df["Benchmark_Equity"].cummax()
    bench_dd = (equity_df["Benchmark_Equity"] - bench_peak) / bench_peak * 100.0

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=equity_df.index,
            y=strat_dd,
            name="Strategy Drawdown",
            fill="tozeroy",
            line=dict(color="#FF4B4B", width=1.8),
            hovertemplate="Strategy DD: %{y:.2f}%<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=equity_df.index,
            y=bench_dd,
            name="NIFTY 50 Benchmark Drawdown",
            line=dict(color="#A0AEC0", width=1.2, dash="dot"),
            hovertemplate="Benchmark DD: %{y:.2f}%<extra></extra>",
        )
    )

    if split_date:
        split_dt = pd.to_datetime(split_date)
        if equity_df.index[0] < split_dt < equity_df.index[-1]:
            fig.add_vline(
                x=split_dt,
                line_width=1.5,
                line_dash="dash",
                line_color="#FFD700",
            )

    fig.update_layout(
        title="<b>Underwater Drawdown Profile (% from Peak)</b>",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01),
        margin=dict(l=40, r=40, t=50, b=40),
        height=320,
    )

    return fig


def plot_price_and_signals(
    df_signals: pd.DataFrame,
    trades_df: Optional[pd.DataFrame] = None,
    sample_window_days: Optional[int] = None,
    split_date: Optional[str] = "2025-09-01",
) -> go.Figure:
    """
    Interactive candlestick chart with indicators and buy/sell signals.
    """
    plot_df = df_signals.iloc[-sample_window_days:] if sample_window_days and len(df_signals) > sample_window_days else df_signals

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.75, 0.25],
    )

    fig.add_trace(
        go.Candlestick(
            x=plot_df.index,
            open=plot_df["Open"],
            high=plot_df["High"],
            low=plot_df["Low"],
            close=plot_df["Close"],
            name="NIFTY 50 Price",
            increasing_line_color="#00D084",
            decreasing_line_color="#FF4B4B",
        ),
        row=1,
        col=1,
    )

    if "EMA_Trend" in plot_df.columns:
        fig.add_trace(
            go.Scatter(
                x=plot_df.index,
                y=plot_df["EMA_Trend"],
                name="200 EMA (Regime Filter)",
                line=dict(color="#F6AD55", width=1.5),
            ),
            row=1,
            col=1,
        )

    if "BB_Up" in plot_df.columns and "BB_Low" in plot_df.columns:
        fig.add_trace(
            go.Scatter(
                x=plot_df.index,
                y=plot_df["BB_Up"],
                name="Upper BB",
                line=dict(color="rgba(160, 174, 192, 0.4)", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=plot_df.index,
                y=plot_df["BB_Mid"],
                name="20 SMA (Mid BB)",
                line=dict(color="rgba(237, 100, 166, 0.8)", width=1.2),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=plot_df.index,
                y=plot_df["BB_Low"],
                name="Lower BB (Oversold Dip)",
                line=dict(color="rgba(160, 174, 192, 0.4)", width=1, dash="dot"),
            ),
            row=1,
            col=1,
        )

    if "Supertrend" in plot_df.columns:
        fig.add_trace(
            go.Scatter(
                x=plot_df.index,
                y=plot_df["Supertrend"],
                name="Supertrend",
                line=dict(color="#4FD1C5", width=1.5),
            ),
            row=1,
            col=1,
        )

    # Buy / Exit Markers
    if trades_df is not None and not trades_df.empty:
        start_dt = plot_df.index[0].strftime("%Y-%m-%d")
        sub_trades = trades_df[trades_df["Entry Date"] >= start_dt]

        if not sub_trades.empty:
            fig.add_trace(
                go.Scatter(
                    x=pd.to_datetime(sub_trades["Entry Date"]),
                    y=sub_trades["Entry Price (₹)"],
                    mode="markers",
                    marker=dict(symbol="triangle-up", size=11, color="#00FF88", line=dict(width=1, color="black")),
                    name="Buy Entry",
                    hovertemplate="Buy Date: %{x|%Y-%m-%d}<br>Price: ₹%{y:,.2f}<extra></extra>",
                ),
                row=1,
                col=1,
            )

            exit_dates = sub_trades.dropna(subset=["Exit Date"])
            if not exit_dates.empty:
                fig.add_trace(
                    go.Scatter(
                        x=pd.to_datetime(exit_dates["Exit Date"]),
                        y=exit_dates["Exit Price (₹)"],
                        mode="markers",
                        marker=dict(symbol="triangle-down", size=11, color="#FF2D55", line=dict(width=1, color="black")),
                        name="Exit Trade",
                        hovertemplate="Exit Date: %{x|%Y-%m-%d}<br>Price: ₹%{y:,.2f}<br>PnL: %{text}<extra></extra>",
                        text=[f"₹{pnl:,.2f} ({ret}%)" for pnl, ret in zip(exit_dates["Net PnL (₹)"], exit_dates["Return (%)"])],
                    ),
                    row=1,
                    col=1,
                )

    if split_date:
        split_dt = pd.to_datetime(split_date)
        if plot_df.index[0] < split_dt < plot_df.index[-1]:
            fig.add_vline(
                x=split_dt,
                line_width=2,
                line_dash="dash",
                line_color="#FFD700",
                annotation_text="Validation Start",
                annotation_position="top left",
                annotation_font_color="#FFD700",
                row=1,
                col=1,
            )

    # Subplot 2: RSI
    if "RSI" in plot_df.columns:
        fig.add_trace(
            go.Scatter(
                x=plot_df.index,
                y=plot_df["RSI"],
                name="RSI (14)",
                line=dict(color="#9F7AEA", width=1.5),
            ),
            row=2,
            col=1,
        )
        fig.add_hline(y=70, line_dash="dash", line_color="#FF4B4B", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#00D084", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[10, 90], row=2, col=1)

    fig.update_layout(
        title="<b>NIFTY 50 Price Action, Indicators & Execution Signals</b>",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(l=40, r=40, t=50, b=40),
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def plot_trade_pnl_distribution(trades_df: pd.DataFrame) -> go.Figure:
    if trades_df.empty:
        return go.Figure()

    returns = trades_df["Return (%)"]
    wins = returns[returns > 0]
    losses = returns[returns <= 0]

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=wins,
            name="Wins",
            marker_color="#00D084",
            opacity=0.8,
            nbinsx=20,
        )
    )
    fig.add_trace(
        go.Histogram(
            x=losses,
            name="Losses",
            marker_color="#FF4B4B",
            opacity=0.8,
            nbinsx=20,
        )
    )
    fig.add_vline(x=0, line_dash="dash", line_color="white", line_width=1.5)

    fig.update_layout(
        title="<b>Trade Return Distribution (%)</b>",
        xaxis_title="Trade Return (%)",
        yaxis_title="Number of Trades",
        barmode="overlay",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=50, b=40),
        height=320,
        legend=dict(yanchor="top", y=0.98, xanchor="right", x=0.98),
    )
    return fig


def plot_monthly_heatmap(equity_df: pd.DataFrame) -> go.Figure:
    strat_daily = equity_df["Strategy_Equity"].pct_change().dropna()
    monthly_ret = strat_daily.resample("ME").apply(lambda r: (1 + r).prod() - 1) * 100.0

    if monthly_ret.empty:
        return go.Figure()

    df_m = pd.DataFrame({
        "Year": monthly_ret.index.year,
        "Month": monthly_ret.index.strftime("%b"),
        "Return": monthly_ret.values
    })

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    table = df_m.pivot(index="Year", columns="Month", values="Return").reindex(columns=month_order)

    fig = go.Figure(
        data=go.Heatmap(
            z=table.values,
            x=table.columns,
            y=table.index,
            colorscale="RdYlGn",
            zmid=0,
            text=np.round(table.values, 1),
            texttemplate="%{text}%",
            hoverongaps=False,
            colorbar=dict(title="Return %"),
        )
    )

    fig.update_layout(
        title="<b>Monthly Returns Heatmap (%)</b>",
        xaxis_title="Month",
        yaxis_title="Year",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=50, b=40),
        height=320,
    )

    return fig
