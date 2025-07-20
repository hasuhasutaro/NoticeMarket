import time
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://bitjita.com/"
INTERVAL_SEC = 10

def scrape_and_print():
    try:
        response = requests.get(TARGET_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # サイト構造に応じて主要情報を抽出
        title = soup.title.string if soup.title else "No title"
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {title}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Start scraping {TARGET_URL} every {INTERVAL_SEC} seconds...")
    while True:
        scrape_and_print()
        time.sleep(INTERVAL_SEC)
