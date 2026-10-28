"""
Supabase Repository.
Handles persistent storage of verified event records to Supabase PostgreSQL via PostgREST,
with idempotent upserts and seamless zero-downtime dual-sync to local `events.json`.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("SupabaseRepository")


class SupabaseRepository:
    """
    Manages database synchronization with Supabase and JSON fallback.
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = (supabase_url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.is_configured = bool(self.supabase_url and self.supabase_key)

        if self.is_configured:
            logger.info(f"Supabase repository configured for endpoint: {self.supabase_url}")
        else:
            logger.info("Supabase credentials not detected in environment. Running in JSON-persisted mode.")

    def format_db_record(self, ev: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps an event dictionary into the Supabase database schema columns.
        Ensures proper typing for PostgreSQL TIMESTAMPTZ and NUMERIC fields.
        """
        tags = ev.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        start_dt = ev.get("start_datetime")
        end_dt = ev.get("end_datetime")

        return {
            "id": ev.get("id"),
            "source_name": ev.get("source", "Unknown"),
            "source_event_id": ev.get("source_event_id") or ev.get("id"),
            "original_url": ev.get("link") or ev.get("original_url"),
            "booking_url": ev.get("link") or ev.get("booking_url"),
            "title": ev.get("title"),
            "description": ev.get("description"),
            "city": ev.get("city", "Raipur"),
            "state": ev.get("state", "Chhattisgarh"),
            "venue_name": ev.get("venue"),
            "address": ev.get("address") or ev.get("venue"),
            "latitude": ev.get("latitude") if ev.get("latitude") is not None and ev.get("latitude") != "" else None,
            "longitude": ev.get("longitude") if ev.get("longitude") is not None and ev.get("longitude") != "" else None,
            "start_datetime": start_dt if start_dt and str(start_dt).strip() else None,
            "end_datetime": end_dt if end_dt and str(end_dt).strip() else None,
            "date_human": ev.get("date") or ev.get("date_human"),
            "time_human": ev.get("time") or ev.get("time_human"),
            "timezone": ev.get("timezone", "Asia/Kolkata"),
            "price_min": ev.get("price_min") if ev.get("price_min") is not None and ev.get("price_min") != "" else None,
            "price_max": ev.get("price_max") if ev.get("price_max") is not None and ev.get("price_max") != "" else None,
            "price_type": ev.get("price_type", "undisclosed"),
            "currency": ev.get("currency", "INR"),
            "category": ev.get("category", "Shows"),
            "tags": tags,
            "image_url": ev.get("image") or ev.get("image_url"),
            "first_seen_at": ev.get("first_seen_at"),
            "last_seen_at": ev.get("last_verified_at"),
            "last_verified_at": ev.get("last_verified_at"),
            "verification_status": ev.get("verification_status", "CONFIRMED"),
            "lifecycle_status": ev.get("lifecycle_status", "UPCOMING"),
            "freshness_tier": ev.get("freshness_tier", "MEDIUM")
        }

    def sync_to_supabase(self, events: List[Dict[str, Any]]) -> bool:
        """
        Performs an idempotent batch upsert into the Supabase 'events' table.
        """
        if not self.is_configured or not events:
            return False

        endpoint = f"{self.supabase_url}/rest/v1/events"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal"
        }

        db_records = [self.format_db_record(ev) for ev in events]

        batch_size = 50
        success_count = 0

        for i in range(0, len(db_records), batch_size):
            batch = db_records[i:i + batch_size]
            try:
                res = requests.post(endpoint, headers=headers, json=batch, timeout=12)
                if res.status_code in [200, 201, 204]:
                    success_count += len(batch)
                else:
                    logger.error(f"Supabase upsert failed (Status {res.status_code}): {res.text[:200]}")
            except Exception as exc:
                logger.error(f"Supabase network error during upsert: {exc}")

        logger.info(f"Supabase sync complete: {success_count}/{len(db_records)} records upserted.")
        return success_count > 0

    def sync_to_json(self, events: List[Dict[str, Any]], filepath: str = "events.json") -> bool:
        """
        Saves the verified dataset to events.json for static frontend consumption.
        """
        try:
            frontend_payload = []
            for ev in events:
                frontend_payload.append({
                    "id": ev.get("id"),
                    "title": ev.get("title"),
                    "date": ev.get("date") or ev.get("date_human", "Upcoming Event"),
                    "time": ev.get("time") or ev.get("time_human", "Evening onwards"),
                    "venue": ev.get("venue") or ev.get("venue_name", "Raipur, Chhattisgarh"),
                    "price": ev.get("price", "Book Online"),
                    "source": ev.get("source", "Verified Source"),
                    "image": ev.get("image") or ev.get("image_url"),
                    "link": ev.get("link") or ev.get("original_url", "#"),
                    "category": ev.get("category", "Shows"),
                    "tag": "week",
                    "description": ev.get("description", f"Live event in Raipur: {ev.get('title')}"),
                    "verification_status": ev.get("verification_status", "CONFIRMED"),
                    "freshness_tier": ev.get("freshness_tier", "MEDIUM"),
                    "check_interval_hours": ev.get("check_interval_hours", 12),
                    "first_seen_at": ev.get("first_seen_at"),
                    "last_verified_at": ev.get("last_verified_at"),
                    "next_check_due": ev.get("next_check_due")
                })

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(frontend_payload, f, indent=4, ensure_ascii=False)

            logger.info(f"JSON sync complete: {len(frontend_payload)} events written to {filepath}")
            return True
        except Exception as exc:
            logger.error(f"Failed to write events.json: {exc}")
            return False

    def save_all(self, events: List[Dict[str, Any]], json_filepath: str = "events.json") -> Dict[str, Any]:
        """
        Dual-syncs to Supabase and local JSON.
        """
        supabase_ok = False
        if self.is_configured:
            supabase_ok = self.sync_to_supabase(events)

        json_ok = self.sync_to_json(events, json_filepath)
        return {
            "supabase_synced": supabase_ok,
            "json_synced": json_ok,
            "total_events": len(events)
        }
