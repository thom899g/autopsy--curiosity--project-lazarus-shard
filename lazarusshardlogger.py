"""
Robust logging system for tracking execution and debugging
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any
import json

class LazarusLogger:
    """Custom logger with structured logging for Lazarus Shard"""
    
    def __init__(self, name: str = "