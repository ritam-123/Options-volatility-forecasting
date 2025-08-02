import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def fetch_option_chain(symbol='AAPL', last_date='2025-08-30'):
    stock = yf.Ticker(symbol)
    expiry_dates = stock.options
    if not expiry_dates:
        return

    cutoff = datetime.strptime(last_date, '%Y-%m-%d')
    selected_expiries = [e for e in expiry_dates if datetime.strptime(e, '%Y-%m-%d') <= cutoff]

    project_root = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
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

if __name__ == "__main__":
    fetch_option_chain('AAPL', last_date='2025-08-30')
