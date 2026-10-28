"""
Scrapers Package for Hamara Sheher / RaipurTales.
Modular, resilient multi-source event aggregation system.
"""

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.deduplicator import EventDeduplicator
from scrapers.event_validator import EventValidator
from scrapers.supabase_repository import SupabaseRepository

__all__ = [
    "BaseConnector",
    "EventNormalizer",
    "EventDeduplicator",
    "EventValidator",
    "SupabaseRepository",
]

