import logging

def setup_logging(name: str) -> logging.Logger:
    """
    Set up logging for a module.
    
    Args:
        name (str): Name of the module
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger 