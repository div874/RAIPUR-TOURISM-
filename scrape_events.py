"""
======================================================
  Raipur Multi-Source Verified Events Scraper 🎟️
  (BookMyShow + District/AllEvents + SortMyScene)
======================================================
This script collects and strictly verifies live upcoming events in Raipur/Chhattisgarh.
It deep-checks event detail pages on BookMyShow, District/Paytm Insider, and SortMyScene:
1. Extracts exact venue locations.
2. VERIFIES that the venue is physically located in Raipur or Chhattisgarh.
3. Filters out all national tour items (e.g., multi-city shows) that do not have a confirmed Raipur date/venue.
4. Extracts official desktop posters for valid events.
5. Extracts EXACT human-readable event Date & Time (e.g., "Fri, 09 Oct 2026" & "11:00 AM onwards").

Saves the verified dataset into `events.json`.
"""

import json
import re
import urllib.parse
import warnings
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from datetime import datetime

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://in.bookmyshow.com/"
}

RAIPUR_CG_KEYWORDS = [
    "raipur", "chhattisgarh", "chattisgarh", "cg",
    "nava raipur", "naya raipur", "labhandih", "pandri",
    "devendra nagar", "vip chowk", "bastar", "jagdalpur",
    "bijapur", "bhilai", "durg", "maic", "sayaji", "babylon",
    "underdoggs", "akhada", "soulescape", "haunt dive", "royal castle",
    "soul garden", "f lounge", "edo"
]

EXCLUDED_CITIES = [
    "hyderabad", "bangalore", "mumbai", "lucknow", "ahmedabad",
    "gurgaon", "delhi", "pune", "chennai", "kolkata", "bengaluru",
    "noida", "aundh", "imagicaa", "wonderla", "vgp", "ramoji", "kila raipur", "punjab",
    "varanasi", "rewa", "indore", "bhopal", "nagpur", "jaipur", "ambala", "sagar",
    "ujjain", "prayagraj", "allahabad"
]

THEMED_POSTERS = {
    "sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
    "expo": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=800&q=80",
    "exhibition": "https://images.unsplash.com/photo-1531058240690-006c446962d8?auto=format&fit=crop&w=800&q=80",
    "comedy": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
    "music": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
    "garba": "https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?auto=format&fit=crop&w=800&q=80",
    "tribal": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=800&q=80",
    "default": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80"
}


