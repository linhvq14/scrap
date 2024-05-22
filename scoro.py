import os
from datetime import datetime

import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilities import initialize_driver

WAIT_TIME = 0
HEADLESS_MODE = True
driver = initialize_driver(wait=WAIT_TIME, headless=HEADLESS_MODE)
driver.get('https://www.scoro.com/marketplace/')
website_name = "Scoro"


def scoro_scrape():
    web = []
    name_element = driver.find_elements(By.XPATH, '//div[@class="integration-description"]/h3')
    icon_element = driver.find_elements(By.XPATH, '//div[@class="integration-inner"]/img')
    description_elem = driver.find_elements(By.XPATH, '//div[@class="integration-description"]/p')
    url = driver.find_elements(By.XPATH, "//div[@class='integration-description']")
    ranks = 1
    for name, icon, descriptions, element in zip(name_element, icon_element, description_elem, url):
        scraping_date = datetime.now().strftime("%Y-%m-%d")
        names = name.text
        print(name)
        description = descriptions.text
        icon_url = icon.get_attribute("src")
        try:
            urls = WebDriverWait(element, 2).until(
                EC.presence_of_element_located((By.XPATH, 'following-sibling::div/a')))
            read_url = urls.get_attribute("href")
        except TimeoutException:
            read_url = ""
        rank = f"Main-{ranks}"
        ranks += 1
        web.append([names, icon_url, description, read_url, rank, scraping_date])

    df = pd.DataFrame(web, columns=['ListingName', 'Icon URL', 'Short Description', 'Read More URL', 'ListingRank',
                                    'ListingScrapeDate'])
    return df


def get_file_path(output_dir=None, log_dir=None):
    # Get the absolute path of the current Python script
    current_file_path = os.path.abspath(__file__)

    # Get the parent directory of the current file
    parent_dir = os.path.dirname(current_file_path)

    if output_dir is None:
        output_dir = os.path.join(parent_dir, 'output')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


if __name__ == "__main__":
    file_path = os.path.join(get_file_path(), f"{website_name}{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
    df = scoro_scrape()
    pd.set_option('display.max_rows', None)
    df.to_excel(file_path, index=False)
