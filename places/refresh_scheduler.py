"""
Places Pipeline Scheduler & Coordinator.
Executes configured source connectors, normalization, validation, deduplication,
dual-sync persistence (Supabase + local JSON), and data quality reporting.
Supports dry-run mode and multi-city targeting.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from places.official_tourism_connector import OfficialTourismConnector
from places.place_discovery_connector import PlaceDiscoveryConnector
from places.restaurant_connector import RestaurantConnector
from places.local_guide_connector import LocalGuideConnector

from places.place_normalizer import PlaceNormalizer
from places.place_validator import PlaceValidator
from places.place_deduplicator import PlaceDeduplicator
from places.place_repository import PlaceRepository
from places.source_registry import SourceRegistryManager
from places.quality_reporter import QualityReporter

logger = logging.getLogger("PlacePipelineScheduler")


class PlacePipelineScheduler:
    """
    Coordinates multi-source place ingestion for designated cities.
    """

    def __init__(self, city_id: str = "raipur", config_dir: str = "cities"):
        self.city_id = city_id.lower()
        self.config_dir = config_dir
        self.city_config = self.load_city_config()
        self.registry = SourceRegistryManager()
        self.repository = PlaceRepository()

        # Connector registry
        self.available_connectors = {
            "cg_tourism": OfficialTourismConnector(),
            "osm_places": PlaceDiscoveryConnector(),
            "raipur_eateries_registry": RestaurantConnector(),
            "local_experiences": LocalGuideConnector()
        }

    def load_city_config(self) -> Dict[str, Any]:
        path = os.path.join(self.config_dir, f"{self.city_id}.json")
        if not os.path.exists(path):
            logger.warning(f"City configuration not found at {path}. Using default settings.")
            return {"city_id": self.city_id, "display_name": self.city_id.capitalize()}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error(f"Error reading city config {path}: {exc}")
            return {"city_id": self.city_id}

    def run(self, dry_run: bool = False) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        print("=================================================================")
        print(f"   Hamara Sheher — Place Discovery & Ingestion Engine v1.0       ")
        print(f"   Target City: {self.city_config.get('display_name', self.city_id.upper())} ({self.city_id})")
        print(f"   Execution Mode: {'DRY RUN (No writes)' if dry_run else 'LIVE PERSISTENCE'}")
        print(f"   Timestamp: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=================================================================\n")

        raw_pool: List[Dict[str, Any]] = []
        source_runs = []

        # 1. Harvest from active connectors
        for source_id, connector in self.available_connectors.items():
            try:
                records = connector.run(self.city_id)
                raw_pool.extend(records)
                self.registry.record_fetch_status(source_id, "success", count=len(records))
                source_runs.append({
                    "source_id": source_id,
                    "source_name": connector.name,
                    "status": "success",
                    "records_fetched": len(records)
                })
            except Exception as exc:
                logger.error(f"Connector {connector.name} error: {exc}", exc_info=True)
                self.registry.record_fetch_status(source_id, "failed", error=str(exc))
                source_runs.append({
                    "source_id": source_id,
                    "source_name": connector.name,
                    "status": "failed",
                    "error": str(exc)
                })

        print(f"\n[EXTRACTION COMPLETE] Harvested {len(raw_pool)} candidate records.")

        # 2. Normalization
        normalized_pool = [PlaceNormalizer.normalize(r, self.city_id) for r in raw_pool]

        # 3. Validation
        valid_pool = []
        rejected_count = 0
        for p in normalized_pool:
            is_valid, reason = PlaceValidator.validate(p, self.city_config)
            if is_valid:
                valid_pool.append(p)
            else:
                rejected_count += 1
                logger.info(f"Rejected candidate '{p.get('name')}': {reason}")

        print(f"[VALIDATION COMPLETE] {len(valid_pool)} passed validation ({rejected_count} rejected).")

        # 4. Deduplication
        deduped_places, duplicates_logged = PlaceDeduplicator.deduplicate(valid_pool)
        print(f"[DEDUPLICATION COMPLETE] {len(deduped_places)} unique places ({len(duplicates_logged)} merged).")

        # Breakdown by place type
        counts_by_type = {}
        for p in deduped_places:
            pt = p.get("place_type", "destination")
            counts_by_type[pt] = counts_by_type.get(pt, 0) + 1

        # 5. Persistence
        sync_result = {"supabase_synced": False, "json_synced": False}
        if not dry_run:
            json_file = "places.json" if self.city_id == "raipur" else f"places_{self.city_id}.json"
            sync_result = self.repository.save_all(deduped_places, json_filepath=json_file)

        # 6. Quality Reporting
        report = QualityReporter.generate_report(
            city_id=self.city_id,
            total_raw=len(raw_pool),
            final_places=deduped_places,
            duplicates=duplicates_logged,
            rejected_count=rejected_count,
            source_runs=source_runs,
            output_path="reports/data_quality_report.json"
        )

        print("\n=================================================================")
        print("                   PLACES PIPELINE EXECUTION SUMMARY              ")
        print("=================================================================")
        print(f" Target City               : {self.city_id.upper()}")
        print(f" Total Raw Extracted       : {len(raw_pool)}")
        print(f" Unique Verified Places    : {len(deduped_places)}")
        print("   * Destinations          : " + str(counts_by_type.get("destination", 0)))
        print("   * Food & Eateries       : " + str(counts_by_type.get("eatery", 0)))
        print("   * Experiences/Workshops : " + str(counts_by_type.get("experience", 0)))
        print("\n DATA QUALITY METRICS:")
        print(f"   * Source Attribution    : {report['quality_metrics']['source_attribution_percentage']}%")
        print(f"   * Exact Coordinates     : {report['quality_metrics']['precise_coordinates_percentage']}%")
        print(f"   * Verified Status       : {report['quality_metrics']['verified_status_percentage']}%")
        print(f"   * Complete Addresses    : {report['quality_metrics']['has_complete_address_count']}")
        print("\nPERSISTENCE STATUS:")
        if dry_run:
            print("   * Supabase Sync         : SKIPPED (Dry run)")
            print("   * Local JSON Sync       : SKIPPED (Dry run)")
        else:
            print(f"   * Supabase PostgREST    : {'SUCCESS' if sync_result['supabase_synced'] else 'SKIPPED / PENDING CONFIG'}")
            print(f"   * Local JSON File       : {'SUCCESS' if sync_result['json_synced'] else 'FAILED'}")
        print("=================================================================\n")

        return {
            "places": deduped_places,
            "quality_report": report,
            "sync_result": sync_result
        }


def main():
    city = "raipur"
    dry_run = False
    if "--city" in sys.argv:
        idx = sys.argv.index("--city")
        if idx + 1 < len(sys.argv):
            city = sys.argv[idx + 1]
    if "--dry-run" in sys.argv:
        dry_run = True

    scheduler = PlacePipelineScheduler(city_id=city)
    scheduler.run(dry_run=dry_run)


if __name__ == "__main__":
    main()

