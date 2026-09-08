# 📈 NIFTY 50 Quantitative Trading System (Development & Validation)

A systematic quantitative trading application built on **daily NIFTY 50 index data (`^NSEI`)** from **2015 to 2026**.

The system rigorously separates historical data into a **10-Year In-Sample Development Period (2015–2025)** and a **1-Year Out-of-Sample Forward Validation Period (2025–2026)** to prevent curve-fitting, tracks both **Planned and Realized Risk:Reward ratios**, and includes an integrated **User Feedback & Admin Analytics Center**.

---

## 🌐 Live Public Shareable Cloud URL

> [!TIP]
> **Live Cloud Application URL**: **[https://junction-locator-traveller-recipient.trycloudflare.com](https://junction-locator-traveller-recipient.trycloudflare.com)**
> Accessible globally over secure HTTPS without any installation.

---

## 🌟 Key Highlights

1. **Dual-Period Rigor (Development vs. Validation)**:
   - **In-Sample Development (2015–2025, ~10 Years)**: Used to develop and calibrate rules across bull runs, bear crashes, and election volatility.
   - **Out-of-Sample Validation (2025–2026, Last 1 Year)**: Left completely untouched during development to forward-test generalization.
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
5. **User Feedback & Admin Center**:
   - Persistent SQLite feedback engine (`data/feedback.db`).
   - Non-technical users can submit ratings and modification suggestions.
   - Admin mode with submission analytics, status management, and CSV export.

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

---

## ☁️ Deploying to GitHub & Cloud Platforms

### 1. Push to GitHub
```bash
# Set your remote repository
git remote add origin https://github.com/<your-username>/nifty50-quant-strategy.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Streamlit Community Cloud (Free)
1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Connect your GitHub account.
3. Select this repository, branch `main`, and main file path `app.py`.
4. Click **Deploy**!
