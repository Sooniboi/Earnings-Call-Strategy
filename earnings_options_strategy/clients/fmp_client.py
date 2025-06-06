import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
from dotenv import load_dotenv

class FMPClient:
    """Client for interacting with Financial Modeling Prep API."""
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    BASE_URL_V4 = "https://financialmodelingprep.com/api/v4"
    
    def __init__(self, api_key: Optional[str] = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise ValueError("FMP API key not provided and FMP_API_KEY environment variable not set")

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        params = params or {}
        params["apikey"] = self.api_key
        print(f"\nMaking request to: {url}")
        print(f"With params: {params}")
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            response.raise_for_status()
        data = response.json()
        print(f"Response data: {data}")
        return data

    def get_next_earnings_date(self, ticker: str) -> Optional[datetime]:
        """Get the next earnings date for a ticker."""
        url = f"{self.BASE_URL}/earning_calendar"
        params = {"symbol": ticker}
        data = self._make_request(url, params)
        if not data:
            return None
        earnings_dates = pd.DataFrame(data)
        earnings_dates['date'] = pd.to_datetime(earnings_dates['date'])
        future_dates = earnings_dates[earnings_dates['date'] > datetime.now()]
        if future_dates.empty:
            return None
        return future_dates.iloc[0]['date']

    def get_insider_trades(self, ticker: str, limit: int = 30) -> List[Dict]:
        """Get recent insider trading activity for a ticker."""
        url = f"{self.BASE_URL_V4}/insider-trading"
        params = {"symbol": ticker, "limit": limit}
        return self._make_request(url, params)

    def get_historical_earnings(self, ticker: str, limit: int = 4) -> List[Dict]:
        """Get historical earnings data for a ticker."""
        url = f"{self.BASE_URL}/historical/earning_calendar/{ticker}"
        params = {"limit": limit}
        return self._make_request(url, params)

    def get_earnings_surprise(self, ticker: str, limit: int = 4) -> List[Dict]:
        """Get historical earnings surprise data for a ticker."""
        url = f"{self.BASE_URL}/earnings-surprises/{ticker}"
        params = {"limit": limit}
        return self._make_request(url, params) 