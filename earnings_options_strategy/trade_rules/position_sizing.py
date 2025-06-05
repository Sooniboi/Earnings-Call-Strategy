"""
Module for calculating position sizes based on signals and risk parameters.
"""
from ..utils.logging_setup import setup_logging
from ..utils.config import MAX_POSITION_SIZE

logger = setup_logging('position_sizing')

class PositionSizer:
    def __init__(self, portfolio_value):
        """
        Initialize position sizer.
        
        Args:
            portfolio_value (float): Current portfolio value in dollars
        """
        self.portfolio_value = portfolio_value
        self.max_position_size = MAX_POSITION_SIZE
        
    def calculate_position_size(self, signal_strength, volatility):
        """
        Calculate position size based on signal strength and volatility.
        
        Args:
            signal_strength (float): Composite signal score [-1, 1]
            volatility (float): Historical volatility of the underlying
            
        Returns:
            float: Position size in dollars
        """
        try:
            # Convert signal to absolute value for sizing
            signal_magnitude = abs(signal_strength)
            
            # Base position size on signal strength and volatility
            position_size = (
                self.portfolio_value * 
                self.max_position_size * 
                signal_magnitude * 
                (1 / volatility)  # Reduce size for higher volatility
            )
            
            # Ensure position size doesn't exceed maximum
            position_size = min(
                position_size,
                self.portfolio_value * self.max_position_size
            )
            
            logger.info(
                f"Calculated position size: ${position_size:,.2f} "
                f"(signal: {signal_strength:.2f}, vol: {volatility:.2f})"
            )
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            raise
            
    def calculate_contract_quantity(self, position_size, option_price):
        """
        Calculate number of option contracts to trade.
        
        Args:
            position_size (float): Target position size in dollars
            option_price (float): Current option price
            
        Returns:
            int: Number of contracts to trade
        """
        try:
            # Calculate number of contracts (each contract is 100 shares)
            contracts = int(position_size / (option_price * 100))
            
            logger.info(
                f"Calculated contract quantity: {contracts} "
                f"(size: ${position_size:,.2f}, price: ${option_price:.2f})"
            )
            
            return contracts
            
        except Exception as e:
            logger.error(f"Error calculating contract quantity: {str(e)}")
            raise 