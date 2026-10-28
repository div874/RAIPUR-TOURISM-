"""
Source Registry Manager.
Loads, queries, and updates operational source telemetry and permission statuses.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger("SourceRegistry")


class SourceRegistryManager:
    """
    Manages data source definitions, permission tracking, and health metrics.
    """

    def __init__(self, registry_path: str = "config/source_registry.json"):
        self.registry_path = registry_path
        self.sources: List[Dict[str, Any]] = self.load_registry()

    def load_registry(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.registry_path):
            logger.warning(f"Registry file not found at {self.registry_path}")
            return []
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error(f"Failed to load registry: {exc}")
            return []

    def get_sources_for_city(self, city_id: str) -> List[Dict[str, Any]]:
        """Returns enabled sources configured for the designated city."""
        return [
            s for s in self.sources
            if s.get("enabled", False) and city_id.lower() in [c.lower() for c in s.get("supported_cities", [])]
        ]

    def record_fetch_status(self, source_id: str, status: str, count: int = 0, error: Optional[str] = None):
        """Updates last run telemetry for a source."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for s in self.sources:
            if s.get("source_id") == source_id:
                s["last_fetch_status"] = status
                s["last_fetch_count"] = count
                if status == "success":
                    s["last_successful_fetch"] = now_iso
                if error:
                    s["last_error"] = str(error)
                break
        self.save_registry()

    def save_registry(self):
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(self.sources, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.error(f"Failed to save registry updates: {exc}")

