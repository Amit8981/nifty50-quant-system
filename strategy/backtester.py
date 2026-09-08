"""
Backtester Engine Module.
Simulates trading with realistic execution, dynamic Stop Loss & Take Profit,
slippage/brokerage fees, and comprehensive Risk:Reward tracking.
Supports Capital Allocation mode (ETF/Cash) and Risk Budgeting mode (Derivatives).
"""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd


class Trade:
    def __init__(
        self,
        trade_id: int,
        entry_date: pd.Timestamp,
        entry_price: float,
        shares: int,
        stop_loss: float,
        take_profit: float,
        planned_risk_per_share: float,
        planned_reward_per_share: float,
        planned_rr: float,
        side: str = "LONG",
    ):
        self.trade_id = trade_id
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.shares = shares
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.planned_risk_per_share = planned_risk_per_share
        self.planned_reward_per_share = planned_reward_per_share
        self.planned_rr = planned_rr
        self.side = side

        self.exit_date: Optional[pd.Timestamp] = None
        self.exit_price: Optional[float] = None
        self.exit_reason: Optional[str] = None
        self.gross_pnl: float = 0.0
        self.net_pnl: float = 0.0
        self.return_pct: float = 0.0
        self.realized_rr: float = 0.0
        self.holding_days: int = 0
        self.is_open: bool = True

    def close(
        self,
        exit_date: pd.Timestamp,
        exit_price: float,
        exit_reason: str,
        fee_pct: float = 0.0005,
    ):
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.is_open = False
        self.holding_days = max(1, (exit_date - self.entry_date).days)

        cost_basis = self.shares * self.entry_price
        exit_val = self.shares * self.exit_price

        # Transaction cost (brokerage + slippage) applied to entry and exit
        entry_fee = cost_basis * fee_pct
        exit_fee = exit_val * fee_pct
        total_fees = entry_fee + exit_fee

        if self.side == "LONG":
            self.gross_pnl = exit_val - cost_basis
        else:
            self.gross_pnl = cost_basis - exit_val

        self.net_pnl = self.gross_pnl - total_fees
        self.return_pct = (self.net_pnl / cost_basis) * 100.0 if cost_basis > 0 else 0.0

        # Realized R:R relative to initial planned risk
        total_planned_risk = self.planned_risk_per_share * self.shares
        if total_planned_risk > 0:
            self.realized_rr = self.net_pnl / total_planned_risk
        else:
            self.realized_rr = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Trade ID": self.trade_id,
            "Side": self.side,
            "Entry Date": self.entry_date.strftime("%Y-%m-%d"),
            "Entry Price (₹)": round(self.entry_price, 2),
            "Shares": self.shares,
            "Stop Loss (₹)": round(self.stop_loss, 2),
            "Take Profit (₹)": round(self.take_profit, 2),
            "Planned R:R": round(self.planned_rr, 2),
            "Exit Date": self.exit_date.strftime("%Y-%m-%d") if self.exit_date else None,
            "Exit Price (₹)": round(self.exit_price, 2) if self.exit_price else None,
            "Exit Reason": self.exit_reason,
            "Net PnL (₹)": round(self.net_pnl, 2),
            "Return (%)": round(self.return_pct, 2),
            "Realized R:R": round(self.realized_rr, 2),
            "Duration (Days)": self.holding_days,
            "Outcome": "WIN" if self.net_pnl > 0 else "LOSS",
        }


