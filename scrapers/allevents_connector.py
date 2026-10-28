"""
AllEvents Connector.
Extracts verified events from the AllEvents Raipur directory.
"""

import json
import urllib.parse
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from scrapers.base_connector import BaseConnector
from scrapers.normalizer import EventNormalizer
from scrapers.event_validator import EventValidator


class AllEventsConnector(BaseConnector):
    """
    Connects to AllEvents Raipur and extracts structured event records.
    """

    DIRECTORY_URL = "https://allevents.in/raipur/all"

    def __init__(self):
        super().__init__(name="AllEvents", source_id="allevents", timeout=10, max_retries=2)

    def extract_from_event_page(self, event_url: str, fallback_title: str) -> Dict[str, Any]:
        """
        Deep-checks an individual AllEvents page if needed.
        """
        response = self.safe_get(event_url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        title = fallback_title
        venue_name = "Raipur, Chhattisgarh"
        address = "Raipur, Chhattisgarh"
        start_date_iso = None
        poster_url = None
        price_raw = None

        # Look for JSON-LD schema
        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or script.text or ""
            if '"@type":"event"' in content.lower().replace(" ", ""):
                try:
                    data = json.loads(content)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("name"):
                            title = item.get("name")
                        if item.get("image"):
                            img = item.get("image")
                            poster_url = img if isinstance(img, str) else img.get("url")
                        if item.get("startDate"):
                            start_date_iso = item.get("startDate")
                        loc = item.get("location", {})
                        if isinstance(loc, dict):
                            venue_name = loc.get("name", venue_name)
                            addr = loc.get("address", {})
                            if isinstance(addr, dict):
                                street = addr.get("streetAddress", "")
                                locality = addr.get("addressLocality", "")
                                address = f"{locality} {street}".strip()
                        if item.get("offers"):
                            offers = item.get("offers")
                            if isinstance(offers, dict):
                                price_raw = offers.get("price")
                except Exception:
                    pass

        # OG image fallback
        if not poster_url:
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
            if og_img and og_img.get("content"):
                poster_url = og_img.get("content")

        venue_clean = EventNormalizer.clean_address(venue_name, locality=address)
        s_iso, _, d_hum, t_hum = EventNormalizer.parse_iso_or_human_date(start_date_iso)
        min_p, max_p, p_type, curr = EventNormalizer.parse_price(price_raw)

        candidate = {
            "source": "AllEvents",
            "title": title,
            "venue": venue_clean,
            "address": address,
            "original_url": event_url,
            "link": event_url,
            "start_datetime": s_iso,
            "date": d_hum or "Upcoming Event",
            "time": t_hum or "Evening onwards",
            "image": poster_url or EventNormalizer.get_themed_poster(title),
            "price": f"₹{int(min_p)} onwards" if min_p else "Book on AllEvents",
            "price_min": min_p,
            "price_max": max_p,
            "price_type": p_type,
            "currency": curr or "INR",
            "category": EventNormalizer.categorize_event(title, venue=venue_clean),
            "description": f"Live event at {venue_clean}: '{title}'. Tickets available on AllEvents."
        }

        is_valid, reason = EventValidator.validate_event(candidate)
        if is_valid:
            return candidate
        else:
            self.logger.info(f"Skipping AllEvents candidate '{title}': {reason}")
            return None

    def fetch_records(self) -> List[Dict[str, Any]]:
        events_list = []
        seen_titles = set()

        response = self.safe_get(self.DIRECTORY_URL)
        if not response:
            return events_list

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Parse JSON-LD events present on the directory page
        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string or script.text or ""
            if '"@type":"event"' in content.lower().replace(" ", ""):
                try:
                    data = json.loads(content)
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        title = item.get("name")
                        if not title:
                            continue

                        norm_title = title.lower()
                        if norm_title in seen_titles:
                            continue

                        event_url = item.get("url") or self.DIRECTORY_URL
                        img = item.get("image")
                        poster = img if isinstance(img, str) else (img.get("url") if isinstance(img, dict) else None)
                        start_date = item.get("startDate")

                        loc = item.get("location", {})
                        venue_name = "Raipur, Chhattisgarh"
                        address = ""
                        if isinstance(loc, dict):
                            venue_name = loc.get("name", venue_name)
                            addr = loc.get("address", {})
                            if isinstance(addr, dict):
                                street = addr.get("streetAddress", "")
                                locality = addr.get("addressLocality", "")
                                address = f"{locality} {street}".strip()

                        venue_clean = EventNormalizer.clean_address(venue_name, locality=address)
                        s_iso, _, d_hum, t_hum = EventNormalizer.parse_iso_or_human_date(start_date)

                        offers = item.get("offers")
                        price_raw = offers.get("price") if isinstance(offers, dict) else None
                        min_p, max_p, p_type, curr = EventNormalizer.parse_price(price_raw)

                        candidate = {
                            "source": "AllEvents",
                            "title": title,
                            "venue": venue_clean,
                            "address": address,
                            "original_url": event_url,
                            "link": event_url,
                            "start_datetime": s_iso,
                            "date": d_hum or "Upcoming Event",
                            "time": t_hum or "Evening onwards",
                            "image": poster or EventNormalizer.get_themed_poster(title),
                            "price": f"₹{int(min_p)} onwards" if min_p else "Book on AllEvents",
                            "price_min": min_p,
                            "price_max": max_p,
                            "price_type": p_type,
                            "currency": curr or "INR",
                            "category": EventNormalizer.categorize_event(title, venue=venue_clean),
                            "description": f"Live event at {venue_clean}: '{title}'. Get tickets directly on AllEvents."
                        }

                        is_valid, reason = EventValidator.validate_event(candidate)
                        if is_valid:
                            seen_titles.add(norm_title)
                            events_list.append(candidate)
                        else:
                            self.logger.info(f"Filtered out AllEvents item '{title}': {reason}")
                except Exception as exc:
                    self.logger.warning(f"Error parsing AllEvents JSON-LD: {exc}")

        # 2. Extract links in the HTML
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title_text = a.get_text(strip=True)
            if "/raipur/" in href and any(char.isdigit() for char in href) and len(title_text) > 4:
                full_link = urllib.parse.urljoin("https://allevents.in", href)
                norm_title = title_text.lower()
                if norm_title not in seen_titles:
                    seen_titles.add(norm_title)
                    ev = self.extract_from_event_page(full_link, title_text)
                    if ev:
                        events_list.append(ev)

        return events_list

