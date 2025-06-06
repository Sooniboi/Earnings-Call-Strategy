from clients.reddit_client import RedditClient
from datetime import datetime, timedelta
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def main():
    client = RedditClient()
    
    # Test stock posts
    print("\nTesting Reddit posts for ORCL:")
    posts_df = client.get_stock_posts("ORCL", days=7)
    print(f"\nFound {len(posts_df)} posts")
    if not posts_df.empty:
        print("\nLatest posts:")
        display_cols = ['created_utc', 'title', 'score', 'num_comments', 'subreddit']
        print(posts_df[display_cols].head())
        
        # Analyze subreddit distribution
        print("\nPosts by subreddit:")
        subreddit_counts = posts_df['subreddit'].value_counts()
        print(subreddit_counts)
        
        # Get comments for the top post
        if len(posts_df) > 0:
            top_post = posts_df.iloc[0]
            print(f"\nFetching comments for top post: {top_post['title']}")
            comments_df = client.get_post_comments(top_post['url'])
            if not comments_df.empty:
                print(f"\nFound {len(comments_df)} comments")
                print("\nTop comments:")
                print(comments_df[['created_utc', 'score', 'body']].head())
    
    # Test retail sentiment analysis
    print("\nTesting retail sentiment analysis for ORCL:")
    sentiment = client.get_retail_sentiment("ORCL", days=7)
    if sentiment:
        print("\nSentiment Analysis Summary:")
        print(f"Total posts: {sentiment['total_posts']}")
        print(f"Total comments: {sentiment['total_comments']}")
        print(f"Engagement score: {sentiment['engagement_score']}")
        
        print("\nTop posts:")
        for i, post in enumerate(sentiment['top_posts'], 1):
            print(f"\n{i}. {post['title']}")
            print(f"   Score: {post['score']}")
            print(f"   Comments: {post['num_comments']}")
            print(f"   Subreddit: r/{post['subreddit']}")
        
        print("\nSubreddit distribution:")
        for subreddit, count in sentiment['subreddit_distribution'].items():
            print(f"r/{subreddit}: {count} posts")
        
        print("\nDaily engagement:")
        for date, metrics in sorted(sentiment['daily_engagement'].items()):
            print(f"{date}: {metrics['score']} score, {metrics['num_comments']} comments")
        
        print("\nSentiment trend:")
        print(f"Overall trend: {sentiment['sentiment_trend']['trend']}")
        print("Daily scores:")
        for date, score in zip(sentiment['sentiment_trend']['dates'], 
                             sentiment['sentiment_trend']['scores']):
            print(f"{date}: {score:.2f}")

if __name__ == "__main__":
    main() 