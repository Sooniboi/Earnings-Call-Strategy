"""
Module for fetching earnings calendar data.
"""
from datetime import datetime, timedelta
from ..clients.fmp_client import FMPClient
from ..utils.logging_setup import setup_logging

logger = setup_logging('earnings_calendar')

class EarningsCalendarFetcher:
    def __init__(self):
        self.client = FMPClient()
        
    def fetch_upcoming_earnings(self, days_ahead=7):
        """
        Fetch upcoming earnings announcements.
        
        Args:
            days_ahead (int): Number of days to look ahead
            
        Returns:
            list: List of dictionaries containing earnings data
        """
        try:
            end_date = datetime.now() + timedelta(days=days_ahead)
            params = {
                'from': datetime.now().strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            earnings_data = self.client._make_request(f"{self.client.BASE_URL}/earning_calendar", params)
            logger.info(f"Fetched {len(earnings_data)} upcoming earnings announcements")
            
            return earnings_data
            
        except Exception as e:
            logger.error(f"Error fetching earnings calendar: {str(e)}")
            raise
            
    def filter_liquid_stocks(self, earnings_data, min_market_cap=1e9):
        """
        Filter earnings data for liquid stocks.
        
        Args:
            earnings_data (list): List of earnings data dictionaries
            min_market_cap (float): Minimum market cap in dollars
            
        Returns:
            list: Filtered list of earnings data
        """
        # TODO: Implement market cap filtering
        return earnings_data 