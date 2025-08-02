import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# ---------- Part 1: Fetch individual expiry option chains ----------
def fetch_option_chain(symbol='AAPL', last_date='2025-08-30'):
    stock = yf.Ticker(symbol)
    expiry_dates = stock.options
    if not expiry_dates:
        return

    cutoff = datetime.strptime(last_date, '%Y-%m-%d')
    selected_expiries = [e for e in expiry_dates if datetime.strptime(e, '%Y-%m-%d') <= cutoff]

    # Save inside ./data folder
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)

    for expiry in selected_expiries:
        try:
            chain = stock.option_chain(expiry)
            calls = chain.calls
            puts = chain.puts
            calls['type'] = 'call'
            puts['type'] = 'put'
            options = pd.concat([calls, puts])
            options['expiry'] = expiry
            options['underlying'] = symbol
            options['fetch_time'] = datetime.now()
            csv_path = os.path.join(data_dir, f"{symbol}_options_{expiry}.csv")
            options.to_csv(csv_path, index=False)
            print(f"Saved: {csv_path}")
        except Exception as e:
            print(f"Failed for expiry {expiry}: {e}")

# ---------- Part 2: Merge all CSVs, clean, and save ----------
def merge_option_csvs(data_dir):
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and "options" in f]
    df_list = []

    for file in all_files:
        path = os.path.join(data_dir, file)
        try:
            df = pd.read_csv(path)

            # Rename if implied volatility is present
            if 'impliedVolatility' in df.columns:
                df = df.rename(columns={"impliedVolatility": "implied_vol"})

                # Drop missing or invalid data
                df = df.dropna(subset=["implied_vol", "strike", "type", "expiry"])
                df = df[df["implied_vol"].between(0.01, 3.0)]

                # Compute time to expiry in years
                expiry_dates = pd.to_datetime(df["expiry"])
                today = pd.to_datetime("today").normalize()
                df["T"] = (expiry_dates - today).dt.days / 365.0
                df = df[df["T"] > 0]

                # Only keep needed columns
                df = df[["strike", "T", "type", "implied_vol"]]
                df["type"] = df["type"].map({"call": 0, "put": 1})
                df = df.dropna()

                df_list.append(df)
        except Exception as e:
            print(f"Skipping {file} due to error: {e}")

    # Merge all cleaned data
    merged_df = pd.concat(df_list, ignore_index=True)

    # Save the final dataset
    output_path = os.path.join(data_dir, "AAPL_iv_merged.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"Merged CSV saved at: {output_path}")
    print(f"Total samples: {merged_df.shape[0]}")
    return merged_df

# ---------- Main Entry ----------
if __name__ == "__main__":
    fetch_option_chain('AAPL', last_date='2025-08-30')
    data_dir = os.path.join(os.getcwd(), "data")
    merged_df = merge_option_csvs(data_dir)
