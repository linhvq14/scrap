from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def initialize_driver(wait, headless):
    """
    Initializes a Selenium WebDriver with specified options.

    Args:
    wait (int): Time in seconds to wait for elements to load.
    headless (bool): Whether to run the browser in headless mode.

    Returns:
    webdriver.Chrome: Configured Chrome WebDriver instance.
    """
    # Configure WebDriver options
    options = Options()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--proxy-server="direct://"')
        options.add_argument('--proxy-bypass-list=*')
        options.add_argument('--start-maximized')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')

    # Initialize WebDriver
    service = Service()  # Make sure the path to your ChromeDriver is correct
    driver = webdriver.Chrome(service=service, options=options)

    # Set implicit wait time
    driver.implicitly_wait(wait)

    # Alternatively, set explicit wait time (if needed)
    wait = WebDriverWait(driver, wait)

    return driver
