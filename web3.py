import requests
import re
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import os

def chrome_driver():
    driver_path = ChromeDriverManager().install()
    print("Driver path:", driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    if not os.access(driver_path, os.X_OK):
        print("❌ Not executable. Trying to locate the real binary.")
        for root, dirs, files in os.walk(os.path.dirname(driver_path)):
            for file in files:
                if "chromedriver" in file and not file.endswith(".chromedriver"):
                    potential_path = os.path.join(root, file)
                    print("✅ Found likely candidate:", potential_path)
                    driver_path = potential_path
                    break

    return webdriver.Chrome(service=ChromeService(driver_path), options=options)


driver = chrome_driver()

company_name = []
company_website = []
company_phone = []
company_email = []

url = "https://ukbusinessportal.co.uk/category/renewable-energy/"

res = requests.get(url)
print("status code:", res.status_code)

driver.get(url)
time.sleep(5)

source_code = driver.page_source
soup = BeautifulSoup(source_code, "html.parser")

# 👉 Each business card
cards = soup.select("div.col-span-1.w-full.flex.items-center.shadow-custom")
print("Found cards:", len(cards))

for card in cards:
    # Name (usually inside h3)
    name_tag = card.find("h3")
    name = name_tag.get_text(strip=True) if name_tag else None

    # Website: href starts with https
    website_tag = card.find("a", href=re.compile(r"^https"))
    website = website_tag.get("href") if website_tag else None

    # Phone: href starts with tel:
    phone_tag = card.find("a", href=re.compile(r"^tel:"))
    phone = phone_tag.get("href").replace("tel:", "") if phone_tag else None

    # Email: href starts with mailto:
    email_tag = card.find("a", href=re.compile(r"^mailto:"))
    email = email_tag.get("href").replace("mailto:", "") if email_tag else None

    company_name.append(name)
    company_website.append(website)
    company_phone.append(phone)
    company_email.append(email)

data = {
    "Company Name": company_name,
    "Company Website": company_website,
    "Company Phone": company_phone,
    "Company Email": company_email,
}

df = pd.DataFrame(data)
df.to_csv("renewable_energy_companies.csv", index=False)

print("Data saved to renewable_energy_companies.csv")
print("Rows scraped:", len(df))
