"""
Local Organisers and Venues Connector.
Extensible registry for official announcements from local colleges (NIT Raipur, IIIT-NR, HNLU),
cultural centers, malls, and verified city organizers.
Does not perform unauthorized scraping of social media; uses official RSS/feeds and web notices.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse
import re

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class LocalOrganisersConnector(BaseConnector):
    """
    Extensible connector for trusted local hubs, academic institutions, and venue announcements.
    """

    TRUSTED_LOCAL_FEEDS = [
        {
            "name": "NIT Raipur Events",
            "url": "https://www.nitrr.ac.in/",
            "venue": "NIT Raipur Campus, G.E. Road",
            "category": "Culture"
        },
        {
            "name": "IIIT Naya Raipur Fests",
            "url": "https://www.iiitnr.ac.in/",
            "venue": "IIIT Naya Raipur Campus, Sector 24",
            "category": "Sports"
        }
    ]

    def __init__(self):
        super().__init__(name="Local Organisers", source_id="local_organisers", timeout=10, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []

        for feed in self.TRUSTED_LOCAL_FEEDS:
            response = self.safe_get(feed["url"])
            if not response:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # Look for upcoming events / notices
            for item in soup.find_all(["li", "div", "a"], class_=re.compile(r'event|notice|fest|conference', re.I)):
                text = item.get_text(" ", strip=True)
                if not any(w in text.lower() for w in ["hackathon", "fest", "symposium", "conference", "cultural night", "annual fest", "mela"]):
                    continue

                a_tag = item if item.name == "a" else item.find("a", href=True)
                if not a_tag:
                    continue

                href = a_tag.get("href", "")
                title = a_tag.get_text(strip=True)
                if not title or len(title) < 6:
                    continue

                full_link = urllib.parse.urljoin(feed["url"], href)

                candidate = {
                    "source": feed["name"],
                    "title": title,
                    "venue": feed["venue"],
                    "address": feed["venue"] + ", Raipur",
                    "original_url": full_link,
                    "link": full_link,
                    "start_datetime": None,
                    "date": "Upcoming Campus Event",
                    "time": "Campus Hours",
                    "image": EventNormalizer.get_themed_poster(title, feed["category"]),
                    "price": "Free / Student Entry",
                    "price_min": 0.0,
                    "price_max": 0.0,
                    "price_type": "free",
                    "currency": "INR",
                    "category": feed["category"],
                    "description": f"Campus event at {feed['venue']}: '{title}'. View official college notice."
                }

                is_valid, reason = EventValidator.validate_event(candidate)
                if is_valid:
                    events_list.append(candidate)
                else:
                    self.logger.info(f"Skipping local organiser item '{title}': {reason}")

        return events_list

