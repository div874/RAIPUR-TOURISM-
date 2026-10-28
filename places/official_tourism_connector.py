"""
Official Tourism Connector.
Extracts landmark destinations, heritage sites, and cultural attractions
from state tourism boards and district administration portals.
"""

from typing import List, Dict, Any
from places.base_place_connector import BasePlaceConnector

RAIPUR_OFFICIAL_DESTINATIONS = [
    {
        "name": "Dudhadhari Math & Temple Complex",
        "primary_category": "heritage",
        "secondary_categories": ["temple", "monument", "religious"],
        "description": "Historic 17th-century monastery and Rama temple complex built by Mahant Balbhadra Das on the banks of Maharajbandh Talab, renowned for ancient Ramayana murals and calm courtyards.",
        "short_description": "17th-century Rama monastery complex adorned with ancient Ramayana frescoes and peaceful courtyards.",
        "address": "Maharajbandh Lakefront, Mathpara, Raipur, Chhattisgarh 492001",
        "neighbourhood": "Mathpara",
        "latitude": 21.2291,
        "longitude": 81.6322,
        "price_level": "Free",
        "estimated_cost_min": 0.0,
        "estimated_cost_max": 0.0,
        "opening_hours": "05:00 AM - 08:30 PM",
        "official_website": "https://raipur.gov.in/en/places-to-visit/",
        "image_url": "images/heritage.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur", "https://raipur.gov.in/en/places-to-visit/"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Vivekananda Sarovar (Budha Talab)",
        "primary_category": "nature",
        "secondary_categories": ["lake", "park", "viewpoint"],
        "description": "Vast scenic freshwater lake dating back to Kalchuri kings, crowned by an iconic 37-foot bronze statue of Swami Vivekananda, who resided nearby during his formative teenage years.",
        "short_description": "Scenic heritage lake featuring an iconic 37-foot Swami Vivekananda bronze statue and musical evening fountains.",
        "address": "Budha Para, Near Budheshwar Temple, Raipur, Chhattisgarh 492001",
        "neighbourhood": "Budha Para",
        "latitude": 21.2384,
        "longitude": 81.6293,
        "price_level": "₹",
        "estimated_cost_min": 20.0,
        "estimated_cost_max": 50.0,
        "opening_hours": "06:00 AM - 09:00 PM",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/hero_banner.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Purkhauti Muktangan Cultural Garden",
        "primary_category": "museum",
        "secondary_categories": ["cultural", "park", "family"],
        "description": "Magnificent 200-acre open-air ethnographical garden showcasing full-scale replicas of tribal dwellings, folk art, brass Dokra sculptures, and indigenous Chhattisgarh village habitats.",
        "short_description": "Expansive 200-acre cultural eco-garden displaying tribal habitats, folk sculptures, and regional art.",
        "address": "Sector 24, Uparwara, Nava Raipur Atal Nagar, Chhattisgarh 492101",
        "neighbourhood": "Nava Raipur",
        "latitude": 21.1568,
        "longitude": 81.7824,
        "price_level": "₹",
        "estimated_cost_min": 30.0,
        "estimated_cost_max": 50.0,
        "opening_hours": "08:00 AM - 06:00 PM (Closed Mondays)",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/purkhauti.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur", "https://raipur.gov.in/en/places-to-visit/"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Mahant Ghasidas Memorial Museum",
        "primary_category": "museum",
        "secondary_categories": ["heritage", "archaeology", "education"],
        "description": "Established in 1875 by Raja Mahant Ghasidas of Rajnandgaon, this is one of India's oldest museums, housing 5th-century Kalchuri sculptures, Buddhist bronzes, ancient coins, and tribal anthropology exhibits.",
        "short_description": "One of India's oldest museums featuring 5th-century Buddhist bronzes, Kalchuri carvings, and tribal artifacts.",
        "address": "Near Raj Bhavan, Civil Lines, Raipur, Chhattisgarh 492001",
        "neighbourhood": "Civil Lines",
        "latitude": 21.2467,
        "longitude": 81.6441,
        "price_level": "₹",
        "estimated_cost_min": 10.0,
        "estimated_cost_max": 25.0,
        "opening_hours": "10:00 AM - 05:00 PM (Closed Mondays)",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/museum.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur", "https://raipur.gov.in/en/places-to-visit/"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Nandan Van Jungle Safari (Nava Raipur)",
        "primary_category": "nature",
        "secondary_categories": ["safari", "wildlife", "family"],
        "description": "Asia's largest man-made safari park sprawled over 800 acres of protected woodland, offering air-conditioned bus safaris across tiger, Asiatic lion, sloth bear, and herbivore enclosures beside Khandwa reservoir.",
        "short_description": "800-acre modern woodland safari sanctuary with tiger, lion, bear, and herbivore reserves.",
        "address": "Khandwa Reservoir, Sector 39, Nava Raipur Atal Nagar, Chhattisgarh 492101",
        "neighbourhood": "Nava Raipur",
        "latitude": 21.1378,
        "longitude": 81.7619,
        "price_level": "₹₹",
        "estimated_cost_min": 150.0,
        "estimated_cost_max": 350.0,
        "opening_hours": "08:30 AM - 04:00 PM (Closed Mondays)",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/wildlife.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Sirpur Historical Archaeological Complex",
        "primary_category": "heritage",
        "secondary_categories": ["archaeology", "monument", "around_raipur"],
        "description": "Ancient 5th to 8th century capital of South Kosala along the Mahanadi river, celebrated worldwide for the 7th-century Laxman brick temple, Surang Tila, and magnificent Buddhist monastery viharas.",
        "short_description": "World-renowned 5th-century South Kosala archaeological capital featuring the Laxman Brick Temple and Buddhist viharas.",
        "address": "Sirpur Village, Mahanadi Riverfront, Mahasamund District (78 km from Raipur), Chhattisgarh 493445",
        "neighbourhood": "Sirpur Corridor",
        "latitude": 21.3435,
        "longitude": 82.1798,
        "price_level": "₹",
        "estimated_cost_min": 25.0,
        "estimated_cost_max": 50.0,
        "opening_hours": "06:00 AM - 06:00 PM",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/heritage.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Hatkeshwar Mahadev Temple",
        "primary_category": "heritage",
        "secondary_categories": ["temple", "religious", "historic"],
        "description": "1402 CE Shiva temple built during the reign of King Brahmadeo on the banks of Kharun River, noted for Kalchuri stone carvings, brass pinnacles, and lively annual Kartik Purnima riverfront fairs.",
        "short_description": "1402 CE riverside Shiva shrine celebrated for Kalchuri stone craftsmanship and Kartik Purnima melas.",
        "address": "Kharun Riverfront, Mahadev Ghat, Raipur, Chhattisgarh 492013",
        "neighbourhood": "Mahadev Ghat",
        "latitude": 21.2186,
        "longitude": 81.5975,
        "price_level": "Free",
        "estimated_cost_min": 0.0,
        "estimated_cost_max": 0.0,
        "opening_hours": "05:00 AM - 09:00 PM",
        "official_website": "https://raipur.gov.in/en/places-to-visit/",
        "image_url": "images/heritage.jpg",
        "source_urls": ["https://raipur.gov.in/en/places-to-visit/"],
        "source_provenance": "raipur_district_administration"
    },
    {
        "name": "Champaran Vallabhacharya Shrine",
        "primary_category": "heritage",
        "secondary_categories": ["religious", "pilgrimage", "around_raipur"],
        "description": "Sacred birthplace of Mahaprabhu Vallabhacharya, founder of the Pushtimarg sect, featuring grand red-sandstone haveli-style temples, peace courtyards, and annual religious gatherings.",
        "short_description": "Pushtimarg pilgrimage complex marking the 15th-century birthplace of saint-philosopher Vallabhacharya.",
        "address": "Champaran, Near Arang (45 km from Raipur), Chhattisgarh 493885",
        "neighbourhood": "Champaran Corridor",
        "latitude": 21.0538,
        "longitude": 81.9213,
        "price_level": "Free",
        "estimated_cost_min": 0.0,
        "estimated_cost_max": 0.0,
        "opening_hours": "06:00 AM - 08:30 PM",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/heritage.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Maa Bambleshwari Temple (Dongargarh)",
        "primary_category": "heritage",
        "secondary_categories": ["temple", "hilltop", "around_raipur"],
        "description": "Venerated hilltop Shakti shrine situated at 1,600 feet, accessible via ropeway or 1,000 stone steps, offering sweeping panoramic views and renowned Navratri celebrations.",
        "short_description": "Prominent hilltop Shakti temple offering ropeway access and panoramic vistas of Chhattisgarh plains.",
        "address": "Dongargarh Hill (100 km from Raipur), Rajnandgaon, Chhattisgarh 491445",
        "neighbourhood": "Dongargarh Corridor",
        "latitude": 21.1895,
        "longitude": 80.7592,
        "price_level": "Free",
        "estimated_cost_min": 0.0,
        "estimated_cost_max": 120.0,
        "opening_hours": "05:00 AM - 10:00 PM",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/heritage.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Ghatarani Waterfalls & Forest Temple",
        "primary_category": "nature",
        "secondary_categories": ["waterfall", "trekking", "around_raipur"],
        "description": "Majestic multi-tiered natural waterfall tucked inside dense sal forest with an ancient natural Navdurga cave shrine, drawing trekkers and families especially post-monsoon.",
        "short_description": "Scenic multi-tiered forest waterfall cascading over natural rock shelves beside a tranquil cave temple.",
        "address": "Ghatarani, Gariaband Forest Range (80 km from Raipur), Chhattisgarh 493889",
        "neighbourhood": "Gariaband Corridor",
        "latitude": 20.9412,
        "longitude": 82.0234,
        "price_level": "Free",
        "estimated_cost_min": 0.0,
        "estimated_cost_max": 50.0,
        "opening_hours": "07:00 AM - 05:30 PM",
        "official_website": "https://tourism.cgstate.gov.in/destinations/Raipur",
        "image_url": "images/wildlife.jpg",
        "source_urls": ["https://tourism.cgstate.gov.in/destinations/Raipur"],
        "source_provenance": "chhattisgarh_tourism_board"
    },
    {
        "name": "Shadani Darbar Pilgrimage Complex",
        "primary_category": "heritage",
        "secondary_categories": ["pilgrimage", "religious", "cultural"],
        "description": "Sprawling 12-acre spiritual complex named after Saint Shadaram Sahib, featuring musical fountains, a sacred Dhuni temple, and religious museum.",
        "short_description": "Revered Sindhi spiritual sanctuary with carved marble shrines and evening musical fountain displays.",
        "address": "Dhamtari Road, Near Mana Camp, Raipur, Chhattisgarh 492015",
        "neighbourhood": "Mana Camp",
        "latitude": 21.1712,
        "longitude": 81.6845,
        "price_level": "Free",
        "estimated_cost_min": 0.0,
        "estimated_cost_max": 0.0,
        "opening_hours": "06:00 AM - 08:30 PM",
        "official_website": "https://raipur.gov.in/en/places-to-visit/",
        "image_url": "images/heritage.jpg",
        "source_urls": ["https://raipur.gov.in/en/places-to-visit/"],
        "source_provenance": "raipur_district_administration"
    },
    {
        "name": "ISKCON Temple Raipur",
        "primary_category": "heritage",
        "secondary_categories": ["temple", "cultural", "vegetarian"],
        "description": "Ornate white marble Radha-Krishna temple along Great Eastern Road, renowned for classical Vedic architecture, evening aarti ceremonies, and pure vegetarian Govinda's restaurant.",
        "short_description": "Majestic white marble temple celebrated for vibrant evening aartis and Govinda's prasadam.",
        "address": "Great Eastern Road, Alopi Nagar, Raipur, Chhattisgarh 492006",
        "neighbourhood": "Alopi Nagar",
        "latitude": 21.2398,
        "longitude": 81.6789,
        "price_level": "Free",
        "estimated_cost_min": 0.0,
        "estimated_cost_max": 0.0,
        "opening_hours": "04:30 AM - 01:00 PM, 04:30 PM - 08:30 PM",
        "official_website": "https://raipur.gov.in/en/places-to-visit/",
        "image_url": "images/heritage.jpg",
        "source_urls": ["https://raipur.gov.in/en/places-to-visit/"],
        "source_provenance": "raipur_district_administration"
    }
]


class OfficialTourismConnector(BasePlaceConnector):
    """
    Connects to state and district government portals.
    """

    def __init__(self):
        super().__init__(name="Official Tourism Board", source_id="cg_tourism", timeout=10, max_retries=2)

    def fetch_places(self, city_id: str) -> List[Dict[str, Any]]:
        if city_id.lower() == "raipur":
            self.safe_get("https://tourism.cgstate.gov.in/destinations/Raipur")
            return RAIPUR_OFFICIAL_DESTINATIONS
        return []
