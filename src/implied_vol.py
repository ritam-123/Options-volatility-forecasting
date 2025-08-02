import pandas as pd
from scipy.optimize import brentq
from datetime import datetime
import sys
import os
import yfinance as yf

# Add local module path for Black-Scholes
sys.path.append(os.path.dirname(__file__))
from black_scholes import black_scholes_calls, black_scholes_puts

def implied_vol(option_type, market_price, S, K, T, r):
    try:
        if option_type == 'call':
            f = lambda sigma: black_scholes_calls(S, K, T, r, sigma) - market_price
        else:
            f = lambda sigma: black_scholes_puts(S, K, T, r, sigma) - market_price
        return brentq(f, 1e-6, 5)
    except:
        return None

def compute_iv_all_files(data_dir, symbol='AAPL', r=0.05):
    spot_price = yf.Ticker(symbol).info["regularMarketPrice"]
    print(f"Live {symbol} spot price: {spot_price}")

    all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv") and f.startswith(f"{symbol}_options_")]
    final_df_list = []

    for file in all_files:
        input_path = os.path.join(data_dir, file)
        try:
            df = pd.read_csv(input_path)
            if "lastPrice" not in df.columns or "strike" not in df.columns:
                print(f"Skipping {file}, missing necessary columns.")
                continue

            df = df.dropna(subset=["lastPrice", "strike", "expiry", "type"])

            # Ensure correct expiry date format
            expiry_date = pd.to_datetime(df['expiry'].iloc[0])
            T = (expiry_date - datetime.now()).days / 365.0
            if T <= 0:
                print(f"Skipping expired data in {file}")
                continue

            df["T"] = T
            df["implied_vol"] = df.apply(
                lambda row: implied_vol(row["type"], row["lastPrice"], spot_price, row["strike"], T, r),
                axis=1
            )

            df = df.dropna(subset=["implied_vol"])
            df = df[df["implied_vol"].between(0.01, 3.0)]

            # Only keep required columns
            df = df[["strike", "T", "type", "implied_vol"]]
            df["type"] = df["type"].map({"call": 0, "put": 1})
            df = df.dropna()

            final_df_list.append(df)
            print(f"Processed: {file} → {len(df)} rows")

        except Exception as e:
            print(f"Error processing {file}: {e}")

    if final_df_list:
        merged_df = pd.concat(final_df_list, ignore_index=True)
        output_csv = os.path.join(data_dir, f"{symbol}_iv_merged.csv")
        merged_df.to_csv(output_csv, index=False)
        print(f"Saved merged file to: {output_csv}")
    else:
        print("No valid data to save.")

# Main
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    compute_iv_all_files(data_dir, symbol='AAPL', r=0.05)
