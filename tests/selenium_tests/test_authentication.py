import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
from django.urls import reverse

@pytest.fixture
def create_user(db):
    user = User.objects.create_user(username='testuser', email='test@admin.com', password='testpassword')
    return user

@pytest.mark.django_db
def test_login_valid_user(live_server, selenium, create_user):
    selenium.get(f"{live_server.url}{reverse('login')}")
    username_input = selenium.find_element(By.NAME, "username")
    email_input = selenium.find_element(By.NAME, "email")
    password_input = selenium.find_element(By.NAME, "password")
    submit_button = selenium.find_element(By.XPATH, "//button[@type='submit']")

    username_input.send_keys("testuser")
    email_input.send_keys("email")
    password_input.send_keys("testpassword")
    submit_button.click()

    assert "Dashboard" in selenium.page_source

@pytest.mark.django_db
def test_login_invalid_user(live_server, selenium):
    selenium.get(f"{live_server.url}{reverse('login')}")
    username_input = selenium.find_element(By.NAME, "username")
    email_input = selenium.find_element(By.NAME, "email")
    password_input = selenium.find_element(By.NAME, "password")
    submit_button = selenium.find_element(By.XPATH, "//button[@type='submit']")

    username_input.send_keys("invaliduser")
    email_input.send_keys("Invalidemail")
    password_input.send_keys("wrongpassword")
    submit_button.click()

    assert "Invalid credentials" in selenium.page_source
