import os
import time
import logging
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Optional
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsClient:
    """Client for interacting with NewsAPI for news headlines and analysis."""
    
    def __init__(self):
        """Initialize NewsAPI client with API key and base URL."""
        load_dotenv()
        self.api_key = os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")
        
        self.base_url = "https://newsapi.org/v2"
        self.rate_limit = 100  # requests per day (free tier)
        self.request_times = []  # Track request times for rate limiting
        
    def _handle_rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        # Remove timestamps older than 24 hours
        self.request_times = [t for t in self.request_times if current_time - t < 86400]
        
        if len(self.request_times) >= self.rate_limit:
            logger.error("Daily rate limit reached for NewsAPI")
            return False
        
        self.request_times.append(current_time)
        return True
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make API request with rate limiting and error handling."""
        if not self._handle_rate_limit():
            return None
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'X-Api-Key': self.api_key
        }
        
        try:
            logger.info(f"Making request to {url}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received response with {len(data.get('articles', []))} articles")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None
    
    def get_company_news(self, 
                        company_name: str, 
                        days: int = 7, 
                        sort_by: str = 'relevancy',
                        language: str = 'en') -> pd.DataFrame:
        """
        Fetch news articles about a company.
        
        Args:
            company_name: Name of the company (e.g., 'Oracle')
            days: Number of days to look back (default: 7)
            sort_by: Sort order ('relevancy', 'popularity', 'publishedAt')
            language: Language of articles (default: 'en')
            
        Returns:
            DataFrame containing news articles with columns:
            - title: Article title
            - description: Article description
            - url: Article URL
            - publishedAt: Publication date
            - source: News source
            - sentiment: Article sentiment (if available)
        """
        logger.info(f"Fetching news for {company_name} from the past {days} days")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'q': company_name,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'sortBy': sort_by,
            'language': language
        }
        
        news_data = self._make_request('everything', params)
        if not news_data or 'articles' not in news_data:
            logger.error(f"No news data found for {company_name}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(news_data['articles'])
        if not df.empty:
            # Convert date column
            df['publishedAt'] = pd.to_datetime(df['publishedAt'])
            
            # Sort by date descending
            df = df.sort_values('publishedAt', ascending=False)
            
            # Add days since publication
            df['days_since_publication'] = (datetime.now() - df['publishedAt']).dt.days
            
            logger.info(f"Successfully fetched {len(df)} news articles for {company_name}")
        else:
            logger.warning(f"Empty news data received for {company_name}")
        
        return df
    
    def get_earnings_news(self, 
                         symbol: str, 
                         days_before: int = 3, 
                         days_after: int = 3) -> pd.DataFrame:
        """
        Fetch news articles specifically around earnings.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            days_before: Days before earnings to fetch (default: 3)
            days_after: Days after earnings to fetch (default: 3)
            
        Returns:
            DataFrame containing earnings-related news articles
        """
        logger.info(f"Fetching earnings news for {symbol}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_before + days_after)
        
        # Create search query
        query = f'"{symbol}" AND (earnings OR "quarterly results" OR "financial results")'
        
        params = {
            'q': query,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'sortBy': 'publishedAt',
            'language': 'en'
        }
        
        news_data = self._make_request('everything', params)
        if not news_data or 'articles' not in news_data:
            logger.error(f"No earnings news found for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(news_data['articles'])
        if not df.empty:
            # Convert date column
            df['publishedAt'] = pd.to_datetime(df['publishedAt'])
            
            # Sort by date descending
            df = df.sort_values('publishedAt', ascending=False)
            
            # Add days since publication
            df['days_since_publication'] = (datetime.now() - df['publishedAt']).dt.days
            
            logger.info(f"Successfully fetched {len(df)} earnings news articles for {symbol}")
        else:
            logger.warning(f"Empty earnings news data received for {symbol}")
        
        return df
    
    def get_news_summary(self, 
                        symbol: str, 
                        company_name: str, 
                        days: int = 7) -> Dict:
        """
        Get a summary of news coverage for a company.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            company_name: Company name (e.g., 'Oracle')
            days: Number of days to analyze (default: 7)
            
        Returns:
            Dictionary containing news summary including:
            - total_articles: Total number of articles
            - sources: List of news sources
            - top_headlines: Most relevant headlines
            - sentiment_summary: Overall sentiment analysis
            - coverage_trend: Coverage trend over time
        """
        logger.info(f"Generating news summary for {company_name}")
        
        # Get general company news
        company_news = self.get_company_news(company_name, days=days)
        
        # Get earnings-specific news
        earnings_news = self.get_earnings_news(symbol, days_before=3, days_after=3)
        
        # Combine and analyze the data
        summary = {
            'total_articles': len(company_news) + len(earnings_news),
            'sources': list(set(company_news['source'].apply(lambda x: x['name']).tolist() + 
                              earnings_news['source'].apply(lambda x: x['name']).tolist())),
            'top_headlines': company_news['title'].head(5).tolist(),
            'earnings_headlines': earnings_news['title'].head(5).tolist(),
            'coverage_by_date': company_news.groupby(company_news['publishedAt'].dt.date).size().to_dict(),
            'earnings_coverage': len(earnings_news)
        }
        
        return summary 