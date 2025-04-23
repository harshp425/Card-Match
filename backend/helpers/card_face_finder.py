import json
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 1) load your dataset
DATASET_PATH = '/Users/rpking/Documents/CS4300/4300-Flask-Template-JSON/backend/dataset/dataset.json'
with open(DATASET_PATH, 'r') as f:
    cards = json.load(f)

# 2) headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36'
}

# 3) for each card, fetch the Bing Images page and parse the first thumbnail URL
for card in cards:
    name = card.get('name', '')
    query = urllib.parse.quote_plus(f"{name} credit card logo")
    url = f'https://www.bing.com/images/search?q={query}&FORM=HDRSC2'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️  Failed to fetch for '{name}': {e}")
        card['image_url'] = None
        continue

    soup = BeautifulSoup(resp.text, 'html.parser')
    first = soup.find('a', class_='iusc')
    if first and first.has_attr('m'):
        try:
            meta = json.loads(first['m'])
            card['image_url'] = meta.get('murl')
        except Exception:
            card['image_url'] = None
    else:
        card['image_url'] = None

    print(f"→ {name}: {card['image_url']}")
    # polite pause to avoid being blocked
    time.sleep(random.uniform(1.0, 2.5))

# 4) overwrite your original dataset with the new field injected
with open(DATASET_PATH, 'w') as f:
    json.dump(cards, f, indent=2)

print("✅ dataset.json updated in place with image_url for each card.")
import json
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 1) load your dataset
DATASET_PATH = 'dataset.json'
with open(DATASET_PATH, 'r') as f:
    cards = json.load(f)

# 2) headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36'
}

# 3) for each card, fetch the Bing Images page and parse the first thumbnail URL
for card in cards:
    name = card.get('name', '')
    query = urllib.parse.quote_plus(f"{name} credit card logo")
    url = f'https://www.bing.com/images/search?q={query}&FORM=HDRSC2'
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️  Failed to fetch for '{name}': {e}")
        card['image_url'] = None
        continue

    soup = BeautifulSoup(resp.text, 'html.parser')
    first = soup.find('a', class_='iusc')
    if first and first.has_attr('m'):
        try:
            meta = json.loads(first['m'])
            card['image_url'] = meta.get('murl')
        except Exception:
            card['image_url'] = None
    else:
        card['image_url'] = None

    print(f"→ {name}: {card['image_url']}")
    # polite pause to avoid being blocked
    time.sleep(random.uniform(1.0, 2.5))

# 4) overwrite your original dataset with the new field injected
with open(DATASET_PATH, 'w') as f:
    json.dump(cards, f, indent=2)

print("✅ dataset.json updated in place with image_url for each card.")
