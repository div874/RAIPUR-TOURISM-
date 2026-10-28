"""
Townscript Connector.
Connects to Townscript for conferences, cultural gatherings, and workshops in Raipur.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
import urllib.parse

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class TownscriptConnector(BaseConnector):
    """
    Connects to Townscript Raipur events.
    """

    TARGET_URL = "https://www.townscript.com/raipur/events"

    def __init__(self):
        super().__init__(name="Townscript", source_id="townscript", timeout=8, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        response = self.safe_get(self.TARGET_URL)
        if not response:
            return events_list

        soup = BeautifulSoup(response.text, "html.parser")

        # Parse JSON-LD or structured event blocks
        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or script.text or ""
            if "event" in content.lower():
                try:
                    data = json.loads(content)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        if item.get("@type") == "Event":
                            title = item.get("name")
                            if not title:
                                continue

                            start_date = item.get("startDate")
                            event_url = item.get("url") or self.TARGET_URL
                            img = item.get("image")
                            poster = img if isinstance(img, str) else (img.get("url") if isinstance(img, dict) else None)

                            loc = item.get("location", {})
                            venue_name = loc.get("name", "Raipur, Chhattisgarh") if isinstance(loc, dict) else "Raipur, Chhattisgarh"
                            venue_clean = EventNormalizer.clean_address(venue_name)

                            s_iso, _, d_hum, t_hum = EventNormalizer.parse_iso_or_human_date(start_date)

                            candidate = {
                                "source": "Townscript",
                                "title": title,
                                "venue": venue_clean,
                                "address": venue_clean,
                                "original_url": event_url,
                                "link": event_url,
                                "start_datetime": s_iso,
                                "date": d_hum or "Upcoming Event",
                                "time": t_hum or "Evening onwards",
                                "image": poster or EventNormalizer.get_themed_poster(title),
                                "price": "Register on Townscript",
                                "price_type": "registration_required",
                                "currency": "INR",
                                "category": EventNormalizer.categorize_event(title, venue=venue_clean),
                                "description": f"Event at {venue_clean}: '{title}'. Register on Townscript."
                            }

                            is_valid, reason = EventValidator.validate_event(candidate)
                            if is_valid:
                                events_list.append(candidate)
                            else:
                                self.logger.info(f"Skipping Townscript item '{title}': {reason}")
                except Exception as exc:
                    self.logger.warning(f"Error parsing Townscript JSON: {exc}")

        return events_list

