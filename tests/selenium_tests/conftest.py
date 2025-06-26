import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope='session')
def selenium():
    options = Options()
    options.add_argument('--headless')  # Run tests in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # Disable GPU rendering to avoid EGL errors
    options.add_argument('--window-size=1920,1080')  # Set window size to avoid responsive issues

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()
