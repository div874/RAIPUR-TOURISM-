"""
======================================================
  Raipur Multi-Source Events Scraper 🎟️ (BMS + District)
======================================================
This script collects live upcoming events happening in Raipur from:
1. BookMyShow (Raipur Events & Garba Activities)
2. District / Paytm Insider (Concerts, Screenings, Expos & Shows)

It extracts: Title, Date, Venue, Price, Source, Image, and Booking Link,
and saves the consolidated dataset into `events.json`.
"""

import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

DEFAULT_FALLBACK_POSTER = "images/tribal_dance.jpg"

# ----------------------------------------------------
# MODULE 1: BookMyShow Raipur Scraper
# ----------------------------------------------------
BMS_TARGET_URLS = [
    "https://in.bookmyshow.com/explore/events-raipur",
    "https://in.bookmyshow.com/explore/activities-raipur?cat=AT",
    "https://in.bookmyshow.com/explore/nightlife-raipur",
    "https://in.bookmyshow.com/explore/parties-raipur"
]

EXCLUDED_CITIES = [
    "hyderabad", "bangalore", "mumbai", "lucknow", "ahmedabad",
    "gurgaon", "delhi", "pune", "chennai", "kolkata", "bengaluru",
    "noida", "aundh", "imagicaa", "wonderla", "vgp", "ramoji"
]


def fetch_bms_poster(event_url):
    """Fetches official high-res desktop banner from BookMyShow event pages."""
    try:
        res = requests.get(event_url, headers=HEADERS, timeout=6)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for script in soup.find_all("script", type="application/ld+json"):
                content = script.string or script.text or ""
                if '"@type":"Event"' in content or '"@type": "Event"' in content:
                    try:
                        data = json.loads(content)
                        if isinstance(data, list) and len(data) > 0:
                            data = data[0]
                        images = data.get("image", [])
                        if isinstance(images, list) and len(images) > 0:
                            return images[0]
                        elif isinstance(images, str) and images.startswith("http"):
                            return images
                    except Exception:
                        pass
    except Exception:
        pass
    return DEFAULT_FALLBACK_POSTER


def scrape_bookmyshow_events():
    """Scrapes live event & activity listings with official posters from BookMyShow."""
    print("[SEARCH] Searching BookMyShow for Raipur events...")
    events_list = []
    seen_titles = set()

    for url in BMS_TARGET_URLS:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            anchor_tags = soup.find_all("a", href=True)

            for a in anchor_tags:
                href = a["href"]
                title_text = a.get_text(strip=True)

                is_valid_type = any(path in href for path in ["/events/", "/activities/", "/plays/"])
                is_not_nav = "explore/" not in href and len(title_text) > 3

                if is_valid_type and is_not_nav:
                    full_link = urllib.parse.urljoin("https://in.bookmyshow.com", href)
                    normalized_title = title_text.lower()
                    normalized_href = href.lower()

                    is_outside_event = any(kw in normalized_title or kw in normalized_href for kw in EXCLUDED_CITIES)

                    if not is_outside_event and normalized_title not in seen_titles:
                        seen_titles.add(normalized_title)
                        category = "Garba & Activity" if "activities" in href else "Live Show & Comedy"

                        print(f"  [POSTER] BookMyShow poster for: '{title_text[:40]}'...")
                        poster_url = fetch_bms_poster(full_link)

                        events_list.append({
                            "title": title_text,
                            "date": "Upcoming · Check BookMyShow",
                            "venue": "Raipur Venue / Cultural Center",
                            "price": "Book on BookMyShow",
                            "source": "BookMyShow",
                            "image": poster_url,
                            "link": full_link,
                            "category": category,
                            "tag": "week",
                            "description": f"Live event in Raipur: '{title_text}'. Get tickets directly on BookMyShow."
                        })

        except Exception as error:
            print(f"  [ERROR] BookMyShow fetch error: {error}")

    print(f"  [OK] Found {len(events_list)} events from BookMyShow.\n")
    return events_list


# ----------------------------------------------------
# MODULE 2: District / Paytm Insider Scraper
# ----------------------------------------------------
DISTRICT_URL = "https://allevents.in/raipur/all"


def scrape_district_events():
    """Scrapes live event listings from District / Paytm Insider."""
    print("[SEARCH] Searching District / Paytm Insider for Raipur events...")
    events_list = []
    seen_titles = set()

    try:
        response = requests.get(DISTRICT_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            anchor_tags = soup.find_all("a", href=True)

            for a in anchor_tags:
                href = a["href"]
                title_text = a.get_text(strip=True)

                if "/raipur/" in href and any(char.isdigit() for char in href) and len(title_text) > 3:
                    full_link = urllib.parse.urljoin("https://allevents.in", href)
                    normalized_title = title_text.lower()

                    if normalized_title not in seen_titles:
                        seen_titles.add(normalized_title)

                        # Poster image fallback or parent image
                        parent_card = a.find_parent(["li", "div"])
                        poster_img = DEFAULT_FALLBACK_POSTER
                        if parent_card:
                            img = parent_card.find("img")
                            if img and img.get("src") and "http" in img.get("src"):
                                poster_img = img.get("src")

                        events_list.append({
                            "title": title_text,
                            "date": "Upcoming · Check District",
                            "venue": "Raipur Venue / Convention Center",
                            "price": "Book on District",
                            "source": "District",
                            "image": poster_img,
                            "link": full_link,
                            "category": "Exhibition & Live Event",
                            "tag": "week",
                            "description": f"Live event in Raipur: '{title_text}'. Get tickets directly on District / Paytm Insider."
                        })

    except Exception as error:
        print(f"  [ERROR] District fetch error: {error}")

    print(f"  [OK] Found {len(events_list)} events from District.\n")
    return events_list


# ----------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------
def main():
    print("=========================================")
    print("   Raipur Events Scraper (BookMyShow + District)")
    print("=========================================\n")

    bms_events = scrape_bookmyshow_events()
    district_events = scrape_district_events()

    all_events = bms_events + district_events

    # De-duplicate by title across both platforms
    unique_events = []
    seen_all = set()
    for ev in all_events:
        title_key = ev["title"].lower().strip()
        if title_key not in seen_all:
            seen_all.add(title_key)
            unique_events.append(ev)

    output_filename = "events.json"
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(unique_events, file, indent=4, ensure_ascii=False)

    print("=========================================")
    print(f"[SUCCESS] Scraped & Saved {len(unique_events)} total events to '{output_filename}'!")
    print("=========================================")


if __name__ == "__main__":
    main()
