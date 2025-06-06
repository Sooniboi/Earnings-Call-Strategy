import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from earnings_options_strategy.src.clients.ibkr_client import IBKRClient
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def main():
    client = IBKRClient()
    print("Fetching option chain for ORCL...")
    df = client.get_option_chain("ORCL")
    print(f"Received DataFrame with {len(df)} rows.")
    print(df.head())
    client.disconnect()

if __name__ == "__main__":
    main() 