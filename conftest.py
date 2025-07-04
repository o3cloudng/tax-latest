import pytest
from account.models import User
from tax.models import Infrastructure, DemandNotice, InfrastructureType
from agency.models import Agency
from core import settings
import tax.views.new_infra_view

@pytest.fixture(autouse=True)
def enable_test_email_and_celery(settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True



@pytest.fixture
def test_user(db):
    """Create a custom user using email login."""
    return User.objects.create_user(
        email='testuser@example.com',
        username='testuser',
        phone_number='09060617790',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(client, test_user):
    """Log in user using email and password."""
    # url = reverse('generate_demand_notice')
    
    client.login(email='testuser@example.com', password='testpass123')
    return client

@pytest.fixture
def infrastructure_type(test_user):
    """Creates unprocessed infrastructure."""
    return InfrastructureType.objects.create(
        infra_name = "Mast 1-50",
        rate = 1500
    )

@pytest.fixture
def infrastructure(test_user, infrastructure_type):
    """Creates unprocessed infrastructure."""
    return Infrastructure.objects.create(
        company=test_user,
        length=1000,
        infra_type=infrastructure_type,
        processed=False,
        created_by=test_user,
        is_existing=False
    )

@pytest.fixture
def demand_notice(test_user, infrastructure_type):
    """Creates Demand Notice."""
    subtotal = 100000
    application_cost = 150000
    admin_fees = 15 * subtotal / 100 # 15,000
    sar_cost = 100000
    penalty = 0
    return DemandNotice.objects.create(
        created_by=test_user,
        company=test_user,
        infra = infrastructure_type,
        subtotal = subtotal,
        total_due = subtotal + application_cost + admin_fees + sar_cost,
        penalty = penalty,
        application_fee = application_cost,
        admin_fee = admin_fees,
        site_assessment = sar_cost,
        amount_due = subtotal + application_cost + admin_fees + sar_cost + penalty, # 365,000
        status="DEMAND NOTICE",
    )

@pytest.fixture
def agency():
    """Creates agency for admin email notification."""
    return Agency.objects.create(
        agency_name="Local Dev Agency",
        agency_email="agency@example.com",
        phone_number='09060617790',
        address='Alausa Ikeja, Lagos',
    )
