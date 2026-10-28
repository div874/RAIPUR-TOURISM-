"""
Pipeline Scheduler & Ingestion Coordinator.
Coordinates multi-source extraction, adaptive freshness tiering, deduplication,
state machine transitions (NEW, CONFIRMED, UPDATED, EXPIRED), and dual-sync persistence.
"""

import os
import re
import json
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from scrapers.bookmyshow_connector import BookMyShowConnector
from scrapers.allevents_connector import AllEventsConnector
from scrapers.sortmyscene_connector import SortMySceneConnector
from scrapers.district_connector import DistrictConnector
from scrapers.meetup_connector import MeetupConnector
from scrapers.eventsflare_connector import EventsflareConnector
from scrapers.townscript_connector import TownscriptConnector
from scrapers.luma_connector import LumaConnector
from scrapers.highape_connector import HighApeConnector
from scrapers.unstop_connector import UnstopConnector
from scrapers.official_sources_connector import OfficialSourcesConnector
from scrapers.local_organisers_connector import LocalOrganisersConnector

from scrapers.deduplicator import EventDeduplicator
from scrapers.normalizer import EventNormalizer
from scrapers.supabase_repository import SupabaseRepository

logger = logging.getLogger("PipelineScheduler")


def parse_event_date_to_datetime(date_str: str) -> datetime:
    """
    Parses human or ISO date string to a Python datetime object for lifecycle comparisons.
    """
    if not date_str or "upcoming" in str(date_str).lower():
        return datetime.now(timezone.utc) + timedelta(days=7)

    clean_str = re.sub(r'^[A-Za-z]{3},\s*', '', str(date_str).strip())
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            clean_part = clean_str.split("+")[0].split("Z")[0].split(".")[0][:19]
            dt = datetime.strptime(clean_part, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    return datetime.now(timezone.utc) + timedelta(days=7)


def calculate_freshness_tier(event_dt: datetime, now_dt: datetime) -> tuple:
    """
    Assigns re-verification frequency:
    - HIGH (<= 2 days)   : 2 hours
    - MEDIUM (3-14 days) : 12 hours
    - SPARSE (> 14 days) : 72 hours
    """
    days_until = (event_dt.date() - now_dt.date()).days
    if days_until <= 2:
        tier = "HIGH"
        interval_hours = 2
    elif days_until <= 14:
        tier = "MEDIUM"
        interval_hours = 12
    else:
        tier = "SPARSE"
        interval_hours = 72

    next_check = now_dt + timedelta(hours=interval_hours)
    return tier, next_check.strftime("%Y-%m-%dT%H:%M:%SZ"), interval_hours


class EventPipelineScheduler:
    """
    Coordinates end-to-end multi-source event collection.
    """

    def __init__(self, db_filename: str = "events.json"):
        self.db_filename = db_filename
        self.repository = SupabaseRepository()
        self.connectors = [
            BookMyShowConnector(),
            AllEventsConnector(),
            SortMySceneConnector(),
            DistrictConnector(),
            MeetupConnector(),
            EventsflareConnector(),
            TownscriptConnector(),
            LumaConnector(),
            HighApeConnector(),
            UnstopConnector(),
            OfficialSourcesConnector(),
            LocalOrganisersConnector()
        ]

    def load_existing_events(self) -> Dict[str, Dict[str, Any]]:
        """Loads previous run events for incremental state machine tracking."""
        if not os.path.exists(self.db_filename):
            return {}
        try:
            with open(self.db_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            res = {}
            for ev in data:
                fp = EventDeduplicator.generate_fingerprint(ev.get("title", ""), ev.get("date", ""))
                if fp:
                    res[fp] = ev
            return res
        except Exception as exc:
            logger.warning(f"Could not load previous {self.db_filename}: {exc}")
            return {}

    def run(self) -> List[Dict[str, Any]]:
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        print("=================================================================")
        print("   Hamara Sheher Multi-Source Event Aggregation Engine v3.0      ")
        print("   (Supabase Unified Architecture + Zero-Downtime Resilience)    ")
        print(f"   Execution Timestamp: {now_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=================================================================\n")

        existing_map = self.load_existing_events()
        raw_pool: List[Dict[str, Any]] = []

        # 1. Execute all modular connectors independently
        for connector in self.connectors:
            try:
                records = connector.run()
                raw_pool.extend(records)
            except Exception as exc:
                logger.error(f"Connector {connector.name} unhandled error: {exc}", exc_info=True)

        print(f"\n[EXTRACTION COMPLETE] Harvested {len(raw_pool)} raw candidate records across {len(self.connectors)} sources.")

        # 2. Intra-batch & cross-platform deduplication
        deduped_candidates = EventDeduplicator.deduplicate(raw_pool)
        print(f"[DEDUPLICATION COMPLETE] {len(deduped_candidates)} unique candidates after cross-source merging.")

        # 3. State Machine & Freshness Processing
        stats = {
            "new": 0,
            "confirmed": 0,
            "updated": 0,
            "expired": 0,
            "high_tier": 0,
            "medium_tier": 0,
            "sparse_tier": 0
        }

        final_events: List[Dict[str, Any]] = []

        for ev in deduped_candidates:
            raw_title = ev.get("title", "").strip()
            date_str = ev.get("date", "Upcoming Event")
            fp = EventDeduplicator.generate_fingerprint(raw_title, date_str)

            event_dt = parse_event_date_to_datetime(date_str)
            tier, next_check_iso, interval_hours = calculate_freshness_tier(event_dt, now_dt)

            if tier == "HIGH":
                stats["high_tier"] += 1
            elif tier == "MEDIUM":
                stats["medium_tier"] += 1
            else:
                stats["sparse_tier"] += 1

            # Determine verification status
            if fp in existing_map:
                prev = existing_map[fp]
                changed = (
                    prev.get("venue") != ev.get("venue") or
                    prev.get("date") != ev.get("date") or
                    prev.get("time") != ev.get("time") or
                    prev.get("price") != ev.get("price")
                )
                status = "UPDATED" if changed else "CONFIRMED"
                if changed:
                    stats["updated"] += 1
                else:
                    stats["confirmed"] += 1
                first_seen = prev.get("first_seen_at", now_iso)
            else:
                status = "NEW"
                stats["new"] += 1
                first_seen = now_iso

            # Check if event has expired (older than 1 day in the past)
            if event_dt.date() < (now_dt - timedelta(days=1)).date():
                status = "EXPIRED"
                stats["expired"] += 1

            # Construct normalized, schema-compliant record
            entry = {
                "id": f"evt_{fp}",
                "title": raw_title,
                "date": date_str,
                "time": ev.get("time", "Evening onwards"),
                "venue": ev.get("venue", "Raipur, Chhattisgarh"),
                "address": ev.get("address", ev.get("venue", "Raipur, Chhattisgarh")),
                "price": ev.get("price", "Book Online"),
                "price_min": ev.get("price_min"),
                "price_max": ev.get("price_max"),
                "price_type": ev.get("price_type", "undisclosed"),
                "currency": ev.get("currency", "INR"),
                "source": ev.get("source", "Verified Source"),
                "image": ev.get("image", EventNormalizer.get_themed_poster(raw_title)),
                "link": ev.get("link", "#"),
                "category": ev.get("category", "Shows"),
                "tag": "week",
                "description": ev.get("description", f"Verified event in Raipur: {raw_title}"),
                "start_datetime": ev.get("start_datetime"),
                "verification_status": status,
                "lifecycle_status": "COMPLETED" if status == "EXPIRED" else "UPCOMING",
                "freshness_tier": tier,
                "check_interval_hours": interval_hours,
                "first_seen_at": first_seen,
                "last_verified_at": now_iso,
                "next_check_due": next_check_iso
            }

            if status != "EXPIRED":
                final_events.append(entry)

        # 4. Fallback safeguard: if scraper retrieved 0 active items due to upstream maintenance, keep valid existing events
        if not final_events and existing_map:
            logger.warning("Scraped pool yielded 0 items; retaining previous valid events to preserve live website stability.")
            final_events = list(existing_map.values())

        # 5. Dual-Sync Persistence (Supabase + events.json)
        sync_result = self.repository.save_all(final_events, json_filepath=self.db_filename)

        print("\n=================================================================")
        print("                   PIPELINE EXECUTION METRICS                    ")
        print("=================================================================")
        print(f" Total Sources Checked   : {len(self.connectors)}")
        print(f" Active Verified Events  : {len(final_events)}")
        print(f"   - NEW Events Added    : {stats['new']}")
        print(f"   - CONFIRMED Active    : {stats['confirmed']}")
        print(f"   - UPDATED Records     : {stats['updated']}")
        print(f"   - EXPIRED Pruned      : {stats['expired']}")
        print("\n FRESHNESS HEALTH CHECK TIERING:")
        print(f"   - HIGH Tier   (<= 2 days out, 2h check)  : {stats['high_tier']}")
        print(f"   - MEDIUM Tier (3-14 days out, 12h check) : {stats['medium_tier']}")
        print(f"   - SPARSE Tier (> 14 days out, 72h check) : {stats['sparse_tier']}")
        print("\n PERSISTENCE STATUS:")
        print(f"   - Supabase PostgREST Sync : {'SUCCESS' if sync_result['supabase_synced'] else 'SKIPPED / PENDING CONFIG'}")
        print(f"   - Local events.json Sync  : {'SUCCESS' if sync_result['json_synced'] else 'FAILED'}")
        print("=================================================================\n")

        return final_events


def run_pipeline() -> List[Dict[str, Any]]:
    """Global execution entry point."""
    scheduler = EventPipelineScheduler()
    return scheduler.run()


if __name__ == "__main__":
    run_pipeline()

