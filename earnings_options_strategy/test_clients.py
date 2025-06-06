import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from earnings_options_strategy.src.clients.reddit_client import RedditClient
from earnings_options_strategy.src.clients.tradier_client import TradierClient
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def test_reddit_client():
    print("\n=== Testing RedditClient ===")
    try:
        client = RedditClient()
        print("✓ Successfully initialized RedditClient")
        
        # Test stock posts
        print("\nTesting Reddit posts for ORCL:")
        posts_df = client.get_stock_posts("ORCL", days=7)
        print(f"\nFound {len(posts_df)} posts")
        if not posts_df.empty:
            print("\nLatest posts:")
            display_cols = ['created_utc', 'title', 'score', 'num_comments', 'subreddit']
            print(posts_df[display_cols].head())
            
            # Test comments
            if len(posts_df) > 0:
                top_post = posts_df.iloc[0]
                print(f"\nFetching comments for top post: {top_post['title']}")
                comments_df = client.get_post_comments(top_post['url'])
                if not comments_df.empty:
                    print(f"\nFound {len(comments_df)} comments")
                    print("\nTop comments:")
                    print(comments_df[['created_utc', 'score', 'body']].head())
        
        # Test sentiment analysis
        print("\nTesting retail sentiment analysis:")
        sentiment = client.get_retail_sentiment("ORCL", days=7)
        if sentiment:
            print("\nSentiment Analysis Summary:")
            print(f"Total posts: {sentiment['total_posts']}")
            print(f"Total comments: {sentiment['total_comments']}")
            print(f"Engagement score: {sentiment['engagement_score']}")
        
        print("\n✓ RedditClient tests completed successfully")
        return True
    except Exception as e:
        print(f"\n✗ RedditClient test failed: {str(e)}")
        return False

def test_tradier_client():
    print("\n=== Testing TradierClient ===")
    try:
        client = TradierClient()
        print("✓ Successfully initialized TradierClient")
        
        # Test option expirations
        print("\nTesting option expirations for ORCL:")
        expirations = client.get_option_expirations("ORCL")
        print(f"\nAvailable expirations: {expirations}")
        
        if expirations:
            # Test option chain
            print(f"\nTesting option chain for ORCL (expiration: {expirations[0]}):")
            chain_df = client.get_option_chain("ORCL", expirations[0])
            print(f"\nFound {len(chain_df)} options")
            if not chain_df.empty:
                print("\nSample options:")
                display_cols = ['strike', 'option_type', 'last_price', 'bid', 'ask', 
                              'volume', 'open_interest', 'implied_volatility']
                print(chain_df[display_cols].head())
        
        # Test earnings options analysis
        print("\nTesting earnings options analysis:")
        analysis = client.get_earnings_options_analysis("ORCL", days_before=5, days_after=5)
        if analysis:
            print("\nAnalysis Summary:")
            print(f"Overall mean IV: {analysis['implied_volatility']['overall_mean']:.4f}")
            print(f"Put/Call volume ratio: {analysis['put_call_ratio']['volume_ratio']:.2f}")
            print(f"Max pain strike: ${analysis['max_pain']['max_pain_strike']:.2f}")
        
        print("\n✓ TradierClient tests completed successfully")
        return True
    except Exception as e:
        print(f"\n✗ TradierClient test failed: {str(e)}")
        return False

def main():
    print("Starting client tests...")
    
    # Test RedditClient
    reddit_success = test_reddit_client()
    
    # Test TradierClient
    tradier_success = test_tradier_client()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"RedditClient: {'✓ PASSED' if reddit_success else '✗ FAILED'}")
    print(f"TradierClient: {'✓ PASSED' if tradier_success else '✗ FAILED'}")
    
    if reddit_success and tradier_success:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 