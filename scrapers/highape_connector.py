"""
HighApe Connector.
Connects to HighApe nightlife and music event listings for Raipur.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class HighApeConnector(BaseConnector):
    """
    Connects to HighApe and extracts nightlife events.
    """

    TARGET_URL = "https://highape.com/raipur/events"

    def __init__(self):
        super().__init__(name="HighApe", source_id="highape", timeout=8, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        response = self.safe_get(self.TARGET_URL)
        if not response:
            return events_list

        soup = BeautifulSoup(response.text, "html.parser")
        for card in soup.find_all("div", class_=lambda c: c and ("event-card" in c or "card" in c)):
            link_tag = card.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            title_text = link_tag.get_text(strip=True)
            if not title_text or len(title_text) < 4:
                continue

            full_link = urllib.parse.urljoin("https://highape.com", href)
            img_tag = card.find("img")
            poster = img_tag.get("src") if img_tag else None

            candidate = {
                "source": "HighApe",
                "title": title_text,
                "venue": "Raipur, Chhattisgarh",
                "address": "Raipur, Chhattisgarh",
                "original_url": full_link,
                "link": full_link,
                "start_datetime": None,
                "date": "Upcoming Event",
                "time": "Night onwards",
                "image": poster or EventNormalizer.get_themed_poster(title_text, "music"),
                "price": "Book on HighApe",
                "price_type": "paid",
                "currency": "INR",
                "category": "Clubs",
                "description": f"Nightlife event in Raipur: '{title_text}'. Get tickets on HighApe."
            }

            is_valid, reason = EventValidator.validate_event(candidate)
            if is_valid:
                events_list.append(candidate)
            else:
                self.logger.info(f"Filtered out HighApe event '{title_text}': {reason}")

        return events_list

