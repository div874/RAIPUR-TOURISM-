"""
Meetup Connector.
Discovers local community groups and physical events happening in Raipur.
Strictly rejects virtual/online webinars and ensures physical location in Raipur.
"""

import json
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class MeetupConnector(BaseConnector):
    """
    Connects to Meetup and collects physical events in Raipur.
    """

    MEETUP_RAIPUR_URL = "https://www.meetup.com/find/?location=in--Raipur&source=EVENTS"

    def __init__(self):
        super().__init__(name="Meetup", source_id="meetup", timeout=10, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        response = self.safe_get(self.MEETUP_RAIPUR_URL)
        if not response:
            return events_list

        soup = BeautifulSoup(response.text, "html.parser")

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

                            # Check for online event flag
                            event_mode = str(item.get("eventAttendanceMode", "")).lower()
                            if "online" in event_mode or "online" in title.lower() or "virtual" in title.lower():
                                self.logger.info(f"Skipping online Meetup event: {title}")
                                continue

                            start_date = item.get("startDate")
                            event_url = item.get("url") or self.MEETUP_RAIPUR_URL
                            img = item.get("image")
                            poster = img if isinstance(img, str) else (img.get("url") if isinstance(img, dict) else None)

                            loc = item.get("location", {})
                            venue_name = None
                            address = ""
                            if isinstance(loc, dict):
                                venue_name = loc.get("name")
                                addr = loc.get("address", {})
                                if isinstance(addr, dict):
                                    street = addr.get("streetAddress", "")
                                    locality = addr.get("addressLocality", "")
                                    address = f"{locality} {street}".strip()

                            if not venue_name:
                                continue

                            venue_clean = EventNormalizer.clean_address(venue_name, locality=address)
                            s_iso, _, d_hum, t_hum = EventNormalizer.parse_iso_or_human_date(start_date)

                            candidate = {
                                "source": "Meetup",
                                "title": title,
                                "venue": venue_clean,
                                "address": address or venue_clean,
                                "original_url": event_url,
                                "link": event_url,
                                "start_datetime": s_iso,
                                "date": d_hum or "Upcoming Event",
                                "time": t_hum or "Evening onwards",
                                "image": poster or EventNormalizer.get_themed_poster(title, "tech"),
                                "price": "RSVP on Meetup",
                                "price_type": "registration_required",
                                "currency": "INR",
                                "category": EventNormalizer.categorize_event(title, venue=venue_clean),
                                "description": f"Community event at {venue_clean}: '{title}'. Join on Meetup."
                            }

                            is_valid, reason = EventValidator.validate_event(candidate)
                            if is_valid:
                                events_list.append(candidate)
                            else:
                                self.logger.info(f"Filtered out Meetup event '{title}': {reason}")
                except Exception as exc:
                    self.logger.warning(f"Error parsing Meetup JSON: {exc}")

        return events_list
