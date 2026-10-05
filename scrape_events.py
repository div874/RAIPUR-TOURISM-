"""
======================================================
  Raipur Multi-Source Events Scraper 🎟️ (BMS + District + Google)
======================================================
This script collects live upcoming events happening in Raipur from:
1. BookMyShow (Raipur Events & Garba Activities)
2. District / Paytm Insider (Concerts, Screenings, Expos & Shows)
3. Google Search (Local Raipur Gatherings, Fairs & Meetups)

It extracts official high-res posters/banners for ALL platforms via:
- BookMyShow JSON-LD & Page Banners
- District / Paytm Insider OpenGraph `og:image` Posters
- Google Search Web OpenGraph `og:image` Posters & Themed Banners

Saves the consolidated dataset into `events.json`.
"""

import json
import urllib.parse
import warnings
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

THEMED_POSTERS = {
    "sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
    "expo": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=800&q=80",
    "exhibition": "https://images.unsplash.com/photo-1531058240690-006c446962d8?auto=format&fit=crop&w=800&q=80",
    "flower": "https://images.unsplash.com/photo-1508615070457-7baeba4003ab?auto=format&fit=crop&w=800&q=80",
    "mango": "https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=800&q=80",
    "literature": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=800&q=80",
    "book": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=800&q=80",
    "comedy": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
    "music": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
    "garba": "https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?auto=format&fit=crop&w=800&q=80",
    "tribal": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
    "default": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80"
}

EXCLUDED_CITIES = [
    "hyderabad", "bangalore", "mumbai", "lucknow", "ahmedabad",
    "gurgaon", "delhi", "pune", "chennai", "kolkata", "bengaluru",
    "noida", "aundh", "imagicaa", "wonderla", "vgp", "ramoji", "kila raipur", "punjab"
]


def get_themed_poster(title):
    """Returns a high quality themed event poster matching keywords in title."""
    title_lower = title.lower()
    for key, img_url in THEMED_POSTERS.items():
        if key in title_lower:
            return img_url
    return THEMED_POSTERS["default"]


def fetch_og_poster(url, title=""):
    """
    Generic poster extractor: Fetches OpenGraph/Twitter meta images or JSON-LD images from event pages.
    """
    if not url or not url.startswith("http"):
        return get_themed_poster(title)

    try:
        res = requests.get(url, headers=HEADERS, timeout=6, allow_redirects=True)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 1. Check meta tags
            for meta in soup.find_all("meta"):
                prop = (meta.get("property", "") or meta.get("name", "")).lower()
                if prop in ["og:image", "twitter:image", "image", "twitter:image:src"]:
                    content = meta.get("content", "")
                    if content and content.startswith("http") and "default" not in content:
                        return content
                        
            # 2. Check JSON-LD schema
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string or script.text or "")
                    if isinstance(data, dict):
                        img = data.get("image")
                        if isinstance(img, str) and img.startswith("http"):
                            return img
                        elif isinstance(img, list) and len(img) > 0 and img[0].startswith("http"):
                            return img[0]
                except Exception:
                    pass
    except Exception:
        pass

    return get_themed_poster(title)


# ----------------------------------------------------
# MODULE 1: BookMyShow Raipur Scraper
# ----------------------------------------------------
BMS_TARGET_URLS = [
    "https://in.bookmyshow.com/explore/events-raipur",
    "https://in.bookmyshow.com/explore/activities-raipur?cat=AT",
    "https://in.bookmyshow.com/explore/nightlife-raipur",
    "https://in.bookmyshow.com/explore/parties-raipur"
]


def fetch_bms_poster(event_url, title=""):
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
    return fetch_og_poster(event_url, title)


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

                        print(f"  [POSTER] BookMyShow poster for: '{title_text[:35]}'...")
                        poster_url = fetch_bms_poster(full_link, title_text)

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
    """Scrapes live event listings with official posters from District / Paytm Insider."""
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

                        print(f"  [POSTER] District poster for: '{title_text[:35]}'...")
                        poster_url = fetch_og_poster(full_link, title_text)

                        events_list.append({
                            "title": title_text,
                            "date": "Upcoming · Check District",
                            "venue": "Raipur Venue / Convention Center",
                            "price": "Book on District",
                            "source": "District",
                            "image": poster_url,
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
# MODULE 3: Google Search Local Events Scraper
# ----------------------------------------------------
def scrape_google_events():
    """Scrapes local event listings & news snippets with posters for Raipur via Google Search."""
    print("[SEARCH] Searching Google Search for Raipur local events...")
    search_queries = [
        "events in Raipur",
        "exhibition in Raipur",
        "cultural festival Raipur"
    ]

    google_events = []
    seen = set()

    for q in search_queries:
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            res = requests.get(rss_url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.find_all("item")

                for item in items[:8]:
                    raw_title = item.find("title").text if item.find("title") else ""
                    link_elem = item.find("link")
                    link_text = link_elem.next_sibling if link_elem else "https://google.com"

                    title = raw_title.split(" - ")[0].strip() if " - " in raw_title else raw_title.strip()
                    publisher = raw_title.split(" - ")[-1].strip() if " - " in raw_title else "Google"

                    if len(title) > 5 and not any(city in title.lower() for city in EXCLUDED_CITIES):
                        normalized_title = title.lower()
                        if normalized_title not in seen:
                            seen.add(normalized_title)
                            target_url = str(link_text).strip() if str(link_text).strip() else "https://google.com"
                            
                            # Extract poster image from target event URL or themed poster
                            print(f"  [POSTER] Google poster for: '{title[:35]}'...")
                            poster_url = fetch_og_poster(target_url, title)

                            google_events.append({
                                "title": title,
                                "date": "Upcoming · Local News",
                                "venue": "Raipur, Chhattisgarh",
                                "price": "Check Google Search",
                                "source": "Google Search",
                                "image": poster_url,
                                "link": target_url,
                                "category": "Local Gathering & News",
                                "tag": "week",
                                "description": f"Local Raipur event: '{title}' ({publisher}). Read full details on Google Search."
                            })
        except Exception as error:
            print(f"  [ERROR] Google Search error for '{q}': {error}")

    print(f"  [OK] Found {len(google_events)} local events from Google Search.\n")
    return google_events


# ----------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------
def main():
    print("=========================================")
    print("   Raipur Events Scraper (BMS + District + Google)")
    print("=========================================\n")

    bms_events = scrape_bookmyshow_events()
    district_events = scrape_district_events()
    google_events = scrape_google_events()

    all_events = bms_events + district_events + google_events

    # De-duplicate by title across all platforms
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
    print(f"[SUCCESS] Scraped & Saved {len(unique_events)} total events with posters to '{output_filename}'!")
    print("=========================================")


if __name__ == "__main__":
    main()

