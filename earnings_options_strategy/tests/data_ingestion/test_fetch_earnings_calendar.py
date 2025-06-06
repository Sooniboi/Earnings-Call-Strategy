import unittest
from datetime import datetime, timedelta
from ...data_ingestion.fetch_earnings_calendar import EarningsCalendarFetcher

class TestEarningsCalendarFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = EarningsCalendarFetcher()

    def test_fetch_upcoming_earnings(self):
        earnings_data = self.fetcher.fetch_upcoming_earnings(days_ahead=7)
        self.assertIsInstance(earnings_data, list)
        # Add more assertions as needed

if __name__ == '__main__':
    unittest.main()
