"""
Tests for the composite score module.
"""
import pytest
from ...signal_processing.composite_score import CompositeSignalProcessor

def test_composite_score_calculation():
    """Test composite score calculation."""
    processor = CompositeSignalProcessor()
    
    # Test with valid signals
    signals = {
        'analyst': 0.5,
        'tone': 0.3,
        'insider': -0.2,
        'retail': 0.1,
        'news': 0.4,
        'options': -0.3,
        'historical': 0.2
    }
    
    score = processor.compute_composite_score(signals)
    assert -1 <= score <= 1
    
def test_missing_signals():
    """Test handling of missing signals."""
    processor = CompositeSignalProcessor()
    
    # Test with missing signal
    signals = {
        'analyst': 0.5,
        'tone': 0.3,
        'insider': -0.2,
        'retail': 0.1,
        'news': 0.4,
        'options': -0.3
        # Missing 'historical'
    }
    
    with pytest.raises(ValueError):
        processor.compute_composite_score(signals)
        
def test_invalid_signal_values():
    """Test handling of invalid signal values."""
    processor = CompositeSignalProcessor()
    
    # Test with out-of-range signal
    signals = {
        'analyst': 1.5,  # Should be <= 1
        'tone': 0.3,
        'insider': -0.2,
        'retail': 0.1,
        'news': 0.4,
        'options': -0.3,
        'historical': 0.2
    }
    
    with pytest.raises(ValueError):
        processor.validate_signals(signals)
        
def test_signal_validation():
    """Test signal validation."""
    processor = CompositeSignalProcessor()
    
    # Test with valid signals
    signals = {
        'analyst': 0.5,
        'tone': 0.3,
        'insider': -0.2,
        'retail': 0.1,
        'news': 0.4,
        'options': -0.3,
        'historical': 0.2
    }
    
    assert processor.validate_signals(signals) is True 