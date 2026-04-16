import sys


if sys.platform == "android":
    print("Android platform detected. Changing platform to 'linux' for SeleniumBase compatibility.")
    sys.platform = "linux"

# Import after platform adjustment so SeleniumBase resolves correctly on Termux.
from seleniumbase import Driver


def run_seleniumbase_check(chromium_path):
    driver = None
    try:
        driver = Driver(
            browser="chrome",
            uc=True,  # If uc=False, SeleniumBase doesn't use chromedriver correctly
            headless=True,
            binary_location=chromium_path,
        )
        driver.get("https://github.com/")
        print(f"SeleniumBase loaded title: {driver.title}")
    finally:
        if driver is not None:
            driver.quit()
