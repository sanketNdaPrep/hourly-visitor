import os
import time
import logging
from playwright.sync_api import sync_playwright

TARGET_URL = os.getenv("TARGET_URL", "https://earth-sp-nda.vercel.app/")
DWELL_TIME = int(os.getenv("DWELL_TIME", "300"))
HEADLESS = True

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

def visit_and_stay():
    logging.info(f"Launching browser to visit {TARGET_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        try:
            page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
            logging.info(f"Loaded {TARGET_URL}. Staying active for {DWELL_TIME // 60} minutes...")
            time.sleep(DWELL_TIME)
            logging.info("Stay complete. Closing context.")
        except Exception as e:
            logging.error(f"Error during visit: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    visit_and_stay()
