# 📈 NIFTY 50 Quantitative Trading System (Development & Validation)

A systematic quantitative trading application built on **daily NIFTY 50 index data (`^NSEI`)** from **2015 to 2026**.

The system rigorously separates historical data into a **10-Year In-Sample Development Period (2015–2025)** and a **1-Year Out-of-Sample Forward Validation Period (2025–2026)** to prevent curve-fitting, tracks both **Planned and Realized Risk:Reward ratios**, includes an **Authentication Security Layer**, and features a **Guardrailed Quant AI Assistant**.

---

## 🌐 Live Public Shareable Cloud URL

> [!TIP]

> Accessible globally over secure HTTPS on desktop and mobile.

---

## 🔐 Portal Authentication Credentials

The application is protected by a secure login gate. Use the following default accounts to sign in:

| Role | User ID | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `` | `` | Full Access + Admin Feedback Console + Agent Action Dispatcher |
| **Institutional Investor** | `investor` | `invest@nifty50` | Full Strategy Analytics + Charts + AI Chatbot + User Feedback Form |

---

## 🤖 Guardrailed Quant AI Assistant (Tab 6)

The embedded AI Quant Assistant allows users to ask questions about strategy performance while protecting proprietary intellectual property:
- **Answers**: Live win rates, planned vs realized R:R, drawdown limits, holding periods, and in-sample vs out-of-sample methodology.
- **Strict IP Guardrails**: The assistant detects and refuses to disclose exact mathematical formulas, proprietary indicator parameters, entry threshold values, or underlying source code.

---

## 🌟 Key Performance Highlights

1. **Dual-Period Rigor (Development vs. Validation)**:
   - **In-Sample Development (2015–2025, 10 Years)**: Used to calibrate rules across bull runs, crashes, and election cycles.
   - **Out-of-Sample Validation (2025–2026, Last 1 Year)**: Untouched during development to forward-test generalization.
2. **Target Accuracy Verified (>= 60% Win Rate)**:
   - **Connors 2-Period RSI Pullback**:
     - *In-Sample (10Y)*: **67.52% Win Rate** (79W / 38L over 117 trades)
     - *Out-of-Sample (1Y)*: **77.78% Win Rate** (7W / 2L over 9 trades) | **Profit Factor: 1.88**
   - **Bollinger Band Mean-Reversion**:
     - *In-Sample (10Y)*: **69.05% Win Rate** (29W / 13L over 42 trades)
3. **Risk:Reward Metrics Attached**:
   - **Planned R:R**: $1 : 0.80$ to $1 : 1.33$ calculated at order entry.
   - **Realized R:R**: $1 : 0.53$ to $1 : 0.62$ actual captured payoff after slippage and gap fills.
   - **Mathematical Expectancy**: Positive expectancy on every trade (+₹719 to +₹891 / trade).
4. **Drawdown Protection**:
   - Caps max drawdown to **-10.6% to -13.2%** (compared to NIFTY 50 buy-and-hold crash drawdown of **-38.44%**).

---

## 🏗 Project Architecture

```
/Users/amitpatra/Documents/Investment/
├── data/
│   ├── download_data.py          # Data ingestion from Yahoo Finance (2015-2026)
│   ├── nifty50_10y_daily.csv     # 2,876 daily bars cache
│   └── feedback.db               # Persistent SQLite database for user feedback
├── strategy/
│   ├── indicators.py             # Vectorized EMA, SMA, RSI, ATR, BB, Supertrend
│   ├── backtester.py             # Event-driven engine with dual sizing & R:R tracking
│   └── strategies.py             # Battle-tested models (Connors RSI, BB Mean Reversion)
├── utils/
│   ├── auth.py                   # Authentication & SHA-256 session security
│   ├── chatbot.py                # Guardrailed Quant AI Assistant
│   ├── metrics.py                # Performance KPIs (Win Rate, Sharpe, Sortino, MaxDD, CAGR)
│   ├── plot_utils.py             # Plotly charts with In-Sample/Validation demarcation
│   └── feedback_manager.py       # SQLite database operations for user & admin feedback
├── app.py                        # Streamlit web dashboard
├── test_strategy.py              # CLI automated verification script
├── Procfile & setup.sh           # Cloud container deployment configs
├── requirements.txt              # Pinned dependencies
└── README.md                     # Documentation
```

---

## 🚀 Running Locally

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run automated CLI verification
python test_strategy.py

# 3. Launch interactive web dashboard
HOME=/Users/amitpatra/Documents/Investment streamlit run app.py --server.port=8501
```

Access locally at `http://localhost:8501`.
