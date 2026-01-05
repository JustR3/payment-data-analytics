"""
Payment Intelligence Suite

A production-grade analytics suite for subscription payment data analysis.
Built with DuckDB and Streamlit for the Proton Data Analyst portfolio.
"""

__version__ = "0.1.0"
__author__ = "JustR3"

from .data_generator import PaymentDataGenerator
from .etl_logic import PaymentAnalytics

__all__ = ["PaymentDataGenerator", "PaymentAnalytics"]
