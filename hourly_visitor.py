import os
import time
import random
import logging
import urllib.request
from playwright.sync_api import sync_playwright

TARGET_URL = os.getenv("TARGET_URL", "https://earth-sp-nda.vercel.app/")
DWELL_TIME = int(os.getenv("DWELL_TIME", "300"))
HEADLESS = True

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720}
]

LOCALES = ["en-US", "en-GB", "en-IN", "en-CA", "en-AU"]

def get_random_proxy():
    """Fetch a dynamic public proxy so Vercel receives a unique IP on every run."""
    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            proxies = resp.read().decode('utf-8').strip().splitlines()
            if proxies:
                selected = random.choice(proxies).strip()
                logging.info(f"Selected random proxy IP: {selected}")
                return f"http://{selected}"
    except Exception as e:
        logging.warning(f"Could not fetch dynamic proxy list: {e}")
    return None

def visit_and_stay():
    selected_ua = random.choice(USER_AGENTS)
    selected_vp = random.choice(VIEWPORTS)
    selected_locale = random.choice(LOCALES)
    proxy_server = get_random_proxy()

    launch_args = {
        "headless": HEADLESS,
        "args": ["--disable-blink-features=AutomationControlled"]
    }
    if proxy_server:
        launch_args["proxy"] = {"server": proxy_server}

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(**launch_args)
        except Exception as e:
            logging.warning(f"Proxy launch failed ({e}), falling back to direct connection.")
            launch_args.pop("proxy", None)
            browser = p.chromium.launch(**launch_args)

        context = browser.new_context(
            user_agent=selected_ua,
            viewport=selected_vp,
            locale=selected_locale
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            logging.info(f"Navigating to {TARGET_URL}...")
            page.goto(TARGET_URL, timeout=60000, wait_until="networkidle")
            time.sleep(3)
            page.evaluate("window.scrollBy(0, 400)")
            time.sleep(2)
            logging.info(f"Loaded {TARGET_URL}. Dwell time remaining: {DWELL_TIME - 5}s...")
            time.sleep(max(0, DWELL_TIME - 5))
            logging.info("Stay complete. Closing browser.")
        except Exception as e:
            logging.error(f"Visit interrupted: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    visit_and_stay()
    
