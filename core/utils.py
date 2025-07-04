from agency.tasks import send_html_email

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from agency.tasks import task_func, send_email_func
# from core.utils import send_email_function



def send_email_function(html_content, text_content, to_email, mail_subject):
    data = {
        "html_content": html_content,
        "email_body": text_content,
        "to_email": to_email,
        "email_subject": mail_subject,
    }
    
    send_html_email.delay_on_commit(data)



def taxpayer_notification_email(company, ref_id, dn_date, login_url, amount_due):
    # Send email to new user company
    mail_subject = f"Demand Notice - {company.company_name}"
    to_email = company.email
    
    html_content = render_to_string("Emails/tax_payer/demand_notice.html", {
        "company":company,
        "dn_date":dn_date,
        "referenceid":ref_id,
        "login":login_url,
        "amount_due":amount_due,
        })
    text_content = strip_tags(html_content)
    send_email_function(html_content, text_content, to_email, mail_subject)