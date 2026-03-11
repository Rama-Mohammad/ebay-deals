from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import time

# setup for driver
def setup_driver():
    options = Options()
    #options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    return driver

# for lazy loading
def scroll_page(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scrape_products(driver):

    # explicit wait for at least one element to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'itemtile')]"))
    )

    products = []
    product_elements = driver.find_elements(By.XPATH, "//div[contains(@class,'itemtile')]")

    # try except to handle errors
    for product in product_elements:
        try:
            title = product.find_element(By.XPATH, ".//span[@itemprop='name']").text
        except:
            title = "N/A"
        try:
            discounted_price = product.find_element(By.XPATH, ".//span[@itemprop='price']").text
        except:
            discounted_price = "N/A"
        try:
            original_price = product.find_element(By.XPATH, ".//span[contains(@class,'itemtile-price-strikethrough')]").text
        except:
            original_price = "N/A"
        try:
            shipping = product.find_element(By.XPATH, ".//span[contains(@class,'dne-itemtile-delivery')]").text
        except:
            shipping = "N/A"
        try:
            link = product.find_element(By.XPATH, ".//a[@itemprop='url']")
            item_url = link.get_attribute("href")
        except:
            item_url = "N/A"

        # got it from old lab
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        products.append({
            "timestamp": timestamp,
            "title": title,
            "price": discounted_price,
            "original_price": original_price,
            "shipping": shipping,
            "item_url": item_url
        })
    return products

# prepare + save to csv file
def save_to_csv(products, file_name="ebay_tech_deals.csv"):
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp", "title", "price", "original_price", "shipping", "item_url"])

    new_df = pd.DataFrame(products)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(file_name, index=False)
    print(f"Saved {len(products)} products to {file_name}")

# from old lab
def main():
    driver = setup_driver()
    driver.get("https://www.ebay.com/globaldeals/tech")
    scroll_page(driver)
    products = scrape_products(driver)
    save_to_csv(products)
    driver.quit()

if __name__ == "__main__":
    main()