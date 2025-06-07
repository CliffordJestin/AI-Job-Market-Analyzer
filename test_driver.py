from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# ✅ Path to your chromedriver
CHROMEDRIVER_PATH = r"D:\webdriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # update this if needed

# ✅ Set options
options = Options()
options.add_argument("--start-maximized")  # open in full screen
options.add_argument("--disable-blink-features=AutomationControlled")  # avoid detection

# ✅ Set up driver
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# ✅ Test: Open a website
driver.get("https://www.naukri.com/data-analyst-jobs")

# ✅ Keep browser open for 10 seconds
time.sleep(10)
driver.quit()
