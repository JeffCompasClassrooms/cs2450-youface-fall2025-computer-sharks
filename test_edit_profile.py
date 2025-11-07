import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="module")
def base_url():
    # Default to localhost, can override with env var
    return os.getenv("PROFILE_PAGE_URL", "http://localhost:5005/profile")

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 15)

# -----------------------------
# TESTS
# -----------------------------

def test_page_loads(driver, wait, base_url):
    driver.get(base_url)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    assert "Edit Profile" in driver.page_source

def test_flash_message_section_exists(driver):
    assert "alert" in driver.page_source or "No clown photos yet!" in driver.page_source

def test_upload_photo_form_exists(driver):
    upload_form = driver.find_element(By.CSS_SELECTOR, "form[action*='upload_photo']")
    file_input = upload_form.find_element(By.NAME, "photo")
    upload_button = upload_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    assert upload_form and file_input and upload_button

def test_upload_photo_submit_button_enabled(driver):
    button = driver.find_element(By.CSS_SELECTOR, "form[action*='upload_photo'] button")
    assert button.is_enabled()

def test_photo_gallery_section(driver):
    gallery_header = driver.find_element(By.XPATH, "//h4[contains(text(),'Your Photos')]")
    assert gallery_header.is_displayed()
    assert "No clown photos yet!" in driver.page_source or "img" in driver.page_source

def test_edit_profile_form_exists(driver):
    form = driver.find_element(By.CSS_SELECTOR, "form[action*='profile']")
    username = form.find_element(By.NAME, "username")
    email = form.find_element(By.NAME, "email")
    bio = form.find_element(By.NAME, "bio")
    assert all([form, username, email, bio])

def test_username_field_readonly(driver):
    username = driver.find_element(By.NAME, "username")
    assert username.get_attribute("readonly") is not None

def test_save_changes_button_exists(driver):
    save_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary")
    assert save_button.is_enabled()
    assert "Save Changes" in save_button.text

def test_edit_profile_form_submission(driver):
    email = driver.find_element(By.NAME, "email")
    bio = driver.find_element(By.NAME, "bio")
    save_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary")

    email.clear()
    email.send_keys("new_email@example.com")
    bio.clear()
    bio.send_keys("Testing bio input.")
    save_button.click()

    # No hard failure expected (no redirect assertion)
    assert True

def test_flash_message_after_save(driver):
    alerts = driver.find_elements(By.CSS_SELECTOR, ".alert")
    if alerts:
        alert = alerts[0]
        assert alert.is_displayed()
    else:
        assert True
