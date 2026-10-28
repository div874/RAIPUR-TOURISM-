"""
Official Tourism and Government Sources Connector.
Extracts official state cultural events, Rajyotsav, handicrafts fairs, and district cultural announcements
from Chhattisgarh Tourism Board (tourism.cgstate.gov.in) and District Raipur (raipur.gov.in).
Strictly distinguishes scheduled events from permanent tourist attractions.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse
import re

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class OfficialSourcesConnector(BaseConnector):
    """
    Scrapes official cultural events and state exhibitions from Chhattisgarh Tourism & Raipur Administration.
    """

    SOURCES = [
        ("CG Tourism Events", "https://tourism.cgstate.gov.in/events", "https://tourism.cgstate.gov.in"),
        ("District Raipur Events", "https://raipur.gov.in/en/events/", "https://raipur.gov.in")
    ]

    def __init__(self):
        super().__init__(name="Official Sources", source_id="official_gov", timeout=10, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []

        for source_name, target_url, base_url in self.SOURCES:
            response = self.safe_get(target_url)
            if not response:
                continue

            # If page says "There is no Event" or "No Upcoming events available", log cleanly and continue
            if "there is no event" in response.text.lower() or "no upcoming events available" in response.text.lower():
                self.logger.info(f"{source_name}: No active public events listed currently.")
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # Look for event cards, tables or articles
            for item in soup.find_all(["article", "tr", "div"], class_=re.compile(r'event|card|notice', re.I)):
                text = item.get_text(" ", strip=True)
                if len(text) < 15:
                    continue

                # Check if it has a link
                a_tag = item.find("a", href=True)
                if not a_tag:
                    continue

                title = a_tag.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                full_link = urllib.parse.urljoin(base_url, a_tag["href"])

                # Check if it's a permanent attraction mistakenly listed
                if EventValidator.is_permanent_attraction(title, text):
                    self.logger.info(f"Skipping permanent attraction: {title}")
                    continue

                venue_clean = "Raipur, Chhattisgarh"
                candidate = {
                    "source": "Government of Chhattisgarh",
                    "title": title,
                    "venue": venue_clean,
                    "address": venue_clean,
                    "original_url": full_link,
                    "link": full_link,
                    "start_datetime": None,
                    "date": "Official Announcement",
                    "time": "Full day",
                    "image": EventNormalizer.get_themed_poster(title, "tribal"),
                    "price": "Free / Public Admission",
                    "price_min": 0.0,
                    "price_max": 0.0,
                    "price_type": "free",
                    "currency": "INR",
                    "category": "Culture",
                    "description": f"Official Chhattisgarh Cultural Event: '{title}'. Details on government portal."
                }

                is_valid, reason = EventValidator.validate_event(candidate)
                if is_valid:
                    events_list.append(candidate)
                else:
                    self.logger.info(f"Skipping official candidate '{title}': {reason}")

        return events_list

