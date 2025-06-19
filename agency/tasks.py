from celery import shared_task
from django.core.mail import EmailMultiAlternatives, send_mail
from core import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# from agency.tasks import send_email_function
from account.models import User
from agency.models import Agency
from tax.models import Infrastructure
from django.db.models import Count, Sum, F
# from core.utils import send_email_function
# celery -A core worker -l INFO -P solo # -P solo - For windows
# RUN THIS ON WINDOWS - pip install eventlet
# celery -A core.celeryapp worker --loglevel=info -P eventlet

@shared_task(bind=True)
def task_func(self):
    for i in range(10):
        print(i)
    return "Done"


@shared_task(bind=True)
def send_email_func(self, mail_subject, message, to_email):
    send_mail(
        subject = mail_subject,
        message = message,
        from_email= settings.EMAIL_HOST_USER,
        recipient_list = [to_email],
        fail_silently = True
    )
    return "Done"

@shared_task(bind=True)
def send_html_email(self, data):

    message = EmailMultiAlternatives(
        data["email_subject"], # Email Subject
        data["email_body"], # Email body
        settings.DEFAULT_FROM_EMAIL, # Sender Email Address
        [data["to_email"]] # Receiver Email Address
        )
    html_content = data["html_content"]

    message.attach_alternative(html_content, "text/html")
    message.send()
    return "Done"

@shared_task(bind=True)
def send_annual_tax_emails(self):
    companies = User.objects.filter(is_tax_admin=False)

    agency = Agency.objects.first()
    # print("URL: ", settings.URL)
    for company in companies:
        mail_subject = f"ANNUAL INFRASTRUCTURE TAX"
        to_email = company.email
        infratructure_list = Infrastructure.objects.filter(company=company)
        html_content = render_to_string("Emails/admin/annual_due_email.html", {
            "company_name":company.company_name,
            "agency_email":agency.agency_email,
            "agency_phone":agency.phone_number,
            "infrastructure_list":infratructure_list,
            "infrastructure_annual_tax":"",
            "login":settings.URL,
            })
        text_content = strip_tags(html_content)
        # send_email_function(html_content, text_content, to_email, mail_subject)
        data = {
            "html_content": html_content,
            "email_body": text_content,
            "to_email": to_email,
            "email_subject": mail_subject,
        }
        message = EmailMultiAlternatives(
            data["email_subject"], # Email Subject
            data["email_body"], # Email body
            settings.DEFAULT_FROM_EMAIL, # Sender Email Address
            [data["to_email"]] # Receiver Email Address
            )
        html_content = data["html_content"]

        message.attach_alternative(html_content, "text/html")
        message.send()

    return "Periodic Email Sent."
    # return HttpResponse("Periodic Email Sent.")

@shared_task(bind=True)
def send_annual_tax_emails_to_clients(self):
    company = User.objects.filter(is_tax_admin=False, id=16)
    for comp in company:    
        mail_subject = f"ANNUAL INFRASTRUCTURE TAX"
        results = Infrastructure.objects.filter(company=comp.id).values('infra_type__infra_name')\
            .annotate(
                count=Count('id'),  # Count of each infra_type
                total_rate=Sum(F('infra_type__rate')),  # Sum of rates for each group
                total_cost=Sum(F('infra_type__rate')),  # Same as total_rate in this context
                total_length=Sum(F('length'))  # Same as total_rate in this context
            )\
            .order_by('infra_type__infra_name')  

        overall_cost = 0
        for comp in results:
            if ( 'optic' in str(comp['infra_type__infra_name']).lower()) or ('line' in str(comp['infra_type__infra_name']).lower()):
                total_cost = comp['total_length'] * comp['total_cost']
                overall_cost += total_cost
            else:
                total_cost = comp['total_cost']
                overall_cost += total_cost
                
            # print(f"Infra Type: {comp['infra_type__infra_name']} ({comp['total_length']})\
            #         | Count: {comp['count'] } | Sum: {comp['total_cost']} | Total: {total_cost}")
            # print(f"Infra Type: {comp['infra_type']} | Count: {comp.count} | Sum: {comp.total_cost}")

        # CREATE DEMAND NOTICE FOR EACH TASK PAYER

        html_content = render_to_string("Emails/admin/annual_due_email.html", {
            "company_name":comp.company_name,
            "results": results,
            "overall_cost": overall_cost,
            "login":settings.URL,
            })
        text_content = strip_tags(html_content)
        # send_email_function(html_content, text_content, to_email, mail_subject)
        data = {
            "html_content": html_content,
            "email_body": text_content,
            "to_email": comp.email,
            "email_subject": mail_subject,
        }
        message = EmailMultiAlternatives(
            data["email_subject"], # Email Subject
            data["email_body"], # Email body
            settings.DEFAULT_FROM_EMAIL, # Sender Email Address
            [data["to_email"]] # Receiver Email Address
            )
        html_content = data["html_content"]

        message.attach_alternative(html_content, "text/html")
        message.send()

        print(f"OVERALL TOTAL COST: {overall_cost}")

