from django.test import TestCase, RequestFactory
# from django.contrib.auth.models import User
from account.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, date
from tax.models import DemandNotice, Infrastructure
from agency.models import Agency
from django.core import mail
from core import settings

class DemandNoticeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.demand_notice = DemandNotice.objects.create(
            company=self.user,
            infra="Test Infrastructure",
            subtotal=1000,
            penalty=200,
            application_fee=50,
            admin_fee=30,
            site_assessment=20,
            remittance=0,
            waiver_applied=0,
            annual_fee=100,
            created_by="Test Creator"
        )
        self.client.login(email='test@example.com', password='testpass123')

    def test_demand_notice_creation(self):
        """Test that a demand notice can be created"""
        self.assertEqual(self.demand_notice.company, self.user)
        self.assertEqual(self.demand_notice.infra, "Test Infrastructure")
        self.assertEqual(self.demand_notice.subtotal, 1000)
        self.assertEqual(self.demand_notice.status, "DEMAND NOTICE")

    def test_calculated_total_due(self):
        """Test the total due calculation"""
        expected_total = (1000 + 200 + 50 + 30 + 20 + 100 - 0 - 0)
        self.assertEqual(self.demand_notice.calculated_total_due(), expected_total)
        self.assertEqual(self.demand_notice.total_due, expected_total)

    def test_save_method_updates_total_due(self):
        """Test that save method updates total_due"""
        original_total = self.demand_notice.total_due
        self.demand_notice.remittance = 100
        self.demand_notice.save()
        self.assertNotEqual(self.demand_notice.total_due, original_total)
        self.assertEqual(self.demand_notice.total_due, original_total - 100)

    def test_referenceid_generation(self):
        """Test that referenceid is generated after save"""
        new_notice = DemandNotice.objects.create(
            company=self.user,
            infra="New Infrastructure",
            subtotal=500,
            created_by="Test Creator"
        )
        self.assertIsNotNone(new_notice.referenceid)
        self.assertTrue(new_notice.referenceid.startswith("LA"))

    def test_referenceid_format(self):
        """Test the format of the generated referenceid"""
        today = date.today()
        year = str(today.year)[-2:]
        month = str(today.month).zfill(2)
        
        new_notice = DemandNotice.objects.create(
            company=self.user,
            infra="New Infrastructure",
            subtotal=500,
            created_by="Test Creator"
        )
        
        # Check the format: LA + year + month + 8-digit sequence
        self.assertRegex(new_notice.referenceid, r'^LA\d{2}\d{2}\d{8}$')

    def test_status_choices(self):
        """Test that status field has correct choices"""
        field = DemandNotice._meta.get_field('status')
        self.assertEqual(field.choices, DemandNotice.PAY_CHOICES)


class GenerateDemandNoticeViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.agency = Agency.objects.create(
            agency_name="Test Agency",
            agency_email="agency@example.com"
        )
        # Create test infrastructure
        self.infra = Infrastructure.objects.create(
            company=self.user,
            processed=False,
            created_by=self.user,
            # Add other required fields for Infrastructure
        )
        self.client.login(email='test@example.com', password='testpass123')

    def test_generate_demand_notice_redirects_with_no_infra(self):
        """Test redirect when no infrastructure exists"""
        # Delete the test infrastructure first
        Infrastructure.objects.all().delete()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('generate_demand_notice'))
        
        self.assertRedirects(response, reverse('apply_for_permit'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "No infrastructure entered.")

    def test_generate_demand_notice_creates_record(self):
        """Test successful demand notice creation"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('generate_demand_notice'))
        
        # Check if demand notice was created
        self.assertEqual(DemandNotice.objects.count(), 1)
        notice = DemandNotice.objects.first()
        
        # Verify redirect to generate_receipt
        self.assertRedirects(response, reverse('generate_receipt', args=[notice.referenceid]))
        
        # Check messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Demand notice created.')

    def test_infrastructure_processed_flag(self):
        """Test that infrastructure processed flag is updated"""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(reverse('generate_demand_notice'))
        
        # Refresh infrastructure from db
        infra = Infrastructure.objects.get(pk=self.infra.pk)
        self.assertTrue(infra.processed)
        self.assertEqual(infra.referenceid, DemandNotice.objects.first().referenceid)

    def test_email_sent_to_user(self):
        """Test that email is sent to the user"""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(reverse('generate_demand_notice'))
        
        # Check that two emails were sent (one to user, one to agency)
        self.assertEqual(len(mail.outbox), 2)
        
        # Verify user email
        user_email = mail.outbox[0]
        self.assertEqual(user_email.to, [self.user.email])
        self.assertIn("Your Demand Notice Has Been Created Successfully", user_email.subject)

    def test_email_sent_to_agency(self):
        """Test that email is sent to the agency"""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(reverse('generate_demand_notice'))
        
        # Verify agency email
        agency_email = mail.outbox[1]
        self.assertEqual(agency_email.to, [self.agency.agency_email, settings.TAX_AUTHOURITY_EMAIL])
        self.assertIn("NOTICE: NEW DEMAND NOTICE", agency_email.subject)

    def test_authentication_required(self):
        """Test that view requires login"""
        response = self.client.get(reverse('generate_demand_notice'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('generate_demand_notice')}")