from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logging.basicConfig(
    filename="scraping_log.txt", 
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def scrape_with_selenium(search_query, country_code="DE"):
    driver = webdriver.Chrome()
    try:
        logging.info("Starting the web scraping process...")
        logging.info("Opening NorthData website...")
        driver.get("https://www.northdata.com/")
        logging.info("Waiting for the page to load...")
        time.sleep(5)

        try:
            logging.info("Checking for consent dialog...")
            consent_dialog = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cmpboxrecall"))
            )
            logging.info("Consent dialog detected.")
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='cmpboxbtn cmpboxbtnyes cmptxt_btn_yes']"))
            )
            accept_button.click()
            logging.info("Clicked 'Accept all' button.")
        except Exception as e:
            logging.warning(f"Consent dialog did not appear or could not be handled: {e}")

        logging.info("Locating the search box...")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "query"))
        )
        logging.info("Search box located.")
        search_box.clear()
        search_box.send_keys(search_query)
        logging.info(f"Entered search query: {search_query}")

        logging.info("Locating the country dropdown...")
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "ui.inline.multiple.country.dropdown"))
        )
        
        logging.info("Scrolling dropdown into view...")
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        
        logging.info("Clicking the dropdown using JavaScript...")
        driver.execute_script("arguments[0].click();", dropdown)
        logging.info("Opened country dropdown.")

        logging.info(f"Selecting country with code '{country_code}'...")
        country_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@class='item' and @data-value='{country_code}']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", country_item)
        driver.execute_script("arguments[0].click();", country_item)
        logging.info(f"Selected country: {country_code}")

        logging.info("Triggering search...")
        search_box.send_keys(Keys.RETURN)
        logging.info("Search triggered.")

        logging.info("Waiting for search results to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.title"))
        )
        logging.info("Search results loaded.")

        logging.info("Extracting company links...")
        links = driver.find_elements(By.CSS_SELECTOR, "a.title")
        logging.info(f"Number of links found: {len(links)}")

        logging.info("Saving results to 'northdata_results.txt'...")
        with open("northdata_results.txt", "w", encoding="utf-8") as file:
            for index, link in enumerate(links[:20], start=1):
                company_name = link.text
                company_url = link.get_attribute("href")
                logging.debug(f"Company {index}: {company_name}")
                logging.debug(f"URL: {company_url}")
                file.write(f"Company {index}: {company_name}\n")
                file.write(f"URL: {company_url}\n\n")
        logging.info("Results saved successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Closing the browser...")
        driver.quit()
        logging.info("Web scraping process completed.")

scrape_with_selenium("Fitness", "DE")
