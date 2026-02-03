from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

# --- Setup your ChromeDriver path --- 
service = Service(r"C:\Users\hp\Downloads\task\chromedriver.exe") 
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)

# --- Step 1: Open Samsung phones list page ---
base_url = "https://www.gsmarena.com/samsung-phones-9.php"
driver.get(base_url)
time.sleep(2)

# --- Step 2: Find phone links ---
links = []
phones = driver.find_elements(By.CSS_SELECTOR, "div.makers a")

for phone in phones[:30]:  # limit to 30 phones
    links.append(phone.get_attribute("href"))

print(f"✅ Found {len(links)} Samsung phone links")

# --- Step 3: Visit each phone page ---
data = []

for link in links:
    driver.get(link)
    time.sleep(1)

    try:
        name = driver.find_element(By.CSS_SELECTOR, "h1.specs-phone-name-title").text
    except:
        name = "N/A"

    specs = {"Model": name, "URL": link}

    # --- Try to extract some key specs ---
    for spec_name in ["Launch", "Display", "Camera", "Memory", "Battery"]:
        try:
            section = driver.find_element(By.XPATH, f"//table[contains(., '{spec_name}')]").text
            specs[spec_name] = section
        except:
            specs[spec_name] = "N/A"

    data.append(specs)
    print(f"Scraped: {name}")

# --- Step 4: Save results ---
df = pd.DataFrame(data)
df.to_csv("samsung_phones.csv", index=False, encoding="utf-8")
print("\n✅ Scraped", len(df), "phones successfully and saved to samsung_phones.csv")

driver.quit()

