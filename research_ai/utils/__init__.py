"""
Project Galileo Utilities
=========================

Helper functions and utilities for the research pipeline.
"""

# Import helper functions when they exist
try:
    from .helpers import *
except ImportError:
    pass

# Version info
__version__ = "1.0.0"
__author__ = "Project Galileo Team"