import os
import logging
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from ib_insync import IB, Stock, Option, util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IBKRClient:
    """Client for interacting with Interactive Brokers (IBKR) API for options data."""
    def __init__(self):
        load_dotenv()
        self.host = os.getenv('IBKR_HOST', '127.0.0.1')
        self.port = int(os.getenv('IBKR_PORT', 7497))
        self.client_id = int(os.getenv('IBKR_CLIENT_ID', 123))
        self.ib = IB()
        self.connected = False

    def connect(self):
        if not self.connected:
            logger.info(f"Connecting to IBKR at {self.host}:{self.port} (clientId={self.client_id})...")
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            self.connected = True
            logger.info("Connected to IBKR.")

    def disconnect(self):
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR.")

    def get_option_chain(self, symbol: str) -> pd.DataFrame:
        """
        Fetch option contracts for the nearest expiry and strikes within ±20% of the underlying price.
        Returns a DataFrame with contract identifiers, market data, greeks, and underlying data.
        """
        self.connect()
        logger.info(f"Requesting option chain for {symbol}...")
        stock = Stock(symbol, 'SMART', 'USD')
        self.ib.qualifyContracts(stock)
        chains = self.ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
        if not chains:
            logger.warning(f"No option chains found for {symbol}.")
            return pd.DataFrame()
        chain = chains[0]
        logger.info(f"Found {len(chain.expirations)} expirations and {len(chain.strikes)} strikes.")

        # Get underlying price
        underlying_ticker = self.ib.reqTickers(stock)[0]
        underlying_price = underlying_ticker.marketPrice()
        logger.info(f"Underlying price: {underlying_price}")

        # Select nearest expiry
        nearest_expiry = min(chain.expirations)
        logger.info(f"Nearest expiry: {nearest_expiry}")

        # Filter strikes within ±20% of underlying price
        min_strike = underlying_price * 0.8
        max_strike = underlying_price * 1.2
        filtered_strikes = [strike for strike in chain.strikes if min_strike <= strike <= max_strike]
        logger.info(f"Filtered to {len(filtered_strikes)} strikes within ±20% of underlying price.")

        # Get contracts for nearest expiry and filtered strikes
        contracts = []
        for strike in filtered_strikes:
            for right in ['C', 'P']:
                contracts.append(Option(symbol, nearest_expiry, strike, right, 'SMART'))
        logger.info(f"Total contracts to request: {len(contracts)}")

        # Qualify all contracts (get conId etc.)
        qualified_contracts = self.ib.qualifyContracts(*contracts)
        logger.info(f"Qualified {len(qualified_contracts)} contracts.")

        # Request market data snapshots for all contracts
        logger.info("Requesting market data snapshots (this may take a while)...")
        tickers = self.ib.reqTickers(*qualified_contracts)
        logger.info(f"Received {len(tickers)} tickers.")

        # Build DataFrame
        rows = []
        for ticker in tickers:
            c = ticker.contract
            row = {
                'symbol': c.symbol,
                'lastTradeDateOrContractMonth': c.lastTradeDateOrContractMonth,
                'strike': c.strike,
                'right': c.right,
                'bid': ticker.bid,
                'ask': ticker.ask,
                'mid': (ticker.bid + ticker.ask) / 2 if ticker.bid and ticker.ask else None,
                'last': ticker.last,
                'volume': ticker.volume,
                'openInterest': ticker.openInterest,
                'impliedVolatility': ticker.modelGreeks.impliedVol if ticker.modelGreeks else None,
                'delta': ticker.modelGreeks.delta if ticker.modelGreeks else None,
                'gamma': ticker.modelGreeks.gamma if ticker.modelGreeks else None,
                'theta': ticker.modelGreeks.theta if ticker.modelGreeks else None,
                'vega': ticker.modelGreeks.vega if ticker.modelGreeks else None,
                'underlyingLast': underlying_price,
                'underlyingBid': underlying_ticker.bid,
                'underlyingAsk': underlying_ticker.ask
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        logger.info(f"Returning DataFrame with {len(df)} rows.")
        return df 