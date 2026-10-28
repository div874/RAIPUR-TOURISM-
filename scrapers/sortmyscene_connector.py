"""
SortMyScene Connector.
Extracts verified nightlife, DJ sets, screenings, and parties in Raipur from SortMyScene.
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class SortMySceneConnector(BaseConnector):
    """
    Connects to SortMyScene and verifies Raipur events.
    """

    KNOWN_RAIPUR_TARGETS = [
        ("1+1 Pool Offer At Underdoggs Raipur", "https://sortmyscene.com/event/1-1-pool-offer-at-underdoggs-raipur-tuesday-pool-deal-play-one-get-one-free-oct-06-2026", "Underdoggs Raipur"),
        ("WTF & Co. Cinema Rave", "https://sortmyscene.com/event/wtf-co-cinema-rave-oct-09-2026", "TBA, Raipur"),
        ("Fake Resignation Party", "https://sortmyscene.com/event/fake-resignation-party-oct-03-2026", "Edo, Raipur"),
        ("Ex Ki Shaadi", "https://sortmyscene.com/event/ex-ki-shaadi-oct-10-2026", "The Haunt Dive 2.0, Raipur"),
        ("Saturday Glam With Yogesh Rawat", "https://sortmyscene.com/event/saturday-glam-oct-10-2026", "F Lounge by FTV, Raipur"),
        ("Manchester United Vs Tottenham Hotspur", "https://sortmyscene.com/event/manchester-united-vs-tottenham-hotspur-underdoggs-raipur-raipur-oct-10-2026", "Underdoggs Raipur"),
        ("Raas-E-Rang", "https://sortmyscene.com/event/raas-e-rang-oct-11-2026", "The Soul Garden, Raipur"),
        ("Royal Garba Raipur", "https://sortmyscene.com/event/royal-garba-oct-11-2026", "Hotel Royal Castle, Raipur"),
        ("Trick OR Treat", "https://sortmyscene.com/event/trick-or-treat-oct-31-2026", "TBA, Raipur")
    ]

    def __init__(self):
        super().__init__(name="SortMyScene", source_id="sortmyscene", timeout=8, max_retries=2)

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []

        for title, link, default_venue in self.KNOWN_RAIPUR_TARGETS:
            response = self.safe_get(link)
            poster_url = None
            venue_name = default_venue
            date_human = "Upcoming Event"
            time_human = "Evening onwards"
            start_iso = None

            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
                if og_img and og_img.get("content"):
                    poster_url = og_img.get("content")

                # Parse meta description for date/time
                og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
                if og_desc and og_desc.get("content"):
                    desc = og_desc.get("content")
                    m_date = re.search(r'on\s+([A-Za-z]{3}\s+[A-Za-z]{3}\s+\d{2}\s+\d{4})', desc)
                    if m_date:
                        s_iso, _, d_hum, _ = EventNormalizer.parse_iso_or_human_date(m_date.group(1))
                        if d_hum:
                            date_human = d_hum
                            start_iso = s_iso

                    m_time = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)(?:\s*to\s*\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))?)', desc)
                    if m_time:
                        time_human = m_time.group(1).upper()

            venue_clean = EventNormalizer.clean_address(venue_name)
            category = EventNormalizer.categorize_event(title, venue=venue_clean)

            candidate = {
                "source": "SortMyScene",
                "title": title,
                "venue": venue_clean,
                "address": venue_clean,
                "original_url": link,
                "link": link,
                "start_datetime": start_iso,
                "date": date_human,
                "time": time_human,
                "image": poster_url or EventNormalizer.get_themed_poster(title, category),
                "price": "Book on SortMyScene",
                "price_min": None,
                "price_max": None,
                "price_type": "paid",
                "currency": "INR",
                "category": category,
                "description": f"Live event at {venue_clean}: '{title}'. Book passes directly on SortMyScene."
            }

            is_valid, reason = EventValidator.validate_event(candidate)
            if is_valid:
                events_list.append(candidate)
            else:
                self.logger.info(f"Filtered out SortMyScene item '{title}': {reason}")

        return events_list

