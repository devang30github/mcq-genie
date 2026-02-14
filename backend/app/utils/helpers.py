"""
Utility functions for MCQ Genie application.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix.
    
    Args:
        prefix: Optional prefix for the ID (e.g., 'test_', 'chat_')
    
    Returns:
        Unique identifier string
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def calculate_expiry_time(minutes: int) -> datetime:
    """
    Calculate expiry datetime from now.
    
    Args:
        minutes: Number of minutes until expiry
    
    Returns:
        Expiry datetime
    """
    return datetime.utcnow() + timedelta(minutes=minutes)


def is_expired(expiry_time: datetime) -> bool:
    """
    Check if a datetime has expired.
    
    Args:
        expiry_time: The expiry datetime to check
    
    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow() > expiry_time


def calculate_score_percentage(correct: int, total: int) -> float:
    """
    Calculate score percentage.
    
    Args:
        correct: Number of correct answers
        total: Total number of questions
    
    Returns:
        Score as percentage (0-100)
    """
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 2)


def serialize_datetime(dt: datetime) -> str:
    """
    Serialize datetime to ISO format string.
    
    Args:
        dt: Datetime object
    
    Returns:
        ISO format datetime string
    """
    return dt.isoformat()


def parse_datetime(dt_str: str) -> datetime:
    """
    Parse ISO format datetime string.
    
    Args:
        dt_str: ISO format datetime string
    
    Returns:
        Datetime object
    """
    return datetime.fromisoformat(dt_str)