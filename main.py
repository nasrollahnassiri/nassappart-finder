import requests
from bs4 import BeautifulSoup
import json
import os
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN")

HEADERS = {"User-Agent": "Mozilla/5.0"}

SEEN_FILE = "seen.json"

# =========================
# TELEGRAM
# =========================

def send(chat_id, msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": msg
    })

    if response.status_code != 200:
        print("ERREUR TELEGRAM:", response.text)

# =========================
# SEEN
# =========================

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# =========================
# PARSING
# =========================

def extract_price(text):
    match = re.search(r'(\d[\d\s]*)\s?CHF', text)
    return int(match.group(1).replace(" ", "")) if match else None

def extract_rooms(text):
    match = re.search(r'(\d+\.?\d*)\s?pi', text)
    return float(match.group(1)) if match else None

def extract_surface(text):
    match = re.search(r'(\d+)\s?m²', text)
    return int(match.group(1)) if match else None

def match_zip(text, zip_min, zip_max):
    matches = re.findall(r'\b\d{4}\b', text)
    for z in matches:
        z = int(z)
        if zip_min <= z <= zip_max:
            return True
    return False

def detect_parking(text):
    return any(k in text.lower() for k in ["parking", "garage"])

def detect_availability(text):
    if "immédiate" in text.lower():
        return "Immédiate"
    match = re.search(r'dès\s([\d\.]+)', text.lower())
    return match.group(1) if match else "?"

def detect_charges(text):
    if "charges comprises" in text.lower():
        return True
    if "charges non comprises" in text.lower():
        return False
    return None

# =========================
# SCRAPER
# =========================

def scrape_immoscout():
    results = []

    url = "https://www.immoscout24.ch/en/real-estate/rent/canton-vaud?rss=true"

    r = requests.get(url, headers=HEADERS)

    soup = BeautifulSoup(r.text, "xml")

    items = soup.find_all("item")

    for item in items:
        title = item.title.text
        link = item.link.text

        text = title

        results.append((text, link))

    return results
# =========================
# MAIN
# =========================

def main():
    print("SCRIPT DEMARRE")

   listings = scrape_immoscout()

    print("NB ANNONCES TROUVEES:", len(listings))

    for text, link in listings[:5]:
        print("----")
        print(text[:200])
        print(link)

if __name__ == "__main__":
    main()