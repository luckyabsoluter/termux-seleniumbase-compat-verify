from termux_platform_shim import apply_seleniumbase_platform_shim


apply_seleniumbase_platform_shim()

# Import after platform shim so SeleniumBase resolves correctly on Termux.
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
