"""
Technical Indicators Module.
Vectorized implementation of essential technical indicators using Pandas and NumPy.
"""

import numpy as np
import pandas as pd


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculates Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Calculates Simple Moving Average."""
    return series.rolling(window=period).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculates Relative Strength Index (RSI) using Wilder's smoothing.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's smoothing: alpha = 1 / period
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates Average True Range (ATR) using Wilder's smoothing.
    Expects High, Low, Close in df.
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, adjust=False).mean()
    return atr


def calculate_bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0):
    """
    Calculates Bollinger Bands (Middle, Upper, Lower).
    """
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * num_std)
    lower = middle - (std * num_std)
    return middle, upper, lower


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    Calculates MACD line, Signal line, and MACD Histogram.
    """
    fast_ema = calculate_ema(series, fast)
    slow_ema = calculate_ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    """
    Calculates Supertrend indicator line and direction.
    Returns: supertrend (pd.Series), direction (pd.Series: 1 for Bullish, -1 for Bearish)
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    atr = calculate_atr(df, period)

    hl2 = (high + low) / 2.0
    basic_upper = hl2 + (multiplier * atr)
    basic_lower = hl2 - (multiplier * atr)

    n = len(df)
    upper_band = np.zeros(n)
    lower_band = np.zeros(n)
    supertrend = np.zeros(n)
    direction = np.zeros(n)  # 1: Up, -1: Down

    close_arr = close.values
    bu_arr = basic_upper.values
    bl_arr = basic_lower.values

    upper_band[0] = bu_arr[0]
    lower_band[0] = bl_arr[0]
    direction[0] = 1
    supertrend[0] = lower_band[0]

    for i in range(1, n):
        # Lower band logic
        if bl_arr[i] > lower_band[i - 1] or close_arr[i - 1] < lower_band[i - 1]:
            lower_band[i] = bl_arr[i]
        else:
            lower_band[i] = lower_band[i - 1]

        # Upper band logic
        if bu_arr[i] < upper_band[i - 1] or close_arr[i - 1] > upper_band[i - 1]:
            upper_band[i] = bu_arr[i]
        else:
            upper_band[i] = upper_band[i - 1]

        # Direction logic
        if direction[i - 1] == 1:
            if close_arr[i] < lower_band[i]:
                direction[i] = -1
                supertrend[i] = upper_band[i]
            else:
                direction[i] = 1
                supertrend[i] = lower_band[i]
        else:
            if close_arr[i] > upper_band[i]:
                direction[i] = 1
                supertrend[i] = lower_band[i]
            else:
                direction[i] = -1
                supertrend[i] = upper_band[i]

    return pd.Series(supertrend, index=df.index), pd.Series(direction, index=df.index)