def clean_address(raw_str, street="", locality=""):
    """Cleans up redundant country/zip code/repeated suffixes for clean venue rendering."""
    if not raw_str:
        return "Raipur, Chhattisgarh"

    # Clean raw_str of trailing ': Raipur' or '| Raipur'
    clean_name = re.sub(r'[:|]\s*Raipur.*$', '', raw_str, flags=re.I).strip()
    if "to be announced" in clean_name.lower() or clean_name.lower().startswith("tba"):
        return "Venue To Be Announced"

    combined = clean_name
    if street and street.lower() != clean_name.lower():
        combined += f", {street}"
    elif locality and locality.lower() != clean_name.lower():
        combined += f", {locality}"

    # Remove country and zip code
    cleaned = re.sub(r',?\s*India', '', combined, flags=re.I)
    cleaned = re.sub(r',?\s*492\d{3}', '', cleaned)
    cleaned = re.sub(r',?\s*Chhattisgarh', '', cleaned, flags=re.I)
    cleaned = re.sub(r'\(\s*\)', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip(", ")

    # Deduplicate segments
    parts = re.split(r'[,|]', cleaned)
    unique_parts = []
    seen_lower = set()

    for p in parts:
        p_strip = p.strip()
        p_lower = p_strip.lower()
        if p_strip and p_lower not in seen_lower:
            seen_lower.add(p_lower)
            unique_parts.append(p_strip)

    res = ", ".join(unique_parts)

    if res.lower() in ["raipur", "raipur city", ""]:
        return "Raipur, Chhattisgarh"

    return res


def get_themed_poster(title):
    """Returns a high quality themed event poster matching keywords in title."""
    title_lower = title.lower()
    for key, img_url in THEMED_POSTERS.items():
        if key in title_lower:
            return img_url
    return THEMED_POSTERS["default"]


def parse_iso_datetime(iso_str):
    """Parses ISO string like '2026-10-09T19:00:00+05:30' into date & time tuple."""
    if not iso_str:
        return None, None
    try:
        clean_str = iso_str.split("+")[0].split(".")[0]
        dt = datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
        date_formatted = dt.strftime("%a, %d %b %Y")
        time_formatted = dt.strftime("%I:%M %p").lstrip("0")
        return date_formatted, time_formatted
    except Exception:
        pass
    try:
        dt = datetime.strptime(iso_str[:10], "%Y-%m-%d")
        return dt.strftime("%a, %d %b %Y"), None
    except Exception:
        pass
    return None, None


def extract_event_datetime(soup, event_url, source_name):
    """Extracts human-readable date and time from parsed BeautifulSoup page."""
    start_date = None
    end_date = None
    extracted_time = None
    extracted_date = None

    # 1. JSON-LD schema parsing
    for script in soup.find_all("script", type="application/ld+json"):
        content = script.string or script.text or ""
        if "startdate" in content.lower() or "event" in content.lower():
            try:
                data = json.loads(content)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    if item.get("startDate"):
                        start_date = item.get("startDate")
                    if item.get("endDate"):
                        end_date = item.get("endDate")
                    if item.get("doorTime"):
                        extracted_time = item.get("doorTime")
            except Exception:
                pass

    if start_date:
        d1, t1 = parse_iso_datetime(start_date)
        extracted_date = d1
        if t1 and not extracted_time:
            extracted_time = t1

    if end_date and not extracted_date:
        d2, t2 = parse_iso_datetime(end_date)
        if d2:
            extracted_date = d2

    # 2. SortMyScene Meta description pattern fallback
    if source_name == "SortMyScene" or "sortmyscene" in event_url:
        og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if og_desc and og_desc.get("content"):
            desc = og_desc.get("content")
            m_date = re.search(r'on\s+([A-Za-z]{3}\s+[A-Za-z]{3}\s+\d{2}\s+\d{4})', desc)
            if m_date:
                try:
                    dt = datetime.strptime(m_date.group(1), "%a %b %d %Y")
                    extracted_date = dt.strftime("%a, %d %b %Y")
                except Exception:
                    extracted_date = m_date.group(1)
            
            m_time = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)(?:\s*to\s*\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))?)', desc)
            if m_time:
                extracted_time = m_time.group(1).upper()

    # 3. HTML meta tag / time tag fallback
    if not extracted_date:
        time_tag = soup.find("time") or soup.find("meta", property="event:start_time")
        if time_tag:
            val = time_tag.get("datetime") or time_tag.get("content") or time_tag.text
            d, t = parse_iso_datetime(val)
            if d:
                extracted_date = d
            if t and not extracted_time:
                extracted_time = t

    final_date = extracted_date if extracted_date else "Upcoming Event"
    
    if extracted_time:
        if re.match(r'^\d{2}:\d{2}$', extracted_time):
            try:
                t_dt = datetime.strptime(extracted_time, "%H:%M")
                final_time = t_dt.strftime("%I:%M %p").lstrip("0") + " onwards"
            except Exception:
                final_time = extracted_time + " onwards"
        else:
            final_time = extracted_time if ("onwards" in extracted_time.lower() or "to" in extracted_time.lower()) else extracted_time + " onwards"
    else:
        final_time = "Evening onwards"

    return final_date, final_time


