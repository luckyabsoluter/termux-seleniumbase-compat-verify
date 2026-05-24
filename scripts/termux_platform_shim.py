import os
import sys


def apply_seleniumbase_platform_shim():
    if sys.platform != "android":
        return

    if os.environ.get("TERMUX_DISABLE_SELENIUMBASE_PLATFORM_SHIM") == "1":
        return

    print("Android platform detected. Reporting platform as 'linux' for SeleniumBase import compatibility.")
    sys.platform = "linux"
