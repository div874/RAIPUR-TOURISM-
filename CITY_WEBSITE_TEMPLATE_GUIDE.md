# City Portal Website Expansion Framework & Template Guide
> **"Hamara [City Name]" City Website Replication Blueprint**

This document serves as the master guide, technical specification, and asset checklist for building personalized, state-of-the-art city portal websites (similar to *Hamara Raipur / RaipurTales*) for any city in India (e.g., *Hamara Jaipur, Hamara Indore, Hamara Varanasi, Hamara Kochi, Hamara Chandigarh*).

---

## 1. Tech Stack Overview

| Component | Technology | Rationale & Usage |
| :--- | :--- | :--- |
| **Core Architecture** | HTML5 + CSS3 + Vanilla JS (ES6+) | Blazing-fast load times, zero-build step required, lightweight deployment on static hosts (Netlify, Vercel, GitHub Pages). |
| **CSS Framework** | Custom CSS + Bootstrap 5.3 Grid | Flexible layout utility, responsive grid, modal popups, and custom root CSS design tokens for instant city color re-theming. |
| **Icon System** | Lucide Icons (`lucide.min.js`) | Clean, scalable vector SVG icon set rendered automatically client-side. |
| **Typography** | Google Fonts: `Outfit` (Primary Display) & `Inter` (Body/UI) | Modern, warm Indian web aesthetic with high legibility across mobile & desktop. |
| **Live Weather Engine** | Open-Meteo Forecast API (REST, Free, No API key needed) | Fetches real-time temperature, condition, feels-like temp, and low/high forecast based on city latitude/longitude. |
| **AI Guide Assistant** | Hybrid AI Architecture (API + Resilient Local Knowledge Engine) | Dual-layer search: attempts live LLM endpoint query (with 4s timeout) and seamlessly falls back to local city knowledge engine without ever failing. |
| **Interactive Components** | ScrollExpand Hero (Vanilla JS), Timeline Switcher, Video Modal Playlist | Creates a dynamic, "wow-factor" visual experience on the home page. |

---

## 2. Typography & Color Theme Tokens

### Fonts
```html
<!-- Include Google Fonts in <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```
- **Primary Display Font (`--font-primary`)**: `'Outfit', sans-serif` (Hero headings, city title, section titles, card headers).
- **Secondary Body Font (`--font-body`)**: `'Inter', sans-serif` (Paragraphs, nav links, badges, search bar text).

### City Color Palette Preset Guide
Each city receives a custom CSS Root color theme that reflects its cultural personality:

```css
/* Add to top of css/city-theme.css */
:root {
  /* Default: Raipur (Terracotta & Gold) */
  --city-primary: #d94e28;
  --city-primary-rgb: 217, 78, 40;
  --city-secondary: #e28d38;
  --city-accent: #ffb74d;
  --city-bg-dark: #121820;
  --city-text-dark: #1e293b;
  --city-card-bg: #ffffff;
  --city-border-radius: 16px;
}

/* Example: Jaipur Theme (Pink & Sandstone) */
body.theme-jaipur {
  --city-primary: #d84364;
  --city-primary-rgb: 216, 67, 100;
  --city-secondary: #f3a852;
  --city-accent: #ffe0b2;
}

/* Example: Indore Theme (Emerald & Heritage Gold) */
body.theme-indore {
  --city-primary: #1e824c;
  --city-primary-rgb: 30, 130, 76;
  --city-secondary: #f5ab35;
  --city-accent: #a3e4d7;
}

/* Example: Varanasi Theme (Sacred Saffron & Indigo) */
body.theme-varanasi {
  --city-primary: #e65100;
  --city-primary-rgb: 230, 81, 0;
  --city-secondary: #283593;
  --city-accent: #ffd54f;
}
```

---

## 3. Explicitly Required City Inputs Checklist Matrix

To launch a new city website, **someone must explicitly provide the following assets and data points**:

