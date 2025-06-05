"""
Module for managing Interactive Brokers connection and basic operations.
"""
from ib_insync import *
from ..utils.logging_setup import setup_logging
from ..utils.config import IBKR_ACCOUNT, IBKR_PASSWORD

logger = setup_logging('ibkr_connection')

class IBKRConnection:
    def __init__(self):
        """Initialize IBKR connection."""
        self.ib = IB()
        self.connected = False
        
    def connect(self):
        """Establish connection to IBKR TWS/Gateway."""
        try:
            if not self.connected:
                self.ib.connect(
                    '127.0.0.1',  # TWS/Gateway host
                    7497,  # TWS port (7496 for Gateway)
                    clientId=1,
                    readonly=False
                )
                self.connected = True
                logger.info("Connected to IBKR TWS/Gateway")
                
        except Exception as e:
            logger.error(f"Failed to connect to IBKR: {str(e)}")
            raise
            
    def disconnect(self):
        """Disconnect from IBKR TWS/Gateway."""
        try:
            if self.connected:
                self.ib.disconnect()
                self.connected = False
                logger.info("Disconnected from IBKR TWS/Gateway")
                
        except Exception as e:
            logger.error(f"Error disconnecting from IBKR: {str(e)}")
            raise
            
    def get_account_summary(self):
        """
        Get account summary information.
        
        Returns:
            dict: Account summary data
        """
        try:
            if not self.connected:
                self.connect()
                
            account = self.ib.accountSummary()
            summary = {
                item.tag: float(item.value)
                for item in account
                if item.currency == 'USD'
            }
            
            logger.info(f"Retrieved account summary: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting account summary: {str(e)}")
            raise
            
    def get_option_chain(self, symbol, exchange='SMART'):
        """
        Get option chain for a symbol.
        
        Args:
            symbol (str): Stock symbol
            exchange (str): Exchange to use
            
        Returns:
            list: Option contracts
        """
        try:
            if not self.connected:
                self.connect()
                
            stock = Stock(symbol, exchange, 'USD')
            self.ib.qualifyContracts(stock)
            
            chains = self.ib.reqSecDefOptParams(
                stock.symbol,
                '',
                stock.secType,
                stock.conId
            )
            
            logger.info(f"Retrieved option chain for {symbol}")
            return chains
            
        except Exception as e:
            logger.error(f"Error getting option chain: {str(e)}")
            raise 