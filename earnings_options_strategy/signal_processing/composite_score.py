"""
Module for computing composite trading signals.
"""
import numpy as np
from ..utils.logging_setup import setup_logging
from ..utils.config import SIGNAL_WEIGHTS

logger = setup_logging('composite_score')

class CompositeSignalProcessor:
    def __init__(self):
        self.weights = SIGNAL_WEIGHTS
        
    def compute_composite_score(self, signals):
        """
        Compute composite score from individual signals.
        
        Args:
            signals (dict): Dictionary of individual signal scores
            
        Returns:
            float: Composite score between -1 and 1
        """
        try:
            # Validate signals
            missing_signals = set(self.weights.keys()) - set(signals.keys())
            if missing_signals:
                raise ValueError(f"Missing signals: {missing_signals}")
                
            # Compute weighted sum
            composite_score = sum(
                signals[signal] * weight 
                for signal, weight in self.weights.items()
            )
            
            # Normalize to [-1, 1]
            composite_score = np.clip(composite_score, -1, 1)
            
            logger.info(f"Computed composite score: {composite_score:.2f}")
            return composite_score
            
        except Exception as e:
            logger.error(f"Error computing composite score: {str(e)}")
            raise
            
    def validate_signals(self, signals):
        """
        Validate individual signal scores.
        
        Args:
            signals (dict): Dictionary of individual signal scores
            
        Returns:
            bool: True if all signals are valid
        """
        for signal, score in signals.items():
            if not isinstance(score, (int, float)):
                raise ValueError(f"Invalid signal type for {signal}")
            if not -1 <= score <= 1:
                raise ValueError(f"Signal {signal} out of range [-1, 1]")
        return True 