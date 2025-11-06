from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from common.config import settings

def get_driver():
    browser = settings.get("automation.browser", "chrome").lower()
    if browser == "edge":
        opts = EdgeOptions()
        opts.add_argument("--disable-gpu")
        opts.add_argument("--start-maximized")
        return webdriver.Edge(options=opts)
    else:
        opts = ChromeOptions()
        opts.add_argument("--disable-gpu")
        opts.add_argument("--start-maximized")
        return webdriver.Chrome(options=opts)
