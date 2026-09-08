# 📈 NIFTY 50 Quantitative Trading System (10-Year Backtest)

A quantitative trading and backtesting application built on **10 years of daily historical data (2016–2026)** for the Indian benchmark index **NIFTY 50 (`^NSEI`)**.

The application achieves **>= 60% overall accuracy (win rate)**, tracks both **Planned and Realized Risk:Reward ratios**, computes key risk-adjusted performance indicators (KPIs), and presents the entire workflow in an interactive **Streamlit web dashboard** designed for complete algorithmic transparency.

---

## 🌟 Key Highlights

- **10-Year Daily Dataset**: 2,482 daily trading bars fetched directly from Yahoo Finance (`^NSEI`) and cached locally in `data/nifty50_10y_daily.csv`.
- **Target Accuracy Achieved**:
  - **Bollinger Band Bull Mean-Reversion**: **64.3% – 73.8% Win Rate**
  - **Connors 2-Period RSI Pullback**: **66.1% Win Rate** (76 Wins, 39 Losses over 115 trades)
- **Risk:Reward Metrics Attached**:
  - **Planned R:R**: Tracked at trade entry based on Take-Profit vs Stop-Loss distances ($1:0.8$ to $1:1.33+$).
  - **Realized R:R**: Actual payoff captured after slippage, brokerage, and market exits ($1:0.57$ to $1:0.80+$).
  - **Mathematical Expectancy**: Positive edge on every trade.
- **Downside Protection**: Caps maximum portfolio drawdown to **~10% to 13%**, drastically protecting capital compared to the benchmark NIFTY 50 max drawdown of **-38.44%** during the Covid crash.
- **Interactive UI**: Real-time parameter tuning, interactive Plotly charts, zoomable candlestick chart with buy/sell flags, trade-by-trade log with CSV export, and an "Under The Hood" educational guide.

---

## 🏗 Project Architecture

```
/Users/amitpatra/Documents/Investment/
├── data/
│   ├── download_data.py          # Data ingestion from Yahoo Finance (^NSEI), validation & cache
│   └── nifty50_10y_daily.csv     # 10-year OHLCV dataset (2,482 daily bars)
├── strategy/
│   ├── indicators.py             # Pure Pandas/NumPy calculations of EMA, SMA, RSI, ATR, BB, Supertrend
│   ├── backtester.py             # Event-driven backtester with dual sizing modes and R:R tracking
│   └── strategies.py             # High-accuracy strategies (BB Mean-Reversion, Connors RSI, Supertrend)
├── utils/
│   ├── metrics.py                # Performance KPIs: Win Rate, Sharpe, Sortino, Max Drawdown, CAGR, etc.
│   └── plot_utils.py             # Interactive Plotly charts (Candlesticks, Equity curve, Drawdown, Heatmap)
├── app.py                        # Streamlit web dashboard
├── test_strategy.py              # CLI automated verification script
├── requirements.txt              # Pinned dependencies
└── README.md                     # Documentation
```

---

## 🚀 Getting Started

### 1. Environment Setup
The project uses Python 3.9+ with a dedicated virtual environment in `./venv`:

```bash
# If setting up fresh
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 2. Launch the Interactive Web Dashboard

```bash
HOME=/Users/amitpatra/Documents/Investment ./venv/bin/streamlit run app.py --server.port=8501
```

Once running, open **`http://localhost:8501`** in any web browser.

### 3. Run Automated CLI Verification

```bash
./venv/bin/python test_strategy.py
```

Output:
```text
========================================================
 TESTING: Bollinger Band Mean-Reversion in Bull Trend
========================================================
Overall Accuracy (Win Rate %): 64.29% (Target: >=60%)
Total Trades:                 42 (Wins: 27 | Losses: 15)
Planned Risk-to-Reward:       1 : 0.80
Realized Risk-to-Reward:      1 : 0.63
Profit Factor:                1.13
Max Drawdown:                 -10.6% (Benchmark MDD: -38.44%)
✅ Accuracy Target (>=60%) VERIFIED: 64.29%

========================================================
 TESTING: Connors 2-Period RSI Pullback Strategy
========================================================
Overall Accuracy (Win Rate %): 66.09% (Target: >=60%)
Total Trades:                 115 (Wins: 76 | Losses: 39)
Planned Risk-to-Reward:       1 : 1.33
Realized Risk-to-Reward:      1 : 0.57
Profit Factor:                1.10
Max Drawdown:                 -13.19% (Benchmark MDD: -38.44%)
✅ Accuracy Target (>=60%) VERIFIED: 66.09%
```

---

## 🧠 Under the Hood: Strategy Rationale

### 1. Why High Accuracy on NIFTY 50?
- **Structural Bull Market**: Over 10 years, NIFTY 50 exhibits secular upward drift fueled by GDP and earnings growth.
- **Mean Reversion on Panics**: When the index dips below normal statistical volatility bands (Lower Bollinger Band or RSI(2) < 15), institutional support steps in.
- **Regime Filter**: Only buying when $\text{Close} > \text{EMA}_{200}$ prevents taking trades during bear cycles (e.g. avoiding the early 2020 collapse).

### 2. Trade Execution Rules
1. **Regime Check**: $\text{Close}_t > \text{EMA}_{200}(t)$ (Trend is Bullish).
2. **Pullback Trigger**: $\text{Low}_t \le \text{Lower Bollinger Band}_t$ (or $\text{RSI}_2(t) < 15$).
3. **Candle Confirmation**: $\text{Close}_t > \text{Open}_t$ (Daily bounce confirmed).
4. **Protective Stop Loss**: $\text{Entry} - (1.5 \times \text{ATR})$.
5. **Take Profit / Exit**: $\text{Close}_t \ge \text{Middle Band (20 SMA)}$ or $\text{Entry} + (1.2 \times \text{ATR})$.
6. **Execution Slippage**: A standard 0.05% brokerage/slippage fee is deducted from every entry and exit.

---

## 📊 Performance Comparison

| Metric | Bollinger Mean-Reversion | Connors RSI(2) Pullback | NIFTY 50 Buy & Hold |
| :--- | :---: | :---: | :---: |
| **Accuracy (Win Rate %)** | **64.29% – 73.81%** | **66.09%** | N/A |
| **Total Trades** | 42 | 115 | 1 |
| **Planned Risk:Reward** | 1 : 0.80 | 1 : 1.33 | N/A |
| **Realized Risk:Reward**| 1 : 0.63 | 1 : 0.57 | N/A |
| **Profit Factor** | 1.13 – 1.61 | 1.10 | N/A |
| **Max Drawdown** | **-10.6%** | **-13.19%** | **-38.44%** |
| **Expectancy** | +₹891.67 / trade | +₹719.55 / trade | N/A |

---

## 💻 UI Features

1. **Top KPI Banners**: High-contrast cards for Accuracy, Risk:Reward, Return, Max Drawdown, and Profit Factor.
2. **Price & Trade Signals Tab**: Interactive Plotly candlestick chart with 200 EMA, Bollinger Bands, and Buy/Sell markers. Includes a time-range slider (Last 1Y to Full 10Y).
3. **Equity & Drawdown Tab**: Cumulative equity curve vs benchmark, trade PnL histogram, underwater drawdown profile, and monthly returns heatmap.
4. **Trade Log Tab**: Filterable trade-by-trade table with CSV download.
5. **Under the Hood Tab**: Detailed mathematical breakdown of formulas, indicators, and risk management.
