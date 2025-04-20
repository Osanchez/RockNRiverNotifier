import os
import time
import random
import uuid
import json
import http.client
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://roundrocktexas.aluvii.com/store/shop/categoryproducts?categoryId=1"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")


class PushoverAPI:
    def __init__(self, token, user_key):
        self.http_client = http.client.HTTPSConnection("api.pushover.net", 443)
        self.token = token
        self.user_key = user_key

    def send_notification(self, message, title=None):
        payload = {
            "token": self.token,
            "user": self.user_key,
            "message": message,
        }
        if title:
            payload["title"] = title

        try:
            self.http_client.request(
                "POST",
                "/1/messages.json",
                urllib.parse.urlencode(payload),
                { "Content-type": "application/x-www-form-urlencoded" }
            )

            response = self.http_client.getresponse()
            data = response.read()

            if response.status == 200:
                result = json.loads(data.decode())
                return result.get("status") == 1
            else:
                print(f"Request failed with status {response.status}: {data.decode()}")
                return False

        except Exception as e:
            print(f"Exception during Pushover notification: {e}")
            return False

def initialize_driver() -> webdriver.Chrome:
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-cache")
    options.add_argument("--disk-cache-size=0")
    options.add_argument("--remote-debugging-port=9222")

    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def wait_for_page_load(driver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

def get_cache_busted_url() -> str:
    return f"{BASE_URL}&_={uuid.uuid4()}"

def navigate_to_rock_n_river(driver):
    url = get_cache_busted_url()
    driver.get(url)
    wait_for_page_load(driver)

def page_has_changed(driver) -> bool:
    soup = BeautifulSoup(driver.page_source, "html.parser")

    add_to_cart_span = soup.find("span", id="addToCart-2B-4")
    if not add_to_cart_span:
        print("Add to Cart element not found.")
        return False

    parent_div = add_to_cart_span.find_parent("div", class_="divAddToCartButton")
    if not parent_div:
        print("Parent div not found.")
        return False

    style = parent_div.get("style", "")
    return "display:none" not in style.lower()

if __name__ == "__main__":
    print("Starting Rock'N River Alert script...")
    pushover = PushoverAPI(token=PUSHOVER_API_TOKEN, user_key=PUSHOVER_USER_KEY)
    driver = initialize_driver()
    navigate_to_rock_n_river(driver)

    if DEBUG_MODE == True:
        print("DEBUG_MODE is enabled. Sending dry-run notification and exiting...")
        pushover.send_notification(
            message="🚨 DEBUG MODE: Dry run - 'Season Pool Pass Family' alert would be sent here. view season pass availability here: https://roundrocktexas.aluvii.com/store/shop/categoryproducts?categoryId=1",
            title="Rock'N River DEBUG"
        )
        driver.quit()
        print("Dry-run complete. Driver closed. Exiting script.")
        exit(0)

    while True:
        if page_has_changed(driver):
            print("🚨 Page has changed — 'Add to Cart' is now visible!")

            success = pushover.send_notification(
                message="🚨 'Season Pool Pass Family' is now available!\n\nVisit the page to buy: https://roundrocktexas.aluvii.com/store/shop/categoryproducts?categoryId=1",
                title="Rock'N River Season Pool Pass Alert"
            )

            if success:
                print("✅ Pushover notification sent successfully.")
            else:
                print("❌ Failed to send Pushover notification.")
            break

        sleep_time = random.randint(10, 15)
        print(f"Sleeping for {sleep_time} seconds before refreshing...")
        time.sleep(sleep_time)

        print("Refreshing page with cache-busting URL...")
        navigate_to_rock_n_river(driver)
    
    driver.quit()
    print("Driver closed. Exiting script.")
