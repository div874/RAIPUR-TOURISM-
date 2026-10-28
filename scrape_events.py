"""
=============================================================================
  Hamara Sheher / RaipurTales — Multi-Source Verified Events Scraper & Sync
  Integrates BookMyShow, AllEvents, SortMyScene, District, Meetup, Eventsflare,
  Townscript, Luma, HighApe, Unstop, Official Tourism/Gov, and Local Hubs.
  Synchronizes with Supabase PostgreSQL and local `events.json`.
=============================================================================
"""

import sys
import time
import logging
from scrapers.scheduler import run_pipeline, EventPipelineScheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ScrapeEventsMain")


def main():
    if "--daemon" in sys.argv:
        print("Starting Hamara Sheher Multi-Source Ingestion Pipeline in Daemon Mode (3-hour cycle)...")
        while True:
            try:
                run_pipeline()
            except Exception as err:
                logger.error(f"[DAEMON CYCLE ERROR] {err}", exc_info=True)
            print("Cycle completed. Sleeping for 3 hours (10800s)...")
            time.sleep(10800)
    else:
        run_pipeline()


if __name__ == "__main__":
    main()