class BacktestEngine:
    def __init__(
        self,
        df: pd.DataFrame,
        initial_capital: float = 1_000_000.0,
        fee_pct: float = 0.0005,  # 0.05% brokerage/slippage
        sizing_mode: str = "capital_alloc",  # "capital_alloc" or "risk_budget"
        allocation_pct: float = 0.95,  # For capital_alloc mode
        risk_per_trade_pct: float = 0.02,  # For risk_budget mode
    ):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.fee_pct = fee_pct
        self.sizing_mode = sizing_mode
        self.allocation_pct = allocation_pct
        self.risk_per_trade_pct = risk_per_trade_pct

    def run(self, strategy_func, **strategy_params) -> Dict[str, Any]:
        """
        Executes backtest with the provided strategy generator function.
        """
        data = strategy_func(self.df.copy(), **strategy_params)

        cash = self.initial_capital
        portfolio_equity = []
        trades: List[Trade] = []
        current_trade: Optional[Trade] = None
        trade_counter = 0

        dates = data.index
        opens = data["Open"].values
        highs = data["High"].values
        lows = data["Low"].values
        closes = data["Close"].values
        signals = data["Signal"].values
        sl_levels = data["Stop_Loss"].values if "Stop_Loss" in data.columns else np.zeros(len(data))
        tp_levels = data["Take_Profit"].values if "Take_Profit" in data.columns else np.zeros(len(data))
        trailing_stops = data["Trailing_Stop"].values if "Trailing_Stop" in data.columns else np.zeros(len(data))

        benchmark_initial_price = opens[0]
        benchmark_shares = self.initial_capital / benchmark_initial_price
        benchmark_equity = []

        for i in range(len(data)):
            current_date = dates[i]
            cur_open = opens[i]
            cur_high = highs[i]
            cur_low = lows[i]
            cur_close = closes[i]

            # Track benchmark Buy & Hold
            benchmark_equity.append(benchmark_shares * cur_close)

            # 1. Check open trade exits first
            if current_trade is not None:
                # Dynamic trailing stop update
                if trailing_stops[i] > 0 and trailing_stops[i] > current_trade.stop_loss:
                    current_trade.stop_loss = trailing_stops[i]

                exit_price = None
                exit_reason = None

                # Gap down below SL on open
                if cur_open <= current_trade.stop_loss:
                    exit_price = cur_open
                    exit_reason = "Stop Loss (Gap)"
                # Gap up above TP on open
                elif current_trade.take_profit > 0 and cur_open >= current_trade.take_profit:
                    exit_price = cur_open
                    exit_reason = "Take Profit (Gap)"
                # Intraday Stop Loss
                elif cur_low <= current_trade.stop_loss:
                    exit_price = current_trade.stop_loss
                    exit_reason = "Stop Loss"
                # Intraday Take Profit
                elif current_trade.take_profit > 0 and cur_high >= current_trade.take_profit:
                    exit_price = current_trade.take_profit
                    exit_reason = "Take Profit"
                # Strategy exit signal (e.g. Mean reversion to 20 SMA / RSI overbought)
                elif signals[i] == -1:
                    exit_price = cur_close
                    exit_reason = "Signal Exit"
                # End of backtest dataset
                elif i == len(data) - 1:
                    exit_price = cur_close
                    exit_reason = "End of Period"

                if exit_price is not None:
                    current_trade.close(
                        exit_date=current_date,
                        exit_price=exit_price,
                        exit_reason=exit_reason,
                        fee_pct=self.fee_pct,
                    )
                    cash += (current_trade.shares * exit_price) - (current_trade.shares * exit_price * self.fee_pct)
                    trades.append(current_trade)
                    current_trade = None

            # 2. Check new trade entry (only if no open position)
            if current_trade is None and i < len(data) - 1 and signals[i] == 1:
                entry_price = cur_close
                sl = sl_levels[i]
                tp = tp_levels[i]

                if sl > 0 and sl < entry_price:
                    risk_per_share = entry_price - sl
                    reward_per_share = (tp - entry_price) if tp > entry_price else (risk_per_share * 1.5)
                    planned_rr = reward_per_share / risk_per_share

                    # Position Sizing
                    total_equity = cash
                    if self.sizing_mode == "capital_alloc":
                        alloc_cash = total_equity * self.allocation_pct
                        shares = int(alloc_cash / (entry_price * (1.0 + self.fee_pct)))
                    else:  # risk_budget
                        capital_at_risk = total_equity * self.risk_per_trade_pct
                        shares_by_risk = int(capital_at_risk / risk_per_share)
                        max_shares = int((total_equity * 0.95) / (entry_price * (1.0 + self.fee_pct)))
                        shares = min(shares_by_risk, max_shares)

                    if shares > 0:
                        trade_counter += 1
                        cost = shares * entry_price * (1.0 + self.fee_pct)
                        cash -= cost
                        current_trade = Trade(
                            trade_id=trade_counter,
                            entry_date=current_date,
                            entry_price=entry_price,
                            shares=shares,
                            stop_loss=sl,
                            take_profit=tp,
                            planned_risk_per_share=risk_per_share,
                            planned_reward_per_share=reward_per_share,
                            planned_rr=planned_rr,
                            side="LONG",
                        )

            # 3. Record daily equity
            if current_trade is not None:
                unrealized_val = current_trade.shares * cur_close
                daily_equity = cash + unrealized_val
            else:
                daily_equity = cash

            portfolio_equity.append(daily_equity)

        equity_df = pd.DataFrame(
            {
                "Strategy_Equity": portfolio_equity,
                "Benchmark_Equity": benchmark_equity,
            },
            index=dates,
        )

        trade_records = [t.to_dict() for t in trades]
        trades_df = pd.DataFrame(trade_records) if trade_records else pd.DataFrame()

        return {
            "equity_df": equity_df,
            "trades_df": trades_df,
            "raw_trades": trades,
            "final_capital": portfolio_equity[-1] if portfolio_equity else self.initial_capital,
            "initial_capital": self.initial_capital,
            "data_with_signals": data,
        }
