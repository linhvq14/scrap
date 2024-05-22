from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

service = Service()
options = webdriver.ChromeOptions()
# your custom options...
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(
    service=service,
    options=options
)
driver.maximize_window()
driver.get('https://www.scoro.com/marketplace/')

web = []
url = driver.find_elements(By.XPATH, "//div[@class='integration-description']")
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
        urls = WebDriverWait(element, 2).until(EC.presence_of_element_located((By.XPATH, 'following-sibling::div/a')))
        read_url = urls.get_attribute("href")
    except TimeoutException:
        read_url = ""
    rank = f"Main-{ranks}"
    ranks += 1
    web.append([names, icon_url, description, read_url, rank, scraping_date])

df = pd.DataFrame(web, columns=['ListingName', 'Icon URL', 'Short Description', 'Read More URL', 'ListingRank',
                                'ListingScrapeDate'])
pd.set_option('display.max_rows', None)
df.to_excel('scoro.xlsx', index=False)
