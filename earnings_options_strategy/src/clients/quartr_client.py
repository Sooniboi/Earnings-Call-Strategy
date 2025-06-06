import os
import time
import logging
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Optional, Tuple
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuartrClient:
    """Client for interacting with Quartr API for earnings call analysis."""
    
    def __init__(self):
        """Initialize Quartr client with API key and base URL."""
        load_dotenv()
        self.api_key = os.getenv('QUARTR_API_KEY')
        if not self.api_key:
            raise ValueError("QUARTR_API_KEY not found in environment variables")
        
        self.base_url = "https://api.quartr.com/v1"  # Replace with actual Quartr API base URL
        self.rate_limit = 60  # requests per minute (adjust based on actual limit)
        self.request_times = []  # Track request times for rate limiting
        
    def _handle_rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        # Remove timestamps older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        if len(self.request_times) >= self.rate_limit:
            # Wait until we can make another request
            sleep_time = 60 - (current_time - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.request_times.append(current_time)
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make API request with rate limiting and error handling."""
        self._handle_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            logger.info(f"Making request to {url}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received response with {len(data) if isinstance(data, list) else 1} items")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None
    
    def get_earnings_call_transcript(self, symbol: str, date: Optional[datetime] = None) -> Dict:
        """
        Fetch earnings call transcript for a specific date or the most recent one.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            date: Specific date to fetch transcript for (optional)
            
        Returns:
            Dictionary containing transcript data including:
            - transcript: Full transcript text
            - participants: List of participants
            - call_date: Date of the call
            - duration: Call duration
        """
        logger.info(f"Fetching earnings call transcript for {symbol}")
        
        params = {
            'symbol': symbol
        }
        if date:
            params['date'] = date.strftime('%Y-%m-%d')
        
        transcript_data = self._make_request('transcripts', params)
        if not transcript_data:
            logger.error(f"No transcript data found for {symbol}")
            return {}
        
        return transcript_data
    
    def get_management_tone(self, symbol: str, date: Optional[datetime] = None) -> Dict:
        """
        Analyze management tone from earnings call.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            date: Specific date to analyze (optional)
            
        Returns:
            Dictionary containing tone analysis including:
            - overall_sentiment: Overall sentiment score
            - ceo_sentiment: CEO's sentiment score
            - cfo_sentiment: CFO's sentiment score
            - key_topics: List of key topics discussed
            - sentiment_by_topic: Sentiment scores by topic
        """
        logger.info(f"Analyzing management tone for {symbol}")
        
        # First get the transcript
        transcript_data = self.get_earnings_call_transcript(symbol, date)
        if not transcript_data:
            return {}
        
        # Make request for tone analysis
        params = {
            'symbol': symbol,
            'transcript_id': transcript_data.get('id')
        }
        
        tone_data = self._make_request('tone-analysis', params)
        if not tone_data:
            logger.error(f"No tone analysis data found for {symbol}")
            return {}
        
        return tone_data
    
    def get_earnings_call_highlights(self, symbol: str, date: Optional[datetime] = None) -> Dict:
        """
        Get key highlights from earnings call.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            date: Specific date to analyze (optional)
            
        Returns:
            Dictionary containing call highlights including:
            - key_points: List of key points discussed
            - guidance: Forward-looking statements
            - risks: Risk factors mentioned
            - opportunities: Growth opportunities discussed
        """
        logger.info(f"Fetching earnings call highlights for {symbol}")
        
        params = {
            'symbol': symbol
        }
        if date:
            params['date'] = date.strftime('%Y-%m-%d')
        
        highlights_data = self._make_request('highlights', params)
        if not highlights_data:
            logger.error(f"No highlights data found for {symbol}")
            return {}
        
        return highlights_data
    
    def get_analyst_qa_summary(self, symbol: str, date: Optional[datetime] = None) -> Dict:
        """
        Get summary of analyst Q&A session.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            date: Specific date to analyze (optional)
            
        Returns:
            Dictionary containing Q&A summary including:
            - questions: List of key questions asked
            - answers: Management's responses
            - analyst_sentiment: Overall analyst sentiment
            - key_concerns: Main concerns raised
        """
        logger.info(f"Fetching analyst Q&A summary for {symbol}")
        
        params = {
            'symbol': symbol
        }
        if date:
            params['date'] = date.strftime('%Y-%m-%d')
        
        qa_data = self._make_request('analyst-qa', params)
        if not qa_data:
            logger.error(f"No Q&A data found for {symbol}")
            return {}
        
        return qa_data
    
    def get_earnings_call_metrics(self, symbol: str, date: Optional[datetime] = None) -> Dict:
        """
        Get comprehensive metrics from earnings call.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            date: Specific date to analyze (optional)
            
        Returns:
            Dictionary containing call metrics including:
            - management_tone: Overall management tone
            - analyst_sentiment: Analyst sentiment
            - guidance_confidence: Confidence in guidance
            - risk_level: Perceived risk level
            - key_metrics: Important metrics discussed
        """
        logger.info(f"Fetching comprehensive earnings call metrics for {symbol}")
        
        # Get all relevant data
        tone_data = self.get_management_tone(symbol, date)
        highlights = self.get_earnings_call_highlights(symbol, date)
        qa_summary = self.get_analyst_qa_summary(symbol, date)
        
        # Combine and analyze the data
        metrics = {
            'management_tone': tone_data.get('overall_sentiment'),
            'analyst_sentiment': qa_summary.get('analyst_sentiment'),
            'guidance_confidence': highlights.get('guidance_confidence'),
            'risk_level': highlights.get('risk_level'),
            'key_metrics': highlights.get('key_metrics', []),
            'key_concerns': qa_summary.get('key_concerns', []),
            'call_date': tone_data.get('call_date')
        }
        
        return metrics 