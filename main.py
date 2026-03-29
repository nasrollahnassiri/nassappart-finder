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
    requests.post(url, data={"chat_id": chat_id, "text": msg})

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

def scrape_homegate():
    results = []

    url = "https://www.homegate.ch/rent/real-estate/canton-vaud/matching-list"

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "lxml")

    listings = soup.find_all("article")

    for l in listings:
        try:
            text = l.get_text(" ", strip=True)
            link = "https://www.homegate.ch" + l.find("a")["href"]

            results.append((text, link))
        except:
            pass

    return results

# =========================
# MAIN
# =========================

def main():
    with open("config.json") as f:
        config = json.load(f)

    seen = load_seen()
    listings = scrape_homegate()

    for name, profile in config["profiles"].items():

        for text, link in listings:

            if link in seen:
                continue

            price = extract_price(text)
            rooms = extract_rooms(text)
            surface = extract_surface(text)

            if not price or not rooms:
                continue

            if price > profile["max_rent"]:
                continue

            if rooms < profile["min_rooms"]:
                continue

            if not match_zip(text, profile["zip_min"], profile["zip_max"]):
                continue

            charges = detect_charges(text)
            if profile["charges"] and charges is False:
                continue

            availability = detect_availability(text)
            if profile["availability"] and availability == "?":
                continue

            msg = f"""
🏠 {rooms} pièces
💰 {price} CHF
📐 {surface or '?'} m²
🚗 {'Oui' if detect_parking(text) else 'Non'}
📅 {availability}

👉 {link}
"""

            send(profile["chat_id"], msg.strip())
            seen.add(link)

    save_seen(seen)

if __name__ == "__main__":
    main()