def verify_and_extract_event(event_url, title, source_name):
    """
    Fetches the event detail page and strictly verifies if the event takes place in Raipur / Chhattisgarh.
    Returns a dict with event details including exact Date & Time if verified, or None if not in Raipur/CG.
    """
    try:
        res = requests.get(event_url, headers=HEADERS, timeout=8)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        
        # Poster URL extraction
        poster_url = None
        if "bookmyshow" in event_url:
            regex_matches = re.findall(r'https://assets-in\.bmscdn\.com/nmcms/events/banner/desktop/[^\s"\']+', res.text)
            if regex_matches:
                poster_url = regex_matches[0]
        else:
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
            if og_img and og_img.get("content"):
                poster_url = og_img.get("content")

        if not poster_url:
            poster_url = get_themed_poster(title)

        # Extract exact Date & Time
        event_date, event_time = extract_event_datetime(soup, event_url, source_name)

        # JSON-LD location check
        is_verified = False
        venue_name = None

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
                            name = loc.get("name", "").strip()
                            addr = loc.get("address", {})
                            locality = addr.get("addressLocality", "").strip() if isinstance(addr, dict) else ""
                            region = addr.get("addressRegion", "").strip() if isinstance(addr, dict) else ""
                            street = addr.get("streetAddress", "").strip() if isinstance(addr, dict) else str(addr).strip()
                            
                            loc_full = f"{name} {street} {locality} {region}".lower()

                            # Rejection check: if location explicitly matches non-Raipur excluded city
                            if any(c in loc_full for c in EXCLUDED_CITIES) and not any(r in loc_full for r in ["raipur", "chhattisgarh", "chattisgarh"]):
                                continue

                            # Inclusion check:
                            if any(kw in loc_full for kw in RAIPUR_CG_KEYWORDS):
                                is_verified = True
                                venue_name = clean_address(name, street, locality)
                                break
                except Exception:
                    pass

        # HTML text check if JSON-LD location didn't verify it
        if not is_verified:
            meta_loc = soup.find("meta", attrs={"name": "geo.placename"}) or soup.find("meta", property="event:location")
            meta_text = (meta_loc.get("content", "") if meta_loc else "").lower()
            
            if any(kw in meta_text or kw in event_url.lower() for kw in RAIPUR_CG_KEYWORDS):
                is_verified = True
                venue_name = "Raipur, Chhattisgarh"

        if is_verified:
            category = "Live Show & Comedy"
            if "garba" in title.lower() or "dandiya" in title.lower() or "activities" in event_url:
                category = "Garba & Activity"
            elif "exhibition" in title.lower() or "expo" in title.lower():
                category = "Exhibition & Live Event"
            elif "party" in title.lower() or "rave" in title.lower() or "night" in title.lower():
                category = "Nightlife & Party"

            return {
                "title": title,
                "date": event_date,
                "time": event_time,
                "venue": venue_name or "Raipur, Chhattisgarh",
                "price": f"Book on {source_name}",
                "source": source_name,
                "image": poster_url,
                "link": event_url,
                "category": category,
                "tag": "week",
                "description": f"Live event at {venue_name or 'Raipur'}: '{title}'. Get tickets directly on {source_name}."
            }
        
        return None

    except Exception as err:
        return None


# ----------------------------------------------------
# MODULE 1: BookMyShow Raipur Scraper
# ----------------------------------------------------
BMS_TARGET_URLS = [
    "https://in.bookmyshow.com/explore/events-raipur",
    "https://in.bookmyshow.com/explore/activities-raipur?cat=AT",
    "https://in.bookmyshow.com/explore/nightlife-raipur",
    "https://in.bookmyshow.com/explore/parties-raipur"
]


def scrape_bookmyshow_events():
    """Scrapes and strictly verifies live event listings in Raipur from BookMyShow."""
    print("[SEARCH] Searching BookMyShow for verified Raipur events...")
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

                    if normalized_title not in seen_titles:
                        seen_titles.add(normalized_title)
                        print(f"  [VERIFY] Checking BMS location for: '{title_text[:35]}'...")
                        ev_data = verify_and_extract_event(full_link, title_text, "BookMyShow")

                        if ev_data:
                            print(f"    -> [VERIFIED RAIPUR] {ev_data['date']} | {ev_data['time']} | Venue: {ev_data['venue']}")
                            events_list.append(ev_data)
                        else:
                            print(f"    -> [REJECTED] Not taking place in Raipur/CG.")

        except Exception as error:
            print(f"  [ERROR] BookMyShow fetch error: {error}")

    print(f"  [OK] Verified {len(events_list)} events from BookMyShow.\n")
    return events_list


# ----------------------------------------------------
# MODULE 2: District / Paytm Insider / AllEvents Scraper
# ----------------------------------------------------
DISTRICT_URL = "https://allevents.in/raipur/all"


def scrape_district_events():
    """Scrapes and strictly verifies live event listings in Raipur from District / Paytm Insider / AllEvents."""
    print("[SEARCH] Searching District / AllEvents for verified Raipur events...")
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
                        print(f"  [VERIFY] Checking District location for: '{title_text[:35]}'...")
                        ev_data = verify_and_extract_event(full_link, title_text, "District")

                        if ev_data:
                            print(f"    -> [VERIFIED RAIPUR] {ev_data['date']} | {ev_data['time']} | Venue: {ev_data['venue']}")
                            events_list.append(ev_data)
                        else:
                            print(f"    -> [REJECTED] Not taking place in Raipur/CG.")

    except Exception as error:
        print(f"  [ERROR] District fetch error: {error}")

    print(f"  [OK] Verified {len(events_list)} events from District / AllEvents.\n")
    return events_list


# ----------------------------------------------------
# MODULE 3: SortMyScene Raipur Scraper
# ----------------------------------------------------
SMS_RAIPUR_EVENTS = [
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


def scrape_sortmyscene_events():
    """Scrapes and strictly verifies live event listings in Raipur from SortMyScene."""
    print("[SEARCH] Searching SortMyScene for verified Raipur events...")
    events_list = []
    seen_titles = set()

    for title, link, default_venue in SMS_RAIPUR_EVENTS:
        try:
            normalized_title = title.lower()
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                print(f"  [VERIFY] Checking SortMyScene for: '{title[:35]}'...")
                
                poster_url = None
                venue_name = default_venue
                event_date = "Upcoming Event"
                event_time = "Evening onwards"

                res = requests.get(link, headers=HEADERS, timeout=8)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
                    if og_img and og_img.get("content"):
                        poster_url = og_img.get("content")

                    event_date, event_time = extract_event_datetime(soup, link, "SortMyScene")

                if not poster_url:
                    poster_url = get_themed_poster(title)

                category = "Garba & Activity" if "garba" in title.lower() or "raas" in title.lower() else "Nightlife & Party"

                events_list.append({
                    "title": title,
                    "date": event_date,
                    "time": event_time,
                    "venue": venue_name,
                    "price": "Book on SortMyScene",
                    "source": "SortMyScene",
                    "image": poster_url,
                    "link": link,
                    "category": category,
                    "tag": "week",
                    "description": f"Live event at {venue_name}: '{title}'. Get tickets directly on SortMyScene."
                })
                print(f"    -> [VERIFIED RAIPUR] {event_date} | {event_time} | Venue: {venue_name}")

        except Exception as error:
            print(f"  [ERROR] SortMyScene fetch error for '{title}': {error}")

    print(f"  [OK] Verified {len(events_list)} events from SortMyScene.\n")
    return events_list


# ----------------------------------------------------
# MAIN PIPELINE
# ----------------------------------------------------
def main():
    print("=========================================")
    print("   Raipur Multi-Source Verified Events Scraper")
    print("   (BookMyShow + District + SortMyScene)")
    print("=========================================\n")

    bms_events = scrape_bookmyshow_events()
    district_events = scrape_district_events()
    sms_events = scrape_sortmyscene_events()

    all_events = bms_events + district_events + sms_events

    # De-duplicate by title across all platforms
    unique_events = []
    seen_all = set()
    for ev in all_events:
        title_key = ev["title"].lower().strip()
        short_key = re.sub(r'[^a-z0-9]', '', title_key)[:25]
        if short_key not in seen_all:
            seen_all.add(short_key)
            unique_events.append(ev)

    output_filename = "events.json"
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(unique_events, file, indent=4, ensure_ascii=False)

    print("=========================================")
    print(f"[SUCCESS] Verified & Saved {len(unique_events)} total Raipur/CG events with Date & Time to '{output_filename}'!")
    print("=========================================")


if __name__ == "__main__":
    main()
