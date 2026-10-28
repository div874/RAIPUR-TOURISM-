"""
Luma Connector.
Connects to Luma (lu.ma/raipur) for community meetups, tech roundtables, and creative gatherings.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import json
import urllib.parse

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class LumaConnector(BaseConnector):
    """
    Connects to Lu.ma and checks for upcoming Raipur events.
    """

    TARGET_URL = "https://lu.ma/raipur"

    def __init__(self):
        super().__init__(name="Luma", source_id="luma", timeout=8, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        response = self.safe_get(self.TARGET_URL)
        if not response:
            return events_list

        soup = BeautifulSoup(response.text, "html.parser")

        # Parse JSON-LD ItemList
        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or script.text or ""
            if "itemlist" in content.lower() or "event" in content.lower():
                try:
                    data = json.loads(content)
                    items = data.get("itemListElement", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                    for item in items:
                        ev_item = item.get("item", item) if isinstance(item, dict) else {}
                        if not isinstance(ev_item, dict):
                            continue

                        title = ev_item.get("name")
                        if not title:
                            continue

                        event_url = ev_item.get("url") or self.TARGET_URL
                        start_date = ev_item.get("startDate")
                        img = ev_item.get("image")
                        poster = img if isinstance(img, str) else (img[0] if isinstance(img, list) else None)

                        loc = ev_item.get("location", {})
                        venue_name = loc.get("name", "Raipur, Chhattisgarh") if isinstance(loc, dict) else "Raipur, Chhattisgarh"
                        venue_clean = EventNormalizer.clean_address(venue_name)

                        s_iso, _, d_hum, t_hum = EventNormalizer.parse_iso_or_human_date(start_date)

                        candidate = {
                            "source": "Luma",
                            "title": title,
                            "venue": venue_clean,
                            "address": venue_clean,
                            "original_url": event_url,
                            "link": event_url,
                            "start_datetime": s_iso,
                            "date": d_hum or "Upcoming Event",
                            "time": t_hum or "Evening onwards",
                            "image": poster or EventNormalizer.get_themed_poster(title, "tech"),
                            "price": "RSVP on Luma",
                            "price_type": "registration_required",
                            "currency": "INR",
                            "category": EventNormalizer.categorize_event(title, venue=venue_clean),
                            "description": f"Community meetup in Raipur: '{title}'. Register directly on Luma."
                        }

                        is_valid, reason = EventValidator.validate_event(candidate)
                        if is_valid:
                            events_list.append(candidate)
                        else:
                            self.logger.info(f"Skipping Luma item '{title}': {reason}")
                except Exception as exc:
                    self.logger.warning(f"Error parsing Luma JSON: {exc}")

        return events_list

