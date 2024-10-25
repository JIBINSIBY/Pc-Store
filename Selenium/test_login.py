import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestLogin():
  def setup_method(self, method):
    print("Setting up WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Opens Chrome in maximize mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_experimental_option("detach", True)  # keeps the browser open
    try:
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("WebDriver set up successfully.")
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
    self.vars = {}
  
  def teardown_method(self, method):
    if hasattr(self, 'driver'):
        print("Closing WebDriver...")
        self.driver.quit()
    
  def test_login(self):
    print("Starting test_login...")
    # Test name: Login
    # Step # | name | target | value
    # 1 | open | / | 
    self.driver.get("http://127.0.0.1:8000/")
    print("Navigated to homepage")
    # 2 | setWindowSize | 1552x832 | 
    self.driver.set_window_size(1552, 832)
    # 3 | click | linkText=Login | 
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    print("Clicked Login link")
    # 4 | click | id=email | 
    self.driver.find_element(By.ID, "email").click()
    # 5 | click | linkText=Login | 
    self.driver.find_element(By.LINK_TEXT, "Login").click()
    # 6 | click | id=email | 
    self.driver.find_element(By.ID, "email").click()
    # 7 | type | id=email | jibinsiby12345@gmail.com
    self.driver.find_element(By.ID, "email").send_keys("jibinsiby12345@gmail.com")
    print("Entered email")
    # 8 | click | id=password | 
    self.driver.find_element(By.ID, "password").click()
    # 9 | type | id=password | Qwerty123@
    self.driver.find_element(By.ID, "password").send_keys("Qwerty123@")
    print("Entered password")
    # 10 | click | css=button | 
    self.driver.find_element(By.CSS_SELECTOR, "button").click()
    print("Clicked login button")
    print("Test completed.")

if __name__ == "__main__":
    test = TestLogin()
    test.setup_method(None)
    test.test_login()
    time.sleep(5)  # Keep the browser open for 5 seconds
    test.teardown_method(None)