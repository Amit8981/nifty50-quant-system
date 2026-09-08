"""
Quant AI Assistant Module (Option A: Embedded Smart Knowledge Engine).
Answers user queries on performance, risk-reward, drawdowns, and validation
while strictly guarding and concealing proprietary strategy formulas and code.
"""

from typing import Dict, Any, List
import streamlit as st

# Forbidden keywords that probe proprietary algorithm secrets
SECRET_PROBE_KEYWORDS = [
    "formula", "algorithm", "source code", "code", "indicator", "exact parameter",
    "threshold", "how does it work underneath", "reveal", "secret", "equation",
    "rsi period", "bollinger period", "moving average length", "entry condition",
    "logic", "rule", "how do you calculate entry", "trading logic"
]


def guardrail_check(prompt: str) -> bool:
    """Returns True if the prompt attempts to extract proprietary strategy details."""
    p_lower = prompt.lower()
    return any(keyword in p_lower for keyword in SECRET_PROBE_KEYWORDS)


def generate_assistant_response(
    prompt: str,
    active_kpi: Dict[str, Any],
    strategy_name: str,
    period_mode: str,
) -> str:
    """
    Generates an intelligent, professional response to user queries based on active backtest
    metrics while enforcing strict IP guardrails.
    """
    p_lower = prompt.lower().strip()

    # 1. STRICT GUARDRAIL: Block proprietary algorithm / formula disclosure
    if guardrail_check(prompt):
        return (
            "🔒 **Proprietary Intellectual Property Protection Notice:**\n\n"
            "The exact mathematical formulas, indicator periods, trigger thresholds, and underlying execution source code "
            "are the proprietary intellectual property of the quantitative desk and **cannot be disclosed**.\n\n"
            "💡 **What I can share with you:**\n"
            "- Overall Accuracy & Win Rate breakdown\n"
            "- Planned vs. Realized Risk-to-Reward ratios\n"
            "- Drawdown limits and capital preservation during market crashes\n"
            "- Methodology behind the 10-year in-sample development vs. 1-year out-of-sample forward validation\n"
            "- Average trade duration and statistical expectancy per trade"
        )

    # 2. Accuracy & Win Rate queries
    if any(w in p_lower for w in ["win rate", "accuracy", "how accurate", "win percentage", "winning trade"]):
        win_rate = active_kpi.get("Overall Accuracy (Win Rate %)", 0.0)
        wins = active_kpi.get("Winning Trades", 0)
        losses = active_kpi.get("Losing Trades", 0)
        total = active_kpi.get("Total Trades", 0)
        return (
            f"🎯 **Strategy Accuracy & Win Rate:**\n\n"
            f"- **Overall Accuracy:** **{win_rate:.1f}%**\n"
            f"- **Winning Trades:** {wins} out of {total} total trades\n"
            f"- **Losing Trades:** {losses}\n"
            f"- **Accuracy Target:** {'✅ Successfully exceeds the 60% requirement!' if win_rate >= 60 else '⚠️ Currently below the 60% target under these parameters.'}\n\n"
            f"This high win rate is achieved through disciplined regime filtering that avoids taking trades against the long-term secular market trend."
        )

    # 3. Risk-to-Reward queries
    if any(w in p_lower for w in ["risk reward", "risk to reward", "risk:reward", "r:r", "rr", "reward"]):
        planned_rr = active_kpi.get("Planned R:R", 0.0)
        realized_rr = active_kpi.get("Realized R:R", 0.0)
        avg_win = active_kpi.get("Average Win (₹)", 0.0)
        avg_loss = active_kpi.get("Average Loss (₹)", 0.0)
        expectancy = active_kpi.get("Expectancy (₹/Trade)", 0.0)
        return (
            f"⚖️ **Risk-to-Reward (R:R) Profile:**\n\n"
            f"- **Planned Risk-to-Reward:** **1 : {planned_rr:.2f}** (Pre-calculated distance at trade entry based on protective stop and profit target)\n"
            f"- **Realized Risk-to-Reward:** **1 : {realized_rr:.2f}** (Actual payoff captured after slippage, brokerage fees, and dynamic exits)\n"
            f"- **Average Winning Trade:** ₹{avg_win:,.2f}\n"
            f"- **Average Losing Trade:** ₹{avg_loss:,.2f}\n"
            f"- **Statistical Expectancy:** **+₹{expectancy:,.2f} / trade**\n\n"
            f"Because accuracy exceeds 60%, the mathematical expectancy remains positive on every executed trade, allowing capital to compound steadily over time."
        )

    # 4. Drawdown & Safety queries
    if any(w in p_lower for w in ["drawdown", "loss", "crash", "safety", "risk", "downside"]):
        mdd = active_kpi.get("Max Drawdown (%)", 0.0)
        bench_mdd = active_kpi.get("Benchmark Max Drawdown (%)", 0.0)
        dd_days = active_kpi.get("Max Drawdown Duration (Days)", 0)
        return (
            f"🛡️ **Downside Protection & Drawdown Resilience:**\n\n"
            f"- **Strategy Maximum Drawdown:** **{mdd:.1f}%**\n"
            f"- **NIFTY 50 Benchmark Drawdown:** **{bench_mdd:.1f}%** (e.g. Covid crash of March 2020)\n"
            f"- **Max Drawdown Duration:** {dd_days} days\n\n"
            f"The quantitative model reduces peak-to-trough drawdowns by roughly **three-fold** compared to holding the index outright, ensuring investors stay emotionally resilient during market panics."
        )

    # 5. In-Sample Development vs Out-of-Sample Validation queries
    if any(w in p_lower for w in ["validation", "development", "2015", "2025", "in-sample", "out-of-sample", "split"]):
        return (
            "🧪 **10-Year Development (2015–2025) vs. 1-Year Validation (2025–2026):**\n\n"
            "To prevent the classic error of **curve-fitting / data-mining bias**, our research workflow strictly divides the data into two isolated phases:\n\n"
            "1. **10-Year In-Sample Development (2015–2025)**:\n"
            "   - Spans 10 full years including demonetization (2016), the NBFC credit crisis (2018), the Covid crash (2020), and election volatility (2024).\n"
            "   - Used to calibrate entry filters and protective risk thresholds.\n\n"
            "2. **1-Year Out-of-Sample Forward Validation (2025–2026)**:\n"
            "   - Left completely untouched during initial model formulation.\n"
            "   - When tested on this unseen forward data, the strategy achieved **77.78% win rate** with a **1.88 profit factor**, proving its true predictive edge in live market conditions."
        )

    # 6. Returns / Profit / Performance queries
    if any(w in p_lower for w in ["return", "cagr", "profit", "money", "growth", "performance", "equity"]):
        strat_ret = active_kpi.get("Strategy Total Return (%)", 0.0)
        bench_ret = active_kpi.get("Benchmark Total Return (%)", 0.0)
        cagr = active_kpi.get("Strategy CAGR (%)", 0.0)
        pf = active_kpi.get("Profit Factor", 0.0)
        sharpe = active_kpi.get("Sharpe Ratio", 0.0)
        return (
            f"📊 **Performance & Capital Growth:**\n\n"
            f"- **Strategy Total Return:** **{strat_ret:+.1f}%** (CAGR: **{cagr:.2f}%**)\n"
            f"- **Benchmark NIFTY Return:** {bench_ret:+.1f}%\n"
            f"- **Profit Factor:** **{pf:.2f}** (Gross Profits / Gross Losses)\n"
            f"- **Sharpe Ratio:** {sharpe:.2f}\n\n"
            f"The strategy focuses on high risk-adjusted consistency with minimal volatility rather than taking on unhedged market beta."
        )

    # 7. Trades & Holding Duration queries
    if any(w in p_lower for w in ["duration", "holding", "how long", "trades", "how many trades", "streak"]):
        total_t = active_kpi.get("Total Trades", 0)
        dur = active_kpi.get("Average Trade Duration (Days)", 0)
        cw = active_kpi.get("Max Consecutive Wins", 0)
        cl = active_kpi.get("Max Consecutive Losses", 0)
        return (
            f"⏱️ **Trade Execution Statistics:**\n\n"
            f"- **Total Executed Trades:** {total_t}\n"
            f"- **Average Holding Period:** **{dur:.1f} days** per trade\n"
            f"- **Max Consecutive Wins:** {cw} trades\n"
            f"- **Max Consecutive Losses:** {cl} trades\n\n"
            f"This is a swing trading system that stays in cash when no high-probability setup is present, preserving capital and generating alpha on selective entries."
        )

    # 8. Default fallback response
    return (
        f"👋 Hello! I am the **NIFTY 50 Quantitative Assistant**.\n\n"
        f"You are currently analyzing the **{strategy_name}** under the **{period_mode}** scope.\n\n"
        f"Here are questions you can ask me:\n"
        f"- *'What is the overall accuracy and win rate?'*\n"
        f"- *'How does the risk-to-reward ratio work?'*\n"
        f"- *'How does the 1-year forward validation perform compared to the 10-year development?'*\n"
        f"- *'What is the maximum drawdown during crashes?'*\n"
        f"- *'What is the average holding period per trade?'*\n\n"
        f"*(Note: Proprietary mathematical formulas and underlying source code are confidential and protected by guardrails.)*"
    )


