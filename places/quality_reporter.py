"""
Quality Reporter.
Generates machine-readable data quality reports, tracking attribution,
location precision, duplicate rates, and validation audits.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logger = logging.getLogger("QualityReporter")


class QualityReporter:
    """
    Computes data quality scores, audit logs, and diagnostic telemetry for places.
    """

    @staticmethod
    def generate_report(
        city_id: str,
        total_raw: int,
        final_places: List[Dict[str, Any]],
        duplicates: List[Dict[str, Any]],
        rejected_count: int,
        source_runs: List[Dict[str, Any]],
        output_path: str = "reports/data_quality_report.json"
    ) -> Dict[str, Any]:
        """
        Calculates quality metrics and saves a machine-readable audit report.
        """
        total_final = len(final_places)
        has_location_count = sum(1 for p in final_places if p.get("latitude") is not None and p.get("longitude") is not None)
        has_address_count = sum(1 for p in final_places if p.get("address"))
        has_attribution_count = sum(1 for p in final_places if p.get("source_urls") and len(p["source_urls"]) > 0)
        verified_count = sum(1 for p in final_places if p.get("verification_status") == "verified")
        pending_review_count = sum(1 for p in final_places if p.get("verification_status") == "pending_review")

        # By place type
        by_type = {}
        for p in final_places:
            pt = p.get("place_type", "destination")
            by_type[pt] = by_type.get(pt, 0) + 1

        loc_pct = round((has_location_count / total_final) * 100, 1) if total_final else 0
        attr_pct = round((has_attribution_count / total_final) * 100, 1) if total_final else 0
        verif_pct = round((verified_count / total_final) * 100, 1) if total_final else 0

        report = {
            "city_id": city_id,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pipeline_summary": {
                "total_raw_extracted": total_raw,
                "total_unique_saved": total_final,
                "duplicates_merged": len(duplicates),
                "rejected_invalid": rejected_count
            },
            "category_distribution": by_type,
            "quality_metrics": {
                "source_attribution_percentage": attr_pct,
                "precise_coordinates_percentage": loc_pct,
                "verified_status_percentage": verif_pct,
                "pending_review_count": pending_review_count,
                "has_complete_address_count": has_address_count
            },
            "source_execution_telemetry": source_runs,
            "sample_duplicates_merged": duplicates[:10]
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Quality report generated at {output_path}")
        except Exception as exc:
            logger.error(f"Failed to write quality report: {exc}")

        return report

