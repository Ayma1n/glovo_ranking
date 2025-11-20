from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from time import sleep
import json, random
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # CRITICAL for GitHub Actions
options.add_argument("--no-sandbox")  # CRITICAL for GitHub Actions
options.add_argument("--disable-dev-shm-usage")  # CRITICAL for GitHub Actions
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-application-cache")
options.add_argument("--disk-cache-size=0")

driver = webdriver.Chrome(options=options)
driver.get("https://glovoapp.com/en/ma/kenitra/categories/food_1")
sleep(4)

# Handle cookie consent banner if it appears
try:
    accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
    accept_button.click()
    print("✅ Accepted cookies")
    sleep(2)
except:
    print("ℹ️ No cookie banner found or already accepted")

# Save cookies
cookies = driver.get_cookies()
with open('cookies.json', "w", encoding='utf-8') as f:
    json.dump(cookies, f, indent=2)
print(f"✅ Saved {len(cookies)} cookies to cookies.json")

wait = WebDriverWait(driver, 10)

# Wait for initial cards to appear
initial_cards = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "div.StoreCardStoreWall_bottomSection__3YMBc")
))
print(f"Initial cards found: {len(initial_cards)}")

def load_all_restaurants_smooth():
    """Scroll smoothly to load all content"""
    scroll_pause_time = random.uniform(2.9, 3.57)
    screen_height = driver.execute_script("return window.innerHeight")
    scroll_step = screen_height // 2
    
    current_position = 0
    max_height = driver.execute_script("return document.body.scrollHeight")
    
    while current_position < max_height:
        current_position += scroll_step
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        sleep(scroll_pause_time)
        
        new_max_height = driver.execute_script("return document.body.scrollHeight")
        if new_max_height > max_height:
            max_height = new_max_height
            print(f"Page grew to {max_height}px, continuing scroll...")
        
        cards = len(driver.find_elements(By.CSS_SELECTOR, "div.StoreCardStoreWall_bottomSection__3YMBc"))
        print(f"Position: {current_position}px | Cards loaded: {cards}")

# Scroll to load all restaurants
load_all_restaurants_smooth()
all_urls = []
urls = driver.find_elements(By.CSS_SELECTOR, "a.StoreCardStoreWall_wrapper__u8Dc8")
print(f"found {len(urls)}")

for u in urls:
    link = u.get_attribute("href")
    all_urls.append(link)

# ✅ NOW GET ALL CARDS AFTER SCROLLING
store_cards = driver.find_elements(By.CSS_SELECTOR, "div.StoreCardStoreWall_bottomSection__3YMBc")
print(f"\n✅ Total cards after scrolling: {len(store_cards)}\n")

# ✅ EXTRACT AND SAVE RESTAURANT DATA TO JSON
restaurants_dict = {}

for i, c in enumerate(store_cards[:50], start=1):
    try:
        name = c.find_element(By.CSS_SELECTOR, "p.StoreCardStoreWall_title__zlmbD").text
        captions = c.find_elements(By.CSS_SELECTOR, "p.pintxo-typography-caption")
        delivery_fee = captions[0].text if len(captions) > 0 else "N/A"
        score = c.find_element(By.CSS_SELECTOR, "p.pintxo-typography-caption-emphasis").text
        
        # Create restaurant object with name as key
        restaurants_dict[name] = {
            "rank": i,
            "delivery_fee": delivery_fee,  # Keep original format with MAD
            "score": score  # Keep original format with %
        }
        
        print(f"{i}: {name} : {delivery_fee} : {score}")
        
    except Exception as e:
        print(f"{i}: Error - {e}")
        # Add error entry with rank only
        error_name = f"Error_Rank_{i}"
        restaurants_dict[error_name] = {
            "rank": i,
            "delivery_fee": "N/A",
            "score": "N/A",
            "error": str(e)
        }

# ✅ SAVE RESTAURANTS DATA TO JSON FILE
with open("restaurants4_data.json", "w", encoding='utf-8') as f:
    json.dump(restaurants_dict, f, indent=2, ensure_ascii=False)

print(f"\n💾 Saved {len(restaurants_dict)} restaurants to restaurants_data.json")

# Keep the URLs file as well
with open("urls4.json", "w", encoding='utf-8') as f:
    json.dump(all_urls, f, indent=2)

print(f"💾 Saved {len(all_urls)} URLs to urls.json")

driver.quit()

print("🎯 Scraping completed successfully!")
