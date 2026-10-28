"""
Place Repository.
Handles persistent storage of places to Supabase PostgreSQL (places table) via PostgREST,
with idempotent upserts and dual-sync to local `places.json`.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("PlaceRepository")


class PlaceRepository:
    """
    Manages database synchronization with Supabase and JSON fallback for permanent places.
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = (supabase_url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.is_configured = bool(self.supabase_url and self.supabase_key)

        if self.is_configured:
            logger.info(f"Place repository configured for endpoint: {self.supabase_url}")
        else:
            logger.info("Supabase credentials not detected in environment. Running in JSON-persisted mode.")

    def format_db_record(self, p: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a normalized place dictionary into the Supabase database schema columns.
        Ensures strict type compliance for numeric and array columns.
        """
        sec_cats = p.get("secondary_categories") or []
        if isinstance(sec_cats, str):
            sec_cats = [c.strip() for c in sec_cats.split(",") if c.strip()]

        source_urls = p.get("source_urls") or []
        if isinstance(source_urls, str):
            source_urls = [source_urls]

        return {
            "id": p.get("id"),
            "city_id": p.get("city_id", "raipur"),
            "name": p.get("name"),
            "slug": p.get("slug"),
            "place_type": p.get("place_type", "destination"),
            "primary_category": p.get("primary_category", "general"),
            "secondary_categories": sec_cats,
            "description": p.get("description"),
            "short_description": p.get("short_description"),
            "address": p.get("address"),
            "neighbourhood": p.get("neighbourhood"),
            "latitude": p.get("latitude"),
            "longitude": p.get("longitude"),
            "price_level": p.get("price_level", "Unknown"),
            "estimated_cost_min": p.get("estimated_cost_min"),
            "estimated_cost_max": p.get("estimated_cost_max"),
            "currency": p.get("currency", "INR"),
            "opening_hours": p.get("opening_hours"),
            "contact_url": p.get("contact_url"),
            "official_website": p.get("official_website"),
            "booking_url": p.get("booking_url"),
            "image_url": p.get("image_url"),
            "source_urls": source_urls,
            "source_provenance": p.get("source_provenance", "verified_curation"),
            "verification_status": p.get("verification_status", "verified"),
            "operating_status": p.get("operating_status", "open")
        }

    def sync_to_supabase(self, places: List[Dict[str, Any]]) -> bool:
        """
        Performs an idempotent batch upsert into Supabase 'places' table.
        """
        if not self.is_configured or not places:
            return False

        endpoint = f"{self.supabase_url}/rest/v1/places"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"
        }

        db_records = [self.format_db_record(p) for p in places]

        batch_size = 50
        success_count = 0

        for i in range(0, len(db_records), batch_size):
            batch = db_records[i:i + batch_size]
            try:
                res = requests.post(endpoint, headers=headers, json=batch, timeout=12)
                if res.status_code in [200, 201, 204]:
                    success_count += len(batch)
                else:
                    logger.error(f"Supabase places upsert failed (Status {res.status_code}): {res.text[:200]}")
            except Exception as exc:
                logger.error(f"Supabase network error during places upsert: {exc}")

        logger.info(f"Supabase places sync: {success_count}/{len(db_records)} records upserted.")
        return success_count > 0

    def sync_to_json(self, places: List[Dict[str, Any]], filepath: str = "places.json") -> bool:
        """
        Saves the verified places dataset to local JSON for zero-downtime frontend consumption.
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(places, f, indent=4, ensure_ascii=False)
            logger.info(f"JSON places sync: {len(places)} places written to {filepath}")
            return True
        except Exception as exc:
            logger.error(f"Failed to write places.json: {exc}")
            return False

    def save_all(self, places: List[Dict[str, Any]], json_filepath: str = "places.json") -> Dict[str, Any]:
        """
        Dual-syncs to Supabase and local JSON.
        """
        supabase_ok = False
        if self.is_configured:
            supabase_ok = self.sync_to_supabase(places)

        json_ok = self.sync_to_json(places, json_filepath)
        return {
            "supabase_synced": supabase_ok,
            "json_synced": json_ok,
            "total_places": len(places)
        }

