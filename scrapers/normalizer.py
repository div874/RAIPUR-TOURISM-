"""
Event Normalizer.
Standardizes dates, times, timezones (Asia/Kolkata), currencies (INR),
pricing classification, address deduplication, categories, and editorial tags.
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional

# Standard Asia/Kolkata offset (+05:30)
KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))

THEMED_POSTERS = {
    "sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
    "expo": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=800&q=80",
    "exhibition": "https://images.unsplash.com/photo-1531058240690-006c446962d8?auto=format&fit=crop&w=800&q=80",
    "comedy": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
    "music": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
    "garba": "https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?auto=format&fit=crop&w=800&q=80",
    "tribal": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
    "tech": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
    "default": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80"
}


class EventNormalizer:
    """
    Normalizes multi-source raw fields into canonical schema.
    """

    @staticmethod
    def clean_address(raw_str: str, street: str = "", locality: str = "") -> str:
        """Cleans up redundant country/zip code/repeated suffixes for clean venue rendering."""
        if not raw_str:
            return "Raipur, Chhattisgarh"

        clean_name = re.sub(r'[:|]\s*Raipur.*$', '', raw_str, flags=re.I).strip()
        if "to be announced" in clean_name.lower() or clean_name.lower().startswith("tba"):
            return "Venue To Be Announced"

        combined = clean_name
        if street and street.lower() not in clean_name.lower():
            combined += f", {street}"
        elif locality and locality.lower() not in clean_name.lower():
            combined += f", {locality}"

        # Clean country, pincode, chhattisgarh repeats
        cleaned = re.sub(r',?\s*India', '', combined, flags=re.I)
        cleaned = re.sub(r',?\s*492\d{3}', '', cleaned)
        cleaned = re.sub(r',?\s*Chhattisgarh', '', cleaned, flags=re.I)
        cleaned = re.sub(r'\(\s*\)', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(", ")

        # Deduplicate parts
        parts = [p.strip() for p in re.split(r'[,|]', cleaned) if p.strip()]
        unique_parts = []
        seen = set()
        for p in parts:
            p_lower = p.lower()
            if p_lower not in seen:
                seen.add(p_lower)
                unique_parts.append(p)

        res = ", ".join(unique_parts)
        if res.lower() in ["raipur", "raipur city", ""]:
            return "Raipur, Chhattisgarh"
        return res

    @staticmethod
    def parse_price(raw_price: Any, description: str = "") -> Tuple[Optional[float], Optional[float], str, Optional[str]]:
        """
        Extracts min_price, max_price, price_type, currency.
        price_type in: 'free', 'paid', 'undisclosed', 'registration_required', 'unknown'
        """
        combined = f"{raw_price} {description}".lower()

        if raw_price is None or raw_price == "":
            if "free entry" in combined or "free registration" in combined or "entry is free" in combined:
                return 0.0, 0.0, "free", "INR"
            if "registration required" in combined or "register" in combined:
                return None, None, "registration_required", None
            return None, None, "undisclosed", None

        price_str = str(raw_price).strip()

        if price_str.lower() in ["free", "0", "rs 0", "inr 0", "₹0"]:
            return 0.0, 0.0, "free", "INR"

        # Regex search for numbers
        numbers = re.findall(r'[\d,]+(?:\.\d+)?', price_str)
        if numbers:
            parsed_nums = []
            for n in numbers:
                clean_n = n.replace(',', '')
                try:
                    parsed_nums.append(float(clean_n))
                except ValueError:
                    pass

            if parsed_nums:
                min_p = min(parsed_nums)
                max_p = max(parsed_nums)
                currency = "INR" if ("₹" in price_str or "rs" in price_str.lower() or "inr" in price_str.lower()) else "INR"
                return min_p, max_p, "paid", currency

        if "register" in price_str.lower():
            return None, None, "registration_required", None

        return None, None, "undisclosed", None

    @staticmethod
    def parse_iso_or_human_date(date_raw: Any, time_raw: Any = None) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Returns (start_datetime_iso, end_datetime_iso, date_human, time_human).
        Guarantees Asia/Kolkata timezone awareness.
        """
        if not date_raw:
            return None, None, "Upcoming Event", "Evening onwards"

        start_iso = None
        end_iso = None
        date_human = None
        time_human = None

        if isinstance(date_raw, datetime):
            dt = date_raw
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=KOLKATA_TZ)
            start_iso = dt.isoformat()
            date_human = dt.strftime("%a, %d %b %Y")
            time_human = dt.strftime("%I:%M %p").lstrip("0") + " onwards"
            return start_iso, end_iso, date_human, time_human

        date_str = str(date_raw).strip()

        # Check ISO format: e.g. 2026-10-31T19:00:00+05:30
        if "T" in date_str:
            try:
                clean_iso = date_str.split("+")[0].split("Z")[0].split(".")[0]
                dt = datetime.strptime(clean_iso, "%Y-%m-%dT%H:%M:%S")
                dt = dt.replace(tzinfo=KOLKATA_TZ)
                start_iso = dt.isoformat()
                date_human = dt.strftime("%a, %d %b %Y")
                time_human = dt.strftime("%I:%M %p").lstrip("0") + " onwards"
            except Exception:
                pass

        # Check standard human formats
        if not date_human:
            clean_str = re.sub(r'^[A-Za-z]{3},\s*', '', date_str)
            for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"):
                try:
                    dt = datetime.strptime(clean_str[:11].strip(), fmt)
                    dt = dt.replace(tzinfo=KOLKATA_TZ)
                    start_iso = dt.isoformat()
                    date_human = dt.strftime("%a, %d %b %Y")
                    break
                except ValueError:
                    pass

        if not date_human:
            date_human = date_str if len(date_str) < 30 else "Upcoming Event"

        if time_raw and not time_human:
            t_str = str(time_raw).strip()
            if re.match(r'^\d{1,2}:\d{2}', t_str):
                time_human = t_str if "onwards" in t_str.lower() or "to" in t_str.lower() else t_str + " onwards"
            else:
                time_human = t_str
        elif not time_human:
            time_human = "Evening onwards"

        return start_iso, end_iso, date_human, time_human

    @staticmethod
    def categorize_event(title: str, category: str = "", venue: str = "", desc: str = "") -> str:
        """
        Categorizes events into standardized tabs:
        'Sports', 'Culture', 'Clubs', 'Shows'
        """
        corpus = f"{title} {category} {venue} {desc}".lower()

        # 1. SPORTS
        sports_keywords = ["sport", "screening", "vs", "match", "cricket", "football", "turf", "safari", "marathon", "badminton", "tennis", "trek", "outdoor", "camping", "stadium", "ipl", "f1", "race", "hackathon", "competition", "quiz"]
        if any(kw in corpus for kw in sports_keywords):
            return "Sports"

        # 2. CULTURE
        culture_keywords = ["garba", "dandiya", "navratri", "exhibition", "expo", "heritage", "bastar", "tribal", "handicraft", "handloom", "cultural", "fair", "fest", "craft", "puja", "pujo", "workshop", "conference", "literature", "meetup"]
        if any(kw in corpus for kw in culture_keywords):
            return "Culture"

        # 3. CLUBS
        club_keywords = ["club", "dj", "nightclub", "party", "pub", "lounge", "haunt dive", "f lounge", "edo", "afterparty", "dance floor", "nightlife", "bhangra night", "underdoggs"]
        if any(kw in corpus for kw in club_keywords):
            return "Clubs"

        # 4. SHOWS
        return "Shows"

    @classmethod
    def get_themed_poster(cls, title: str, category: str = "") -> str:
        """Returns thematic high resolution photo fallback."""
        corpus = f"{title} {category}".lower()
        for key in ["sports", "expo", "exhibition", "comedy", "music", "garba", "tribal", "tech"]:
            if key in corpus:
                return THEMED_POSTERS[key]
        return THEMED_POSTERS["default"]

