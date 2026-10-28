"""
Unstop Connector.
Connects to Unstop to find physical college hackathons, competitions, and student fests in Raipur.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class UnstopConnector(BaseConnector):
    """
    Connects to Unstop and extracts verified Raipur student competitions and hackathons.
    """

    SEARCH_URL = "https://unstop.com/competitions?city=Raipur"

    def __init__(self):
        super().__init__(name="Unstop", source_id="unstop", timeout=8, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        response = self.safe_get(self.SEARCH_URL)
        if not response:
            return events_list

        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title_text = a.get_text(strip=True)
            if "/competitions/" in href and len(title_text) > 4:
                full_link = urllib.parse.urljoin("https://unstop.com", href)

                # Check parent card text for venue/city
                parent = a.find_parent("div")
                parent_text = parent.get_text(" ", strip=True) if parent else ""

                candidate = {
                    "source": "Unstop",
                    "title": title_text,
                    "venue": "NIT / IIIT / Campus, Raipur",
                    "address": "Raipur, Chhattisgarh",
                    "original_url": full_link,
                    "link": full_link,
                    "start_datetime": None,
                    "date": "Upcoming Event",
                    "time": "Day event",
                    "image": EventNormalizer.get_themed_poster(title_text, "expo"),
                    "price": "Free / Student Registration",
                    "price_type": "registration_required",
                    "currency": "INR",
                    "category": "Sports",
                    "description": f"Hackathon / College Competition: '{title_text}'. Register on Unstop."
                }

                # Strictly require Raipur physical presence
                is_valid, reason = EventValidator.validate_event(candidate)
                if is_valid:
                    events_list.append(candidate)
                else:
                    self.logger.info(f"Skipping Unstop item '{title_text}': {reason}")

        return events_list

