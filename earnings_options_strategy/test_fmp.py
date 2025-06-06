from clients.fmp_client import FMPClient
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def main():
    client = FMPClient()
    
    # Test next earnings date
    print("\nTesting next earnings date for ORCL:")
    next_date = client.get_next_earnings_date("ORCL")
    print(f"Next earnings date: {next_date}")
    
    # Test historical earnings (3 years)
    print("\nTesting historical earnings for ORCL (3 years):")
    earnings_df = client.get_historical_earnings("ORCL", years=3)
    print(f"\nFound {len(earnings_df)} earnings records")
    if not earnings_df.empty:
        print("\nLatest earnings data:")
        display_cols = ['date', 'eps', 'eps_estimate', 'surprise_percentage']
        display_cols = [col for col in display_cols if col in earnings_df.columns]
        print(earnings_df[display_cols].head())
        
        # Calculate summary statistics
        print("\nSummary statistics for key metrics:")
        summary_cols = ['eps', 'eps_estimate', 'surprise_percentage']
        summary_cols = [col for col in summary_cols if col in earnings_df.columns]
        print(earnings_df[summary_cols].describe())
        
        # Calculate beat/miss ratio
        beats = len(earnings_df[earnings_df['surprise_percentage'] > 0])
        misses = len(earnings_df[earnings_df['surprise_percentage'] < 0])
        total = len(earnings_df)
        print(f"\nBeat/Miss Ratio: {beats}/{total} beats ({beats/total*100:.1f}%)")
        print(f"Average surprise: {earnings_df['surprise_percentage'].mean():.2f}%")
    
    # Test earnings surprises (3 years)
    print("\nTesting earnings surprises for ORCL (3 years):")
    surprises_df = client.get_earnings_surprises("ORCL", years=3)
    print(f"\nFound {len(surprises_df)} earnings surprises")
    if not surprises_df.empty:
        print("\nLatest earnings surprises:")
        print(surprises_df[['date', 'actualEarningResult', 'estimatedEarning', 'surprise_percentage']].head())
        
        # Calculate summary statistics for surprises
        print("\nSummary statistics for earnings surprises:")
        print(surprises_df['surprise_percentage'].describe())
        
        # Calculate beat/miss ratio
        beats = len(surprises_df[surprises_df['surprise_percentage'] > 0])
        misses = len(surprises_df[surprises_df['surprise_percentage'] < 0])
        total = len(surprises_df)
        print(f"\nBeat/Miss Ratio: {beats}/{total} beats ({beats/total*100:.1f}%)")
        print(f"Average surprise: {surprises_df['surprise_percentage'].mean():.2f}%")
    
    # Test insider trading data
    print("\nTesting insider trading data for ORCL:")
    insider_df = client.get_insider_trades("ORCL", limit=100)
    print(f"\nFound {len(insider_df)} insider trading records")
    if not insider_df.empty:
        print("\nLatest insider trades:")
        display_cols = ['transactionDate', 'transactionType', 'transactionShares', 
                       'transactionPrice', 'transactionValue', 'reportingName', 'reportingTitle']
        display_cols = [col for col in display_cols if col in insider_df.columns]
        print(insider_df[display_cols].head())
        
        # Calculate summary statistics
        print("\nSummary statistics for insider trades:")
        summary_cols = ['transactionShares', 'transactionPrice', 'transactionValue']
        summary_cols = [col for col in summary_cols if col in insider_df.columns]
        print(insider_df[summary_cols].describe())
        
        # Analyze transaction types
        print("\nTransaction type analysis:")
        type_counts = insider_df['transactionType'].value_counts()
        print(type_counts)
        
        # Calculate net insider activity
        buys = insider_df[insider_df['transactionType'].str.contains('Purchase', case=False, na=False)]
        sells = insider_df[insider_df['transactionType'].str.contains('Sale', case=False, na=False)]
        
        total_buy_value = buys['transactionValue'].sum()
        total_sell_value = sells['transactionValue'].sum()
        net_value = total_buy_value - total_sell_value
        
        print(f"\nNet insider activity:")
        print(f"Total buy value: ${total_buy_value:,.2f}")
        print(f"Total sell value: ${total_sell_value:,.2f}")
        print(f"Net value: ${net_value:,.2f}")
        
        # Analyze by reporting person
        print("\nTop insiders by transaction value:")
        person_summary = insider_df.groupby('reportingName').agg({
            'transactionValue': ['count', 'sum'],
            'transactionShares': 'sum'
        }).round(2)
        print(person_summary.sort_values(('transactionValue', 'sum'), ascending=False).head())

if __name__ == "__main__":
    main() 