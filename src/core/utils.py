from datetime import datetime


def format_timestamp(timestamp: int) -> str:
    """Format a Unix timestamp to human readable date.
    
    Args:
        timestamp: Unix timestamp.
        
    Returns:
        Formatted date string.
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")