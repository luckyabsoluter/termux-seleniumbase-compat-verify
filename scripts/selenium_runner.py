from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def run_selenium_check(chromium_path, chromedriver_path):
    driver = None
    try:
        options = Options()
        options.binary_location = chromium_path
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(executable_path=chromedriver_path)
        driver = Chrome(service=service, options=options)
        driver.get("https://github.com/")
        print(f"Selenium loaded title: {driver.title}")
    finally:
        if driver is not None:
            driver.quit()
