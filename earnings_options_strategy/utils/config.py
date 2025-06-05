"""
Configuration settings for the earnings options strategy.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
FMP_API_KEY = os.getenv('FMP_API_KEY')
QUARTR_API_KEY = os.getenv('QUARTR_API_KEY')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
IBKR_ACCOUNT = os.getenv('IBKR_ACCOUNT')
IBKR_PASSWORD = os.getenv('IBKR_PASSWORD')

# Trading Parameters
MAX_POSITION_SIZE = 0.05  # Maximum 5% of portfolio per trade
MIN_LIQUIDITY = 100  # Minimum daily options volume
MAX_IV_RANK = 80  # Maximum IV rank for entry
MIN_DAYS_TO_EXPIRY = 30
MAX_DAYS_TO_EXPIRY = 45

# Signal Weights
SIGNAL_WEIGHTS = {
    'analyst': 0.2,
    'tone': 0.15,
    'insider': 0.15,
    'retail': 0.1,
    'news': 0.1,
    'options': 0.2,
    'historical': 0.1
}

# Risk Management
STOP_LOSS_PCT = 0.15  # 15% stop loss
TAKE_PROFIT_PCT = 0.30  # 30% take profit
MAX_DAILY_TRADES = 5
MAX_OPEN_POSITIONS = 10

# Data Storage
DATA_DIR = 'data'
LOG_DIR = 'logs'

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True) 