"""
Data Download and Caching Module for NIFTY 50 Daily Historical Data.
Fetches daily OHLCV from 2015-01-01 to present (~11.5 years).
Enables 10-Year Development (2015-2025) and 1-Year Validation (2025-2026).
"""

import os
import sys
from datetime import datetime
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(DATA_DIR, "nifty50_10y_daily.csv")
TICKER = "^NSEI"

# Partition Cutoff Dates
DEVELOPMENT_START = "2015-01-01"
VALIDATION_SPLIT_DATE = "2025-09-01"  # 10 years development: 2015-01 to 2025-08; 1 year validation: 2025-09 onwards


def download_nifty50_data(
    start_date: str = DEVELOPMENT_START,
    output_path: str = DEFAULT_CSV_PATH,
    force_download: bool = False,
) -> pd.DataFrame:
    """
    Downloads NIFTY 50 daily index data starting from 2015-01-01.
    Caches the data to CSV to allow fast offline loading.
    """
    if os.path.exists(output_path) and not force_download:
        df = pd.read_csv(output_path, index_col=0, parse_dates=True)
        # Check if the cached file already starts from 2015
        if not df.empty and df.index[0].strftime("%Y-%m-%d") <= "2015-01-15":
            print(f"Loaded cached data from {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')} ({len(df)} bars).")
            return df
        print("Cached data starts later than 2015. Re-fetching full history from 2015...")

    print(f"Fetching daily data for {TICKER} from {start_date} to present from Yahoo Finance...")
    try:
        import yfinance as yf
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        ticker = yf.Ticker(TICKER)
        df = ticker.history(start=start_date, end=end_date, interval="1d")

        if df.empty:
            raise ValueError(f"No data returned for ticker {TICKER}")

        # Clean columns and index
        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df = df.dropna(subset=["Close"])
        df = df.sort_index()

        # Filter valid positive prices
        df = df[(df["Close"] > 0) & (df["High"] > 0) & (df["Low"] > 0) & (df["Open"] > 0)]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path)
        print(f"Successfully saved {len(df)} rows to {output_path}")
        print(f"Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
        return df

    except Exception as e:
        print(f"Error downloading from Yahoo Finance: {e}")
        if os.path.exists(output_path):
            print(f"Falling back to existing file at {output_path}")
            return pd.read_csv(output_path, index_col=0, parse_dates=True)
        raise e


if __name__ == "__main__":
    force = "--force" in sys.argv
    df = download_nifty50_data(force_download=force)
    print("\nDataset Summary:")
    print(f"Start: {df.index[0].strftime('%Y-%m-%d')} | End: {df.index[-1].strftime('%Y-%m-%d')} | Total Bars: {len(df)}")
