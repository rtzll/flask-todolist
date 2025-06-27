from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Setup headless browser
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# Ganti dengan URL publik kamu
BASE_URL = "https://legendary-space-rotary-phone-7v74xjvvjxxxfrrq4-5000.app.github.dev"

try:
    # 1. Akses halaman login
    driver.get(f"{BASE_URL}/login")

    # 2. Isi form login
    driver.find_element(By.NAME, "email_or_username").send_keys("user1")
    driver.find_element(By.NAME, "password").send_keys("123456")
    driver.find_element(By.TAG_NAME, "form").submit()

    time.sleep(2)  # tunggu redirect

    # 3. Tambah data (ubah sesuai field/tombol aplikasi kamu)
    driver.get(f"{BASE_URL}/todo/new")  # atau form yang digunakan
    driver.find_element(By.NAME, "title").send_keys("Belajar RPL")
    driver.find_element(By.TAG_NAME, "form").submit()

    time.sleep(1)

    # 4. Logout
    driver.get(f"{BASE_URL}/logout")

    print("✅ Test Passed")
except Exception as e:
    print(f"❌ Test Failed: {e}")
finally:
    driver.quit()
