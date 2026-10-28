"""
BookMyShow Connector.
Extracts and verifies live event listings in Raipur from BookMyShow.
"""

import re
import json
import urllib.parse
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class BookMyShowConnector(BaseConnector):
    """
    Connects to BookMyShow and scrapes verified events for Raipur.
    """

    TARGET_URLS = [
        "https://in.bookmyshow.com/explore/events-raipur",
        "https://in.bookmyshow.com/explore/activities-raipur?cat=AT",
        "https://in.bookmyshow.com/explore/nightlife-raipur",
        "https://in.bookmyshow.com/explore/parties-raipur"
    ]

    def __init__(self):
        super().__init__(name="BookMyShow", source_id="bookmyshow", timeout=10, max_retries=2)

    def extract_event_detail(self, event_url: str, title: str) -> Dict[str, Any]:
        """
        Deep-fetches event detail page to extract exact venue and date.
        """
        response = self.safe_get(event_url, headers={"Referer": "https://in.bookmyshow.com/"})
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Poster extraction
        poster_url = None
        bmscdn_matches = re.findall(r'https://assets-in\.bmscdn\.com/nmcms/events/banner/desktop/[^\s"\']+', response.text)
        if bmscdn_matches:
            poster_url = bmscdn_matches[0]
        else:
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
            if og_img and og_img.get("content"):
                poster_url = og_img.get("content")

        # 2. JSON-LD Location & Date parsing
        venue_name = None
        address = None
        start_date_iso = None
        price_raw = None

        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or script.text or ""
            if "location" in content.lower() or "event" in content.lower():
                try:
                    data = json.loads(content)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        loc = item.get("location", {})
                        if isinstance(loc, dict):
                            venue_name = loc.get("name")
                            addr = loc.get("address", {})
                            if isinstance(addr, dict):
                                locality = addr.get("addressLocality", "")
                                street = addr.get("streetAddress", "")
                                address = f"{locality} {street}".strip()

                        if item.get("startDate"):
                            start_date_iso = item.get("startDate")
                        if item.get("offers"):
                            offers = item.get("offers")
                            if isinstance(offers, dict):
                                price_raw = offers.get("price")
                except Exception:
                    pass

        # If no venue name found via JSON-LD, look for meta tags or location tags
        if not venue_name:
            meta_loc = soup.find("meta", attrs={"name": "geo.placename"}) or soup.find("meta", property="event:location")
            if meta_loc and meta_loc.get("content"):
                venue_name = meta_loc.get("content")

        # If still no venue found, we cannot verify this event in Raipur
        if not venue_name:
            self.logger.info(f"BookMyShow event '{title}' has no verifiable venue on page.")
            return None

        # Normalize address
        venue_clean = EventNormalizer.clean_address(venue_name, locality=address or "")

        # Normalize Date & Time
        s_iso, _, d_hum, t_hum = EventNormalizer.parse_iso_or_human_date(start_date_iso)
        min_p, max_p, p_type, curr = EventNormalizer.parse_price(price_raw)

        candidate = {
            "source": "BookMyShow",
            "title": title,
            "venue": venue_clean,
            "address": address or venue_clean,
            "original_url": event_url,
            "link": event_url,
            "start_datetime": s_iso,
            "date": d_hum or "Upcoming Event",
            "time": t_hum or "Evening onwards",
            "image": poster_url or EventNormalizer.get_themed_poster(title),
            "price": f"₹{int(min_p)} onwards" if min_p else "Book on BookMyShow",
            "price_min": min_p,
            "price_max": max_p,
            "price_type": p_type,
            "currency": curr or "INR",
            "category": EventNormalizer.categorize_event(title, venue=venue_clean),
            "description": f"Live event at {venue_clean}: '{title}'. Book tickets directly on BookMyShow."
        }

        # Validate Raipur location
        is_valid, reason = EventValidator.validate_event(candidate)
        if is_valid:
            return candidate
        else:
            self.logger.info(f"Skipping BookMyShow candidate '{title}': {reason}")
            return None

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        seen_titles = set()

        for url in self.TARGET_URLS:
            response = self.safe_get(url)
            if not response:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title_text = a.get_text(strip=True)

                is_valid_type = any(path in href for path in ["/events/", "/activities/", "/plays/"])
                is_not_nav = "explore/" not in href and len(title_text) > 3

                if is_valid_type and is_not_nav:
                    full_link = urllib.parse.urljoin("https://in.bookmyshow.com", href)
                    norm_title = title_text.lower()
                    if norm_title not in seen_titles:
                        seen_titles.add(norm_title)
                        ev = self.extract_event_detail(full_link, title_text)
                        if ev:
                            events_list.append(ev)

        return events_list
