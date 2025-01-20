from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import json
import pandas as pd
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    # Initialize Chrome driver with proper configuration
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver
def scrape_fields(url, df=None):
    driver = setup_driver()
    driver.get(url)

    # Find all elements with existing headers
    headers = driver.find_elements(By.XPATH, "//h3[contains(@class, 'ribbon blue label')]")
    info_sections = driver.find_elements(By.XPATH, "//div[contains(@class, 'general-information ui relaxed list')]")
    publications = driver.find_elements(By.XPATH, "//div[contains(@class, 'ui feed')]")

    # Extract registration date from history
    history_element = driver.find_element(By.XPATH, "//figure[contains(@class, 'bizq')]")
    data_json = json.loads(history_element.get_attribute('data-data'))
    registration_date = data_json['event'][0]['date'] if data_json.get('event') else ''

    # Get existing header texts
    header_texts = [header.get_attribute('innerText').strip() for header in headers]

    # Prepare data dictionary
    row_dict = {}

    # Match data with corresponding headers
    for header, info_section in zip(headers, info_sections):
        header_text = header.get_attribute('innerText').strip()
        all_divs = info_section.find_elements(By.TAG_NAME, "div")
        content_texts = []
        for div in all_divs:
            div_text = div.get_attribute('innerText').strip()
            if div_text:
                content_texts.append(div_text)
        row_dict[header_text] = ' | '.join(content_texts)

    # Add publications data if 'Publications' header exists
    if 'PUBLICATIONS' in header_texts:
        pub_texts = []
        for pub in publications:
            pub_text = pub.get_attribute('innerText').strip()
            if pub_text:
                pub_texts.append(pub_text)
        row_dict['PUBLICATIONS'] = ' | '.join(pub_texts)

    # Add history data if 'History' header exists
    if 'HISTORY' in header_texts:
        row_dict['HISTORY'] = registration_date

    # Create or append to DataFrame
    if df is None:
        df = pd.DataFrame([row_dict])
    else:
        df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)

    driver.quit()
    print(df)
    return df
    
def get_urls_from_file():
    urls = []
    with open('northdata_results.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('URL:'):
                # Extract URL after the 'URL: ' prefix
                url = line.replace('URL:', '').strip()
                urls.append(url)
    return urls

def main():
    urls = get_urls_from_file()
    df = None

    for url in urls:
        df = scrape_fields(url, df)
        print(f"Processed URL: {url}")

    # Save DataFrame to Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"northdata_scrape_{timestamp}.xlsx"
    print(df)
    df.to_excel(excel_filename, index=False)
    
    print(f"Data saved to {excel_filename}")

if __name__ == "__main__":
    main()
