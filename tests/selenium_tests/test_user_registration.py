import pytest
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from django.urls import reverse

@pytest.mark.django_db
def test_user_registration_valid_data(live_server, selenium):
    selenium.get(f"{live_server.url}{reverse('signup')}")
    username_input = selenium.find_element(By.NAME, "username")
    email_input = selenium.find_element(By.NAME, "email")
    password1_input = selenium.find_element(By.NAME, "password1")
    password2_input = selenium.find_element(By.NAME, "password2")
    submit_button = selenium.find_element(By.XPATH, "//button[@type='submit']")

    username_input.send_keys("newuser")
    email_input.send_keys("newuser@example.com")
    password1_input.send_keys("strongpassword123")
    password2_input.send_keys("strongpassword123")
    submit_button.click()

    assert "Registration successful" in selenium.page_source

@pytest.mark.django_db
def test_user_registration_invalid_data(live_server, selenium):
    selenium.get(f"{live_server.url}{reverse('signup')}")
    username_input = selenium.find_element(By.NAME, "username")
    email_input = selenium.find_element(By.NAME, "email")
    password1_input = selenium.find_element(By.NAME, "password1")
    password2_input = selenium.find_element(By.NAME, "password2")
    submit_button = selenium.find_element(By.XPATH, "//button[@type='submit']")

    username_input.send_keys("")  # Empty username
    email_input.send_keys("invalidemail")  # Invalid email
    password1_input.send_keys("pass")
    password2_input.send_keys("pass")
    submit_button.click()

    assert "This field is required" in selenium.page_source or "Enter a valid email address" in selenium.page_source

@pytest.fixture
def logged_in_user(db, live_server, selenium):
    user = User.objects.create_user(username='existinguser', password='testpassword')
    selenium.get(f"{live_server.url}{reverse('login')}")
    selenium.find_element(By.NAME, "username").send_keys("existinguser")
    selenium.find_element(By.NAME, "password").send_keys("testpassword")
    selenium.find_element(By.XPATH, "//button[@type='submit']").click()
    return user

@pytest.mark.django_db
def test_profile_update(logged_in_user, live_server, selenium):
    selenium.get(f"{live_server.url}{reverse('setup_profile')}")
    email_input = selenium.find_element(By.NAME, "email")
    submit_button = selenium.find_element(By.XPATH, "//button[@type='submit']")

    email_input.clear()
    email_input.send_keys("updatedemail@example.com")
    submit_button.click()

    assert "Profile updated successfully" in selenium.page_source
