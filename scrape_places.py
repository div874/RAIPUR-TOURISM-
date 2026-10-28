"""
=============================================================================
  Hamara Sheher — Place Discovery, Research & Ingestion Pipeline
  Extracts verified destinations, eateries, and experiences for any city.
  Synchronizes to Supabase PostgreSQL (places table) and local places.json.
=============================================================================
"""

import sys
from places.refresh_scheduler import PlacePipelineScheduler


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

