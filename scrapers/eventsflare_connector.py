"""
Eventsflare Connector.
Connects to Eventsflare Raipur section and extracts local live events.
Filters out navigation elements, CTA arrows, and non-Raipur promotional listings.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse
import re

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class EventsflareConnector(BaseConnector):
    """
    Connects to Eventsflare and extracts eligible Raipur listings.
    """

    TARGET_URL = "https://eventsflare.com/raipur"

    def __init__(self):
        super().__init__(name="Eventsflare", source_id="eventsflare", timeout=8, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        response = self.safe_get(self.TARGET_URL)
        if not response:
            return events_list

        soup = BeautifulSoup(response.text, "html.parser")
        seen_titles = set()

        for card in soup.find_all("div", class_=lambda c: c and ("card" in c or "event" in c)):
            link_tag = card.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            title_text = link_tag.get_text(strip=True)
            if not title_text or len(title_text) < 6:
                continue

            # Remove trailing unicode arrows or whitespace
            clean_title = re.sub(r'[\u2190-\u21FF\u2794\u279C\u27A1\uFEFF]', '', title_text).strip()

            # Skip common UI action labels & navigation CTAs
            lower_title = clean_title.lower()
            if any(term in lower_title for term in [
                "login", "continue with", "sign in", "create event",
                "new year", "list your event", "explore raipur", "events in raipur",
                "all events", "view all", "see more", "terms"
            ]):
                continue

            # Event URLs on Eventsflare typically end with an event ID /e/\d+
            if not re.search(r'/e/\d+', href):
                continue

            # Must have explicit raipur in href or card text
            card_text = card.get_text(" ", strip=True).lower()
            if "raipur" not in href.lower() and "raipur" not in card_text:
                continue

            if lower_title in seen_titles:
                continue

            full_link = urllib.parse.urljoin("https://eventsflare.com", href)
            img_tag = card.find("img")
            poster = img_tag.get("src") if img_tag else None

            candidate = {
                "source": "Eventsflare",
                "title": clean_title,
                "venue": "Raipur, Chhattisgarh",
                "address": "Raipur, Chhattisgarh",
                "original_url": full_link,
                "link": full_link,
                "start_datetime": None,
                "date": "Upcoming Event",
                "time": "Evening onwards",
                "image": poster or EventNormalizer.get_themed_poster(clean_title),
                "price": "Book on Eventsflare",
                "price_type": "paid",
                "currency": "INR",
                "category": EventNormalizer.categorize_event(clean_title, desc=card_text),
                "description": f"Live event in Raipur: '{clean_title}'. Get tickets on Eventsflare."
            }

            is_valid, reason = EventValidator.validate_event(candidate)
            if is_valid:
                seen_titles.add(lower_title)
                events_list.append(candidate)
            else:
                self.logger.info(f"Filtered out Eventsflare candidate '{clean_title}': {reason}")

        return events_list