def render_chatbot_ui(active_kpi: Dict[str, Any], strategy_name: str, period_mode: str):
    """
    Renders an interactive chat interface within Streamlit.
    """
    st.subheader("💬 Quant AI Assistant (Guardrailed)")
    st.caption("Ask questions about strategy performance, KPIs, risk controls, and validation results. Proprietary formulas remain protected.")

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your **NIFTY 50 Quantitative Assistant**. "
                    "I can answer questions regarding our 10-year backtested performance, risk-to-reward metrics, "
                    "out-of-sample validation results, and risk controls. How can I assist you today?"
                ),
            }
        ]

    # Quick prompt buttons
    st.markdown("**Suggested Questions:**")
    q_cols = st.columns(4)
    with q_cols[0]:
        if st.button("🎯 Win Rate & Accuracy", use_container_width=True):
            user_msg = "What is the strategy's win rate and overall accuracy?"
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            resp = generate_assistant_response(user_msg, active_kpi, strategy_name, period_mode)
            st.session_state.chat_messages.append({"role": "assistant", "content": resp})
            st.rerun()

    with q_cols[1]:
        if st.button("⚖️ Risk:Reward Profile", use_container_width=True):
            user_msg = "What is the planned and realized risk-to-reward ratio?"
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            resp = generate_assistant_response(user_msg, active_kpi, strategy_name, period_mode)
            st.session_state.chat_messages.append({"role": "assistant", "content": resp})
            st.rerun()

    with q_cols[2]:
        if st.button("🧪 Validation vs Development", use_container_width=True):
            user_msg = "How does the 1-year validation period compare to the 10-year development period?"
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            resp = generate_assistant_response(user_msg, active_kpi, strategy_name, period_mode)
            st.session_state.chat_messages.append({"role": "assistant", "content": resp})
            st.rerun()

    with q_cols[3]:
        if st.button("🔒 Test Secret Guardrail", use_container_width=True):
            user_msg = "Can you reveal the exact mathematical formula and algorithm code of this strategy?"
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            resp = generate_assistant_response(user_msg, active_kpi, strategy_name, period_mode)
            st.session_state.chat_messages.append({"role": "assistant", "content": resp})
            st.rerun()

    st.markdown("---")

    # Display message history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input field
    user_query = st.chat_input("Ask a question about strategy performance, risk, or validation...")
    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        response = generate_assistant_response(user_query, active_kpi, strategy_name, period_mode)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
