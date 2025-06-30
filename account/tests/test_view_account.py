from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from account.models import Sector, AdminSetting, User
# from account.models import User


class TestDashboard(TestCase):
    def test_dashboard_redirect_error(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, expected_url=f"{reverse('login')}?next={reverse('dashboard')}")

    def test_dashboard_login(self):
        User.objects.create_user(email='test@test.com', username='test', password='#1Million')
        #  Log the user in
        self.client.login(email='test@test.com', password='#1Million')
        response = self.client.get(reverse('dashboard'))


class TestHomePage(TestCase):

    def test_login_page_status_code(self):
        response = self.client.get("/clients")
        self.assertEqual(response.status_code, 301)

    def test_signup_page_status_code(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200) # assertContains includes this
        self.assertTemplateUsed(response, 'tax-payers/signup.html')
        self.assertContains(response, 'Create your account', status_code=200)


class TestSector(TestCase):
    def setUp(self):
        Sector.objects.create(name="Agriculture")
        Sector.objects.create(name="Airline")
        Sector.objects.create(name="Telecom")
        AdminSetting.objects.create(name="Annual-fee", rate="150000")
        AdminSetting.objects.create(name="application-fee", rate="50000")

    def test_sector(self):
        response = Sector.objects.all()
        self.assertEqual(response.count(), 3)
        self.assertEqual(response.first().name, 'Agriculture')
        self.assertEqual(response.last().name, 'Telecom')

    def test_no_sector(self):
        Sector.objects.all().delete()
        response = Sector.objects.all()
        self.assertEqual(response.count(), 0)

    def test_admin_setting(self):
        response = AdminSetting.objects.all()
        self.assertEqual(response.count(), 2)
        self.assertEqual(response.first().name, 'Annual-fee')
        self.assertEqual(response.first().rate, 150000)
        self.assertEqual(response.last().name, 'application-fee')
        self.assertEqual(response.last().rate, 50000)


class TestForm(TestCase):

    def test_signup_form(self):
        form_data = {
            'email': 'test@test.com',
            'phone_number': '08060617790',
            'password1': '#1Million',
            'password2': '#1Million'
        }
        response = self.client.post(reverse('signup'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='test@test.com').exists())

    def test_invalid_signup_form(self):
        form_data = {
            'email': 'test@test.com',
            'phone_number': '08060617790',
            'password1': '#1Million',
            'password2': '#1Million1'
        }
        response = self.client.post(reverse('signup'), data=form_data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(User.objects.filter(email='test@test.com').password1, '#1Million')
        self.assertFalse(User.objects.exists())


class TestForgotPassword(TestCase):
    pass

