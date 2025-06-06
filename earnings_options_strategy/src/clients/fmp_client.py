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

class FMPClient:
    """Client for interacting with Financial Modeling Prep API."""
    
    def __init__(self):
        """Initialize FMP client with API key and base URL."""
        load_dotenv()
        self.api_key = os.getenv('FMP_API_KEY')
        if not self.api_key:
            raise ValueError("FMP_API_KEY not found in environment variables")
        
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.rate_limit = 300  # requests per minute
        self.request_times = []  # Track request times for rate limiting
        
    def _handle_rate_limit(self):
        """Implement rate limiting to stay within 300 requests per minute."""
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
        params['apikey'] = self.api_key
        
        try:
            logger.info(f"Making request to {url} with params: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Received response with {len(data) if isinstance(data, list) else 1} items")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None
    
    def get_insider_trades(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch insider trading data for the given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            limit: Maximum number of trades to fetch (default: 100)
            
        Returns:
            DataFrame containing insider trading data with the following columns:
            - transactionDate: Date of the transaction
            - transactionType: Type of transaction (e.g., 'Purchase', 'Sale')
            - transactionCode: SEC transaction code
            - transactionShares: Number of shares traded
            - transactionPrice: Price per share
            - transactionValue: Total value of transaction
            - sharesOwnedFollowingTransaction: Shares owned after transaction
            - securityName: Name of the security
            - reportingCik: CIK of the reporting person
            - reportingName: Name of the reporting person
            - reportingTitle: Title of the reporting person
        """
        logger.info(f"Fetching insider trading data for {symbol}")
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        insider_data = self._make_request('insider-trading', params)
        if not insider_data:
            logger.error(f"No insider trading data found for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(insider_data)
        if not df.empty:
            # Convert date column
            df['transactionDate'] = pd.to_datetime(df['transactionDate'])
            
            # Sort by date descending
            df = df.sort_values('transactionDate', ascending=False)
            
            # Convert numeric columns
            numeric_cols = ['transactionShares', 'transactionPrice', 'transactionValue', 
                          'sharesOwnedFollowingTransaction']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate additional metrics
            df['days_since_transaction'] = (datetime.now() - df['transactionDate']).dt.days
            
            # Group transactions by type
            transaction_summary = df.groupby('transactionType').agg({
                'transactionValue': ['count', 'sum', 'mean'],
                'transactionShares': ['sum', 'mean']
            }).round(2)
            
            logger.info(f"Successfully fetched {len(df)} insider trading records for {symbol}")
            logger.info("\nTransaction Summary:")
            logger.info(transaction_summary)
        else:
            logger.warning(f"Empty insider trading data received for {symbol}")
        
        return df
    
    def get_historical_earnings(self, symbol: str, years: int = 3) -> pd.DataFrame:
        """
        Fetch historical earnings data for the specified number of years.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            years: Number of years of historical data to fetch (default: 3)
            
        Returns:
            DataFrame containing historical earnings data
        """
        logger.info(f"Fetching {years} years of historical earnings for {symbol}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        # Fetch earnings data
        params = {
            'symbol': symbol,
            'limit': 1200  # Maximum allowed by API
        }
        
        # First try earnings-surprises endpoint
        surprises_data = self._make_request('earnings-surprises', params)
        if not surprises_data:
            logger.error(f"No earnings surprises data found for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(surprises_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            
            # Filter by date
            df = df[df['date'] >= start_date]
            
            # Sort by date descending
            df = df.sort_values('date', ascending=False)
            
            # Convert numeric columns
            numeric_cols = ['actualEarningResult', 'estimatedEarning']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate surprise percentage
            df['surprise_percentage'] = ((df['actualEarningResult'] - df['estimatedEarning']) / 
                                      df['estimatedEarning'] * 100)
            
            # Rename columns to match expected format
            df = df.rename(columns={
                'actualEarningResult': 'eps',
                'estimatedEarning': 'eps_estimate'
            })
            
            logger.info(f"Successfully fetched {len(df)} earnings records for {symbol}")
        else:
            logger.warning(f"Empty earnings data received for {symbol}")
        
        return df
    
    def get_earnings_surprises(self, symbol: str, years: int = 3) -> pd.DataFrame:
        """
        Fetch earnings surprises data for the specified number of years.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            years: Number of years of historical data to fetch (default: 3)
            
        Returns:
            DataFrame containing earnings surprises data
        """
        logger.info(f"Fetching {years} years of earnings surprises for {symbol}")
        
        params = {
            'symbol': symbol,
            'limit': 1200  # Maximum allowed by API
        }
        
        surprises_data = self._make_request('earnings-surprises', params)
        if not surprises_data:
            logger.error(f"No earnings surprises data found for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(surprises_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years * 365)
            
            # Filter by date
            df = df[df['date'] >= start_date]
            
            # Sort by date descending
            df = df.sort_values('date', ascending=False)
            
            # Convert numeric columns
            numeric_cols = ['actualEarningResult', 'estimatedEarning']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate surprise percentage
            df['surprise_percentage'] = ((df['actualEarningResult'] - df['estimatedEarning']) / 
                                      df['estimatedEarning'] * 100)
            
            logger.info(f"Successfully fetched {len(df)} earnings surprises for {symbol}")
        else:
            logger.warning(f"Empty earnings surprises data received for {symbol}")
        
        return df
    
    def get_next_earnings_date(self, symbol: str) -> Optional[datetime]:
        """
        Fetch the next earnings date for the given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'ORCL')
            
        Returns:
            datetime object of next earnings date or None if not found
        """
        logger.info(f"Fetching next earnings date for {symbol}")
        
        params = {
            'from': datetime.now().strftime('%Y-%m-%d'),
            'to': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        }
        
        calendar_data = self._make_request('calendar/earnings', params)
        if not calendar_data:
            logger.error(f"No earnings calendar data found for {symbol}")
            return None
        
        # Find the next earnings date for the symbol
        for entry in calendar_data:
            if entry.get('symbol') == symbol:
                try:
                    next_date = datetime.strptime(entry['date'], '%Y-%m-%d')
                    logger.info(f"Found next earnings date for {symbol}: {next_date}")
                    return next_date
                except (KeyError, ValueError) as e:
                    logger.error(f"Error parsing earnings date: {str(e)}")
                    continue
        
        logger.warning(f"No upcoming earnings date found for {symbol}")
        return None 