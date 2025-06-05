# Earnings Options Strategy

An automated trading system that generates options trading signals based on earnings announcements and various market indicators.

## Project Structure

- `data_ingestion/`: Modules for fetching market data, earnings calendars, and sentiment data
- `signal_processing/`: Components for processing raw data into trading signals
- `trade_rules/`: Trading logic and position management rules
- `execution/`: Order execution and position monitoring
- `backtesting/`: Historical testing framework
- `utils/`: Utility functions and configuration
- `scripts/`: Main execution scripts
- `tests/`: Unit tests

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
- Copy `utils/config.example.py` to `utils/config.py`
- Fill in your API keys and configuration settings

## Usage

### Running the Pipeline
```bash
python scripts/run_pipeline.py
```

### Running Backtests
```bash
python scripts/run_backtest.py
```

### Generating Reports
```bash
python scripts/generate_reports.py
```

## Testing
```bash
pytest tests/
```

## License
MIT License 