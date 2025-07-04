import pytest
from django.contrib.auth.models import User
from django.urls import reverse

@pytest.mark.django_db
def test_user_registration_valid_data(client):
    url = reverse('signup')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'strongpassword123',
        'password2': 'strongpassword123'
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirect after successful registration
    assert User.objects.filter(username='newuser').exists()

@pytest.mark.django_db
def test_user_registration_invalid_data(client):
    url = reverse('signup')
    data = {
        'username': '',
        'email': 'invalidemail',
        'password1': 'pass',
        'password2': 'pass'
    }
    response = client.post(url, data)
    content = response.content.decode()
    assert "This field is required" in content or "Enter a valid email address" in content

@pytest.fixture
def logged_in_user(db, client):
    user = User.objects.create_user(username='existinguser', password='testpassword')
    client.login(username='existinguser', password='testpassword')
    return user

@pytest.mark.django_db
def test_profile_update(logged_in_user, client):
    url = reverse('setup_profile')
    data = {'email': 'updatedemail@example.com'}
    response = client.post(url, data)
    assert "Profile updated successfully" in response.content.decode()
