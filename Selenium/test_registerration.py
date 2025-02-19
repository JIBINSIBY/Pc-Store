from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse

class SignUpTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_signup_form_display(self):
        """Test if signup form elements are displayed"""
        self.browser.get(self.live_server_url + reverse('signup'))
        form_elements = ['email', 'username', 'password', 'cpassword']
        for element in form_elements:
            self.assertTrue(self.browser.find_element(By.ID, element).is_displayed())

    def test_successful_registration(self):
        """Test successful user registration"""
        self.browser.get(self.live_server_url + reverse('signup'))
        
        # Fill form
        form_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Test@123456',
            'cpassword': 'Test@123456'
        }
        
        for field, value in form_data.items():
            self.browser.find_element(By.ID, field).send_keys(value)
        
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for success message or redirect
        WebDriverWait(self.browser, 5).until(
            EC.url_changes(self.live_server_url + reverse('signup'))
        )

    def test_validation_errors(self):
        """Test form validation errors"""
        self.browser.get(self.live_server_url + reverse('signup'))
        
        # Test invalid email
        self.browser.find_element(By.ID, 'email').send_keys('invalid-email')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Wait for error message
        error = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-message'))
        )
        self.assertIn('valid email', error.text.lower())