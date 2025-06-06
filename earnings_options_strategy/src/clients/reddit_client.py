import os
import time
import logging
from datetime import datetime, timedelta
import praw
from typing import List, Dict, Optional
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditClient:
    """Client for interacting with Reddit API for retail sentiment analysis."""
    
    def __init__(self):
        """Initialize Reddit client with API credentials."""
        load_dotenv()
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'earnings_analysis_bot v1.0')
        
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Reddit API credentials not found in environment variables")
        
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        
        # Relevant subreddits for stock discussion
        self.subreddits = [
            'wallstreetbets',
            'stocks',
            'investing',
            'stockmarket',
            'options'
        ]
        
        # Rate limiting
        self.rate_limit = 60  # requests per minute
        self.request_times = []
    
    def _handle_rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        # Remove timestamps older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 60 - (current_time - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.request_times.append(current_time)
    
    def get_stock_posts(self, 
                       symbol: str, 
                       days: int = 7, 
                       limit: int = 100) -> pd.DataFrame:
        """
        Fetch posts about a stock from relevant subreddits.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            days: Number of days to look back (default: 7)
            limit: Maximum number of posts per subreddit (default: 100)
            
        Returns:
            DataFrame containing posts with columns:
            - title: Post title
            - score: Post score (upvotes - downvotes)
            - created_utc: Creation timestamp
            - num_comments: Number of comments
            - subreddit: Subreddit name
            - url: Post URL
            - selftext: Post content
        """
        logger.info(f"Fetching Reddit posts about {symbol}")
        
        posts = []
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        for subreddit_name in self.subreddits:
            self._handle_rate_limit()
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                search_query = f"{symbol} OR ${symbol}"
                
                for post in subreddit.search(search_query, limit=limit, sort='relevance'):
                    if datetime.fromtimestamp(post.created_utc) >= cutoff_time:
                        posts.append({
                            'title': post.title,
                            'score': post.score,
                            'created_utc': datetime.fromtimestamp(post.created_utc),
                            'num_comments': post.num_comments,
                            'subreddit': subreddit_name,
                            'url': post.url,
                            'selftext': post.selftext,
                            'author': post.author.name if post.author else '[deleted]'
                        })
            except Exception as e:
                logger.error(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
        
        df = pd.DataFrame(posts)
        if not df.empty:
            df = df.sort_values('created_utc', ascending=False)
            logger.info(f"Successfully fetched {len(df)} posts about {symbol}")
        else:
            logger.warning(f"No posts found about {symbol}")
        
        return df
    
    def get_post_comments(self, post_url: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch comments from a specific post.
        
        Args:
            post_url: URL of the Reddit post
            limit: Maximum number of comments to fetch (default: 100)
            
        Returns:
            DataFrame containing comments with columns:
            - body: Comment text
            - score: Comment score
            - created_utc: Creation timestamp
            - author: Comment author
        """
        logger.info(f"Fetching comments from post: {post_url}")
        
        try:
            submission = self.reddit.submission(url=post_url)
            submission.comments.replace_more(limit=0)  # Remove MoreComments objects
            
            comments = []
            for comment in submission.comments.list()[:limit]:
                comments.append({
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': datetime.fromtimestamp(comment.created_utc),
                    'author': comment.author.name if comment.author else '[deleted]'
                })
            
            df = pd.DataFrame(comments)
            if not df.empty:
                df = df.sort_values('created_utc', ascending=False)
                logger.info(f"Successfully fetched {len(df)} comments")
            else:
                logger.warning("No comments found")
            
            return df
        except Exception as e:
            logger.error(f"Error fetching comments: {str(e)}")
            return pd.DataFrame()
    
    def get_retail_sentiment(self, 
                           symbol: str, 
                           days: int = 7) -> Dict:
        """
        Analyze retail sentiment from Reddit posts and comments.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            days: Number of days to analyze (default: 7)
            
        Returns:
            Dictionary containing sentiment analysis including:
            - total_posts: Total number of posts
            - total_comments: Total number of comments
            - engagement_score: Combined score of posts and comments
            - top_posts: Most upvoted posts
            - subreddit_distribution: Posts by subreddit
            - sentiment_trend: Sentiment trend over time
        """
        logger.info(f"Analyzing retail sentiment for {symbol}")
        
        # Get posts
        posts_df = self.get_stock_posts(symbol, days=days)
        if posts_df.empty:
            return {}
        
        # Calculate engagement metrics
        total_posts = len(posts_df)
        total_comments = posts_df['num_comments'].sum()
        engagement_score = posts_df['score'].sum() + posts_df['num_comments'].sum()
        
        # Get top posts
        top_posts = posts_df.nlargest(5, 'score')[['title', 'score', 'num_comments', 'subreddit', 'url']]
        
        # Analyze subreddit distribution
        subreddit_dist = posts_df['subreddit'].value_counts().to_dict()
        
        # Calculate daily engagement
        posts_df['date'] = posts_df['created_utc'].dt.date
        daily_engagement = posts_df.groupby('date').agg({
            'score': 'sum',
            'num_comments': 'sum'
        }).to_dict('index')
        
        sentiment = {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'engagement_score': engagement_score,
            'top_posts': top_posts.to_dict('records'),
            'subreddit_distribution': subreddit_dist,
            'daily_engagement': daily_engagement,
            'sentiment_trend': self._calculate_sentiment_trend(posts_df)
        }
        
        return sentiment
    
    def _calculate_sentiment_trend(self, posts_df: pd.DataFrame) -> Dict:
        """
        Calculate sentiment trend from post titles and content.
        This is a simple implementation that can be enhanced with proper sentiment analysis.
        
        Args:
            posts_df: DataFrame containing posts
            
        Returns:
            Dictionary containing sentiment trend data
        """
        # Group by date and calculate average score
        daily_scores = posts_df.groupby(posts_df['created_utc'].dt.date)['score'].mean()
        
        # Calculate trend
        trend = {
            'dates': daily_scores.index.strftime('%Y-%m-%d').tolist(),
            'scores': daily_scores.values.tolist(),
            'trend': 'positive' if daily_scores.iloc[-1] > daily_scores.iloc[0] else 'negative'
        }
        
        return trend 