import unittest
from datetime import datetime
from earnings_options_strategy.clients.fmp_client import FMPClient

class TestFMPClient(unittest.TestCase):
    def setUp(self):
        self.client = FMPClient()

    def test_get_next_earnings_date(self):
        """Test fetching next earnings date for ORCL."""
        next_date = self.client.get_next_earnings_date("ORCL")
        if next_date:
            self.assertIsInstance(next_date, datetime)
            self.assertGreater(next_date, datetime.now())

    def test_get_insider_trades(self):
        """Test fetching insider trades for ORCL."""
        trades = self.client.get_insider_trades("ORCL", limit=5)
        self.assertIsInstance(trades, list)

    def test_get_historical_earnings(self):
        """Test fetching historical earnings for ORCL."""
        earnings = self.client.get_historical_earnings("ORCL", limit=4)
        self.assertIsInstance(earnings, list)
        if earnings:
            self.assertLessEqual(len(earnings), 4)

    def test_get_earnings_surprise(self):
        """Test fetching earnings surprises for ORCL."""
        surprises = self.client.get_earnings_surprise("ORCL", limit=4)
        self.assertIsInstance(surprises, list)
        if surprises:
            self.assertLessEqual(len(surprises), 4)

if __name__ == '__main__':
    unittest.main() 