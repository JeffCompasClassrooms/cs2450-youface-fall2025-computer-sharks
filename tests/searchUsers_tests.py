from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Don't specify chromedriver path!
driver = webdriver.Chrome(options=options)

try:
    driver.get("http://127.0.0.1:5005")
    time.sleep(2)

    print("--= Beginning Tests =--")
    searchTextBox = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    searchButton = driver.find_element(By.CSS_SELECTOR, "input[type='submit']") 


    #copy = driver.find_element(By.CSS_SELECTOR, "p[class='lead']").text

    #if copy == "A billion dollars and it's yours!":
     #   print("[FAILED] - Default Copy is still in place.")
    #else:
    #    print("[PASSED] - Default Copy has been changed.")

    if searchButton:
        print("[PASSED] - Search Button Exists.")
    else:
        print("[FAILED] - Search button not found.")
    if searchTextBox:
        print("[PASSED] - Search Box Exists.")
    else:
        print("[FAILED] - Search Box not found.")
    try:
        searchButton.click()
        print("[PASSED] - Search button is clickable.")
    except Exception:
        print("[FAILED] - Search button not clickable.")
    
    time.sleep(1)
    searchTextBox = driver.find_element(By.NAME, "searchName")
    placeholder = searchTextBox.get_attribute("placeholder")

    if placeholder and placeholder.lower() == "username":
        print(f"[PASSED] - Placeholder text found: '{placeholder}'")
    else:
        print("[FAILED] - No placeholder text in search box.")

except Exception as e:
    print("Error:", e)

finally:
    print("--= Ending Tests =--")
    driver.quit()
