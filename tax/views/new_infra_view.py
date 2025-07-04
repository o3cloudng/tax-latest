from django.shortcuts import render, redirect
from tax.forms import InfrastructureForm, InfrastructureForm2
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from account.models import AdminSetting
from tax.models import InfrastructureType, Waiver, Infrastructure, DemandNotice
from datetime import date, datetime
from django_htmx.http import HttpResponseClientRedirect
from django.db.models import Q, Sum, Count
from core.decorator import tax_payer_only
from agency.models import Agency
from core.services import generate_demand_notice, total_due #, generate_ref_id
from account.models import AdminSetting
import json
from core import settings

from django.db.models import (F, ExpressionWrapper,
                                IntegerField, Value, Case, When)
from django.db.models.functions import Now


@login_required
@tax_payer_only
def new_infrastructure(request):
    form = InfrastructureForm()
    
    # total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost = total_due(request.user.id, False)

    current_year = datetime.now().year

    if Infrastructure.objects\
        .filter(Q(is_existing = False) & Q(processed = False) \
            & Q(company=request.user)).order_by('-created_at').exists():
        infrastructures= Infrastructure.objects\
            .filter(Q(is_existing = False) & Q(processed = False) \
                & Q(company=request.user)).order_by('-created_at')
    else:
        infrastructures = []

    context = {
        'form':form,
        'infra': 'Mast',
        'company': request.user,
        'current_year': current_year,
        'infrastructures': infrastructures,
        # 'subtotal': subtotal,
        'infrastructure': InfrastructureType.objects.all().first(),
        'infra_form': InfrastructureForm(),
        'infra_form2': InfrastructureForm2(),
        # 'referenceid':  "",
        'infra_types': InfrastructureType.objects.all().order_by('pk')

    }
    return render(request, 'tax-payers/apply_for_permit.html', context)

@login_required
def generate_demand_notice(request):
    company = request.user
    if not Infrastructure.objects.select_related('infra_type') \
        .filter(Q(company=company) & Q(processed=False) & Q(created_by=company)).exists():
        messages.error(request, "No infrastructure entered.")
        return redirect('apply_for_permit')
    
    total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra = total_due(company, False)
    # print(f"total_sum = {total_sum} | Sub = {subtotal} | Sum Cost {sum_cost_infrastructure} | Admin = {admin_fees}")
    demand_notice = DemandNotice.objects.create(
        created_by=request.user,
        company=request.user,
        infra = infra,
        subtotal = subtotal,
        total_due = total_sum,
        penalty = 0,
        application_fee = application_cost,
        admin_fee = admin_fees,
        site_assessment = sar_cost,
        amount_due = subtotal + application_cost + admin_fees + sar_cost,
        status="DEMAND NOTICE",
    )
    if demand_notice:
        obj = DemandNotice.objects.get(pk=demand_notice.id)
        infra = Infrastructure.objects.filter(Q(is_existing=False) & Q(processed=False))
        infra.update(processed=True, referenceid=obj.referenceid)
        # infra.save()
        messages.success(request, 'Demand notice created.')
        # return redirect('generate_receipt', ref_id)
        from core.utils import send_email_function
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        # # Send Email here for demand notice
        mail_subject = f"Your Demand Notice Has Been Created Successfully - Ref No: {obj.referenceid}"
        to_email = request.user.email
        
        html_content = render_to_string("Emails/tax_payer/demand_notice.html", {
            "company":request.user,
            "amount_due":obj.total_due,
            "referenceid":obj.referenceid,
            "dn_date": obj.created_at,
            "login":settings.URL,
            })
        text_content = strip_tags(html_content)
        send_email_function(html_content, text_content, to_email, mail_subject)

        agency_email = Agency.objects.all().first().agency_email
        html_content = render_to_string("Emails/admin/new_demand_notice.html", {
            "company":request.user,
            "amount_due":obj.total_due,
            "referenceid":obj.referenceid,
            "dn_date": obj.created_at,
            "login":settings.URL,
            })
        text_content = strip_tags(html_content)
        send_email_function(html_content, text_content, agency_email, "NOTICE: NEW DEMAND NOTICE")
        send_email_function(html_content, text_content, settings.TAX_AUTHOURITY_EMAIL, "NOTICE: NEW DEMAND NOTICE")
        return redirect('generate_receipt', obj.referenceid)
    
    messages.error(request, 'Failed to generate demand notice')
    return redirect('apply_for_permit')

@login_required
def generate_receipt(request, ref_id):

    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)
    # print(type(infra), infra)

    context = {
        # 'infrastructure': infrastructure,
        'ref_id': ref_id,
        'subtotal': demand_notice.subtotal,
        'agency': Agency.objects.all().first(),
        'app_fee': admin_settings.get(slug='application-fee'),
        'total_app_fee': demand_notice.application_fee,
        'admin_pm_fees': demand_notice.admin_fee,
        'admin_pm_fees_sum': demand_notice.admin_fee,
        'site_assessment': demand_notice.site_assessment,
        'total_due': demand_notice.total_due,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
        'infrastructure': infra,
        'total_liability': demand_notice.total_due,
        'site_assessment_cost': demand_notice.site_assessment       
    }
    
    return render(request, 'tax-payers/receipts/demand-notice.html', context)


@login_required
@tax_payer_only
def resources(request):
    context = {}
    return render(request, 'tax-payers/resources.html', context)

@login_required
@tax_payer_only
def upload_existing_facilities(request):
    context = {}
    return render(request, 'tax-payers/upload-existing-facility.html', context)
