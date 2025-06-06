from clients.news_client import NewsClient
from datetime import datetime, timedelta
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def main():
    client = NewsClient()
    
    # Test general company news
    print("\nTesting general company news for Oracle:")
    company_news = client.get_company_news("Oracle", days=7)
    print(f"\nFound {len(company_news)} news articles")
    if not company_news.empty:
        print("\nLatest news articles:")
        display_cols = ['publishedAt', 'title', 'source', 'url']
        print(company_news[display_cols].head())
        
        # Analyze news sources
        print("\nNews sources distribution:")
        source_counts = company_news['source'].apply(lambda x: x['name']).value_counts()
        print(source_counts)
    
    # Test earnings-specific news
    print("\nTesting earnings news for ORCL:")
    earnings_news = client.get_earnings_news("ORCL", days_before=3, days_after=3)
    print(f"\nFound {len(earnings_news)} earnings-related articles")
    if not earnings_news.empty:
        print("\nLatest earnings news:")
        display_cols = ['publishedAt', 'title', 'source', 'url']
        print(earnings_news[display_cols].head())
        
        # Analyze earnings news timing
        print("\nEarnings news timing:")
        earnings_news['day'] = earnings_news['publishedAt'].dt.date
        timing_counts = earnings_news['day'].value_counts().sort_index()
        print(timing_counts)
    
    # Test news summary
    print("\nTesting news summary for Oracle/ORCL:")
    summary = client.get_news_summary("ORCL", "Oracle", days=7)
    print("\nNews Summary:")
    print(f"Total articles: {summary['total_articles']}")
    print(f"Earnings-specific articles: {summary['earnings_coverage']}")
    
    print("\nTop general headlines:")
    for i, headline in enumerate(summary['top_headlines'], 1):
        print(f"{i}. {headline}")
    
    print("\nTop earnings headlines:")
    for i, headline in enumerate(summary['earnings_headlines'], 1):
        print(f"{i}. {headline}")
    
    print("\nNews sources:")
    for source in sorted(summary['sources']):
        print(f"- {source}")
    
    print("\nCoverage by date:")
    for date, count in sorted(summary['coverage_by_date'].items()):
        print(f"{date}: {count} articles")

if __name__ == "__main__":
    main() 