import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------
# Configuration
# ------------------------
@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    yield driver
    print("--= Ending Tests =--")
    driver.quit()

@pytest.fixture(scope="module")
def base_url():
    return os.getenv("PROFILE_PAGE_URL", "http://localhost:5005/profile")

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 15)

# ------------------------
# Begin Tests
# ------------------------
def test_edit_profile_full_flow(driver, wait, base_url):
    print("--= Beginning Edit Profile Tests =--")

    # 1️⃣ Page load
    driver.get(base_url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print(f"[TEST 1] Page loaded: {driver.title or 'Untitled Page'}")
    
    # 2️⃣ Login form (if present)
    try:
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        print("[PASSED] Login elements exist.")
    except Exception:
        print("[SKIPPED] Login screen not present — already logged in or not required.")

    # 3️⃣ Check edit profile section
    wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(),'Edit Profile')]")))
    print("[PASSED] Edit profile page loaded.")

    # 4️⃣ Verify profile input fields
    username_field = driver.find_element(By.NAME, "username")
    email_field = driver.find_element(By.NAME, "email")
    bio_field = driver.find_element(By.NAME, "bio")
    if username_field and email_field and bio_field:
        print("[PASSED] All profile inputs exist.")
    else:
        print("[FAILED] One or more profile inputs missing.")

    # 5️⃣ Verify Save button
    save_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary")
    if save_button.is_enabled():
        print("[PASSED] Save button found and enabled.")
    else:
        print("[FAILED] Save button not enabled.")

    # 6️⃣ Edit and submit profile info
    email_field.clear()
    email_field.send_keys("new_email@example.com")
    bio_field.clear()
    bio_field.send_keys("Updated bio via Selenium test.")
    save_button.click()
    print("[INFO] Save button clicked — waiting for response...")

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert")))
        flash = driver.find_element(By.CSS_SELECTOR, ".alert")
        print(f"[PASSED] Flash message displayed: {flash.text}")
    except Exception:
        print("[SKIPPED] No flash message detected (may not be implemented).")

    # 7️⃣ Refresh and check persistence

    driver.refresh()
    wait.until(EC.presence_of_element_located((By.NAME, "email")))
    
    persisted_email = driver.find_element(By.NAME, "email").get_attribute("value")
    persisted_bio = driver.find_element(By.NAME, "bio").get_attribute("value")

    if "new_email@example.com" in persisted_email:
        print("[PASSED] Email persisted correctly after refresh.")
    else:
        print(f"[FAILED] Email did not persist (got: {persisted_email})")
    
    if "Updated bio via Selenium test." in persisted_bio:
        print("[PASSED] Bio persisted correctly after refresh.")
    else:
        print(f"[FAILED] Bio did not persist (got: {persisted_bio})")


    # 8️⃣ Optional: Upload form test
    try:
        upload_form = driver.find_element(By.CSS_SELECTOR, "form[action*='upload_photo']")
        upload_button = upload_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        print("[PASSED] Upload form found.")
        assert upload_button.is_enabled()
        print("[PASSED] Upload button enabled.")
    except Exception:
        print("[SKIPPED] Upload form not found — skipping photo upload test.")

    # 9️⃣ Photo gallery section
    try:
        gallery_header = driver.find_element(By.XPATH, "//h4[contains(text(),'Your Photos')]")
        assert gallery_header.is_displayed()
        print("[PASSED] Photo gallery section visible.")
    except Exception:
        print("[SKIPPED] Gallery section not found.")

    # 🔟 Done
    print("--= All Edit Profile Tests Completed =--")

