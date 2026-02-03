from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 👇 change path if different 
service = Service(r"C:\Users\hp\Downloads\task\chromedriver.exe")

options = Options()
options.add_argument("--headless")  # don't open browser window

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.gsmarena.com/samsung-phones-9.php")

print("✅ Page title:", driver.title)
driver.quit()

