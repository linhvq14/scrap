import logging
import os
import sys
import time
from datetime import datetime, timezone

from selenium.webdriver.common.by import By
from utilities import scroll_click, open_in_new_window, initialize_driver, replace_non_char_with_hyphen, \
    dump_with_xlsxwriter

web_url = "https://blueshift.com/partners/#integration-partners"
url_prefix = "https://blueshift.com/partners/?_integration_categories="
website_name = "Blueshift"
item_output = []
WAIT_TIME = 2
HEADLESS_MODE = True


def scrape_in_item(driver, ranking, item_name, item_url, cat_name, item_icon):
    open_in_new_window(driver, item_url)
    driver.switch_to.window(driver.window_handles[-1])
    driver.implicitly_wait(0.2)
    item_data = {"ListingScrapeDate": datetime.now(timezone.utc).strftime('%Y-%m-%d'), "ListingSellerName": "",
                 "ListingRank": f"{cat_name} - {ranking + 1}", "Listing URL": item_url, "ListingName": item_name,
                 "Icon URL": item_icon}
    try:
        item_data["Short Description"] = driver.find_element(By.CLASS_NAME, "page-intro").text
    except Exception:
        item_data["Short Description"] = ""
        logging.warning(f"{item_name}: Short Description not found")
    item_data["Category 1"] = ""
    item_data["Category 2"] = ""
    try:
        cat_list = driver.find_elements(By.XPATH, "//ul[@class='post-categories']/li")
        for i in range(len(cat_list)):
            item_data[f"Category {i + 1}"] = cat_list[i].text.strip()
    except Exception:
        logging.warning(f"{item_name}: Categories not found")

    item_data["Visit Website URL"] = ""
    item_data["View documentation URL"] = ""
    try:
        website_external_links = driver.find_elements(By.XPATH, "//div[@class='page-header-cta']/a")
        if len(website_external_links) == 2:
            item_data["Visit Website URL"] = website_external_links[0].get_attribute("href")
            item_data["View documentation URL"] = website_external_links[1].get_attribute("href")
        elif "Documentation" in website_external_links[0].text:
            item_data["View documentation URL"] = website_external_links[0].get_attribute("href")
        else:
            item_data["Visit Website URL"] = website_external_links[0].get_attribute("href")
    except Exception:
        logging.warning(f"{item_name}: Visit Website and Document URL not found")

    time.sleep(1)
    driver.implicitly_wait(WAIT_TIME)
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])
    return item_data


def scrape_in_page(driver, cat_name, base_ranking):
    in_page_output = []
    item_list = driver.find_elements(By.XPATH, "//*[@class='row facetwp-template']/article")
    for i, item in enumerate(item_list):
        try:
            item_entry = item.find_element(By.XPATH, ".//*[@class='entry-title']/a")
            item_url = item_entry.get_attribute("href")
            item_name = item_entry.text
            item_icon = item.find_element(By.TAG_NAME, "img").get_attribute("src")
            result = scrape_in_item(driver, base_ranking + i, item_name, item_url, cat_name, item_icon)
            in_page_output.append(result)
        except Exception:
            logging.error(f"Error in {cat_name} at {base_ranking + i}")
            continue
        time.sleep(2)
    return in_page_output


def scrape_in_category(driver, cat_name):
    link_name = cat_name
    if cat_name == "Chat":
        link_name = "chat-partners-and-integrations"
    cat_url = get_cat_url(link_name)
    open_in_new_window(driver, cat_url)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    in_cat_output = []

    base_ranking = 0
    page_count = 1
    next_button = driver.find_elements(By.XPATH, "//*[@class='facetwp-page next']")
    while len(next_button) > 0 and next_button[0].is_displayed():
        in_page_result = scrape_in_page(driver, cat_name, base_ranking)
        in_cat_output += in_page_result
        scroll_click(driver, next_button[0], 3)
        next_button = driver.find_elements(By.XPATH, "//*[@class='facetwp-page next']")
        base_ranking += len(in_page_result)
        logging.info(f"Scraping {cat_name} on page {page_count}")
        page_count += 1
    in_page_result = scrape_in_page(driver, cat_name, base_ranking)
    in_cat_output += in_page_result
    logging.info(f"{cat_name} done")
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])
    return in_cat_output


def blueshift_scrape(output_dir=None, log_dir=None):
    parent_dir = os.path.abspath("/home/ec2-user/scraping")
    if log_dir is None:
        log_dir = os.path.join(parent_dir, 'log')
    if output_dir is None:
        output_dir = os.path.join(parent_dir, 'output')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    logging.basicConfig(filename=f"{log_dir}/{website_name}.log", level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')
    driver = initialize_driver(wait=WAIT_TIME, headless=HEADLESS_MODE)
    driver.get(web_url)
    global item_output
    time.sleep(2)
    category_list = driver.find_elements(By.CLASS_NAME, "fs-option")
    task_list = []
    for category in category_list:
        cat_text = category.get_attribute("textContent").split("(")[0].strip()
        task_list.append(cat_text)
    try:
        for task in task_list:
            result = scrape_in_category(driver, task)
            item_output += result
            logging.info(f"{task} finished.")
    finally:
        if len(item_output) == 0:
            logging.error("empty data sent to printer")
        else:
            file_path = os.path.join(output_dir, f"{website_name}{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
            dump_with_xlsxwriter(item_output, file_path)


def get_cat_url(cat_name):
    return url_prefix + replace_non_char_with_hyphen(cat_name)


if __name__ == "__main__":
    '''
    sys.argv[1]: output_path
    sys.argv[2]: log_path
    '''
    if len(sys.argv) == 3:
        blueshift_scrape(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        blueshift_scrape(sys.argv[1])
    else:
        blueshift_scrape()
    logging.info("scraping done")