| # | Asset / Input | Required Format | Description & Purpose |
| :-: | :--- | :--- | :--- |
| **1** | **City Name & State** | String (e.g. "Jaipur, Rajasthan") | City title used across headers, metadata, title tags, and hero banners. |
| **2** | **Personalized City Logo** | SVG or Transparent PNG (`logo.png`) | Custom branding logo featuring local heritage icons (e.g., Raipur Swami Vivekananda statue, Jaipur Hawa Mahal, Indore Rajwada). |
| **3** | **Home Banner City Video** | MP4 Video file (`hero_video.mp4`) | 1080p landscape video loop (15-30s duration, under 20MB) showcasing city drone shots, streets, lakes, and life. |
| **4** | **Video Poster Image** | High-Res JPG (`hero_poster.jpg`) | Poster image displayed before video loads or on mobile data saver mode. |
| **5** | **GPS Coordinates** | Latitude & Longitude (e.g., Jaipur: `26.9124, 75.7873`) | Used in `js/city-weather.js` to automatically fetch live weather & temperature. |
| **6** | **Historical Eras & Timeline** | JSON / Array of 5-8 Milestones | Eras, dates, titles, descriptions, and banner images for the interactive timeline (e.g., Ancient roots, Dynasty era, Modern statehood). |
| **7** | **Top Attractions Photography** | 6-10 JPG/WebP photos (800x600px) | High quality photos of key landmarks, nature spots, museums, and temples. |
| **8** | **Culinary Delicacies List** | Dishtitles, descriptions, food photos | Authentic local street foods, traditional meals, famous food markets, and sweet specialties. |
| **9** | **AI Knowledge Base Data** | Dictionary / JSON object | Specific local answers for: 1-day itinerary, famous food, best sunset spots, turfs/sports arenas, heritage stories, transport hubs. |
| **10** | **Video Reel Playlist** | YouTube Video IDs & Titles (3-5 videos) | Video showcase list for the modal video player. |
| **11** | **Emergency & Tourist Helplines** | Phone numbers & Addresses | Tourist Police, Ambulance, Traffic Helpline, Railway/Airport desk. |

---

## 4. Key Learnings & Architecture Findings from *Hamara Raipur*

1. **Resilient AI Search Assistant (Zero-Downtime Design)**
   - External LLM APIs can face CORS limits, expired keys, or latency.
   - *Solution Implemented*: A dual-layer function in `raipurtales.js` that attempts the live API with an `AbortController` (4-second timeout). If the API fails or times out, it gracefully falls back to `getSmartFallbackResponse(query)` using local keyword matching. **The user never encounters an error message.**

2. **ScrollExpand Hero Banner Effect**
   - The hero container dynamically expands smoothly on mouse scroll or wheel gesture from a 40% window frame to full-screen background video, creating an immersive entrance.

3. **Auto-Caching Weather Widget**
   - Weather API data is cached in `localStorage` for 15 minutes. This reduces external HTTP traffic and makes page load instantaneous on repeat visits.

4. **Category Discovery Filters**
   - Pure client-side jQuery filtering allows users to instantly tab through `All`, `Heritage`, `Nature`, `Culinary`, `Modern`, and `Spiritual` without page reloads.

---

## 5. Quick-Start Implementation Blueprint

### Step 1: Copy Template Structure
```
/hamara-[city-name]/
├── index.html              <-- Main Home Page Template
├── explore.html            <-- Attractions & Landmarks
├── culture.html            <-- History, Heritage & Arts
├── eat.html                <-- Food & Culinary Scene
├── events.html             <-- City Events & Festivals
├── plan-your-visit.html    <-- Itineraries & Transport
├── contribute.html         <-- Community Contributions
├── css/
│   └── city-theme.css      <-- Reusable design tokens & city styles
├── js/
│   ├── city-config.js      <-- Centralized city data file
│   └── city-core.js        <-- Interactive JS engine & AI fallback
└── images/
    ├── logo.png            <-- City Logo
    └── hero_poster.jpg     <-- Video poster
```

### Step 2: Configure Centralized City Data (`js/city-config.js`)
```javascript
const CITY_CONFIG = {
  cityName: "Jaipur",
  stateName: "Rajasthan",
  tagline: "The Pink City of Heritage, Palaces & Craft",
  weather: {
    lat: 26.9124,
    lon: 75.7873
  },
  theme: {
    primaryColor: "#d84364",
    secondaryColor: "#f3a852"
  },
  aiFallbackResponses: {
    food: "Jaipur is world-famous for Dal Baati Churma, Pyaz Kachori at Rawat, Ghewar, and Laal Maas. Explore Johari Bazaar for authentic street eats!",
    sunset: "Best sunset views in Jaipur: Nahargarh Fort overlooking the pink city, Jal Mahal Lake promenade, and Patrika Gate.",
    turfs: "Top turfs and sports grounds in Jaipur include SMS Stadium, Mansarovar Turf Arenas, and Turf Park Vaishali Nagar.",
    heritage: "Must-visit heritage sites: Hawa Mahal, Amer Fort, City Palace, Jantar Mantar, and Albert Hall Museum."
  }
};
```

---

## 6. Summary of Action Items for Launching Next City

1. Select City (e.g. *Indore* or *Jaipur*).
2. Gather Assets using Section 3 Matrix (Logo SVG, 1080p Hero Video, 8-10 Photos, GPS Coordinates).
3. Clone existing repository layout.
4. Update `js/city-config.js` and set root CSS colors in `css/city-theme.css`.
5. Deploy static site to web server / CDN!
