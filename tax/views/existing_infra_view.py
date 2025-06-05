from django.shortcuts import render, redirect
from tax.forms import WaiverForm, RemittanceForm, BulkUploadForm
from django.contrib.auth.decorators import login_required
from account.models import AdminSetting
from tax.models import InfrastructureType, Waiver, Remittance, Infrastructure, DemandNotice
from datetime import date, datetime
from django_htmx.http import HttpResponseClientRedirect
from django.db.models import (F, ExpressionWrapper, Q, Sum, Count, CharField, DecimalField, DateTimeField,
                                IntegerField, Value, Case, When, Func)
from django.db.models.functions import Concat, Cast, Now
from django.contrib import messages
from agency.models import Agency
from core.decorator import tax_payer_only
# from agency.penalty_calculation import penalty_calculation
from core.services import current_year, total_due, penalty_calculation, subtotal_due
from core import settings
import json
from core.utils import send_email_function, taxpayer_notification_email
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from agency.tasks import task_func, send_email_func


@login_required
@tax_payer_only
def apply_for_waver(request):
    if request.method == 'POST':
        if Waiver.objects.filter(Q(company=request.user) & Q(referenceid=request.POST.get('referenceid'))).exists():
            messages.error(request, 'You have already applied for waver.')
            # return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))

        form = WaiverForm(request.POST or None, request.FILES or None)
        
        if form.is_valid():
            wave = form.save(commit=False)
            wave.referenceid = request.POST.get('referenceid')
            wave.company = request.user
            wave.save()

            messages.success(request, 'Your request for waver was sent successfully.')
            return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))
        else:
            messages.error(request, 'Your request for waver failed.')
            return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))
        
    messages.error(request, 'Your request for waver failed.')
    return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))

@login_required
@tax_payer_only
def apply_remittance(request):
    if request.method == 'POST':
        # if Remittance.objects.filter(Q(company=request.user) & Q(referenceid=request.POST.get('referenceid'))).exists():
        #     messages.error(request, 'You have already applied for waver.')
        #     return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))
        
        # if Remittance.objects.filter(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid'))).exists():
        #     remit = Remittance.objects.get(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
        #     form = RemittanceForm(request.POST or None, request.FILES or None, instance=remit)
        #     print("REMIT: = ", remit)
        # else:
        #     form = RemittanceForm(request.POST or None, request.FILES or None)
        rem = DemandNotice.objects.get(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
        if Remittance.objects.filter(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid'))).exists():
            remit = Remittance.objects.get(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
            form = RemittanceForm(request.POST or None, request.FILES or None, instance=remit)
            # print("REMIT: = ", remit)
        else:
            form = RemittanceForm(request.POST or None, request.FILES or None)

        # Check if remittance is more than total due
        tot_due = rem.subtotal + rem.annual_fee + rem.application_fee + \
                    rem.admin_fee + rem.site_assessment

        if int(request.POST.get('remitted_amount')) > int(tot_due):
            # print(f"Real Cost: {tot_due}")
            messages.error(request, 'Please check your remittance value.')
            return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))

        
        if form.is_valid():            
            if not int(request.POST.get('remitted_amount')):
                total_due = rem.subtotal + rem.annual_fee + rem.penalty + rem.application_fee + \
                    rem.admin_fee + rem.site_assessment - int(request.POST.get('remitted_amount'))
            else:
                total_due = rem.subtotal + rem.annual_fee + rem.application_fee + \
                rem.admin_fee + rem.site_assessment - int(request.POST.get('remitted_amount'))
                # print(f"Total Due: {total_due}")

            remit = DemandNotice.objects.filter(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
            # print("TOTAL DUE: ", total_due)
            remit.update(remittance=request.POST.get('remitted_amount'), total_due=total_due)
            
        
            remittance = form.save(commit=False)
            remittance.referenceid = request.POST.get('referenceid')
            remittance.company = request.user
            remittance.apply_for_waver = request.POST.get('apply_for_waver')
            # remittance.receipt = request.POST.get('receipt')
            remittance.save()

            messages.success(request, 'Your remittance was added successfully.')
            return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))
            
      
        messages.error(request, 'Your remittance failed.')
        return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))


def age(the_date):
    date_format = "%m/%d/%Y"

    a = datetime.strptime(the_date, date_format)
    b = datetime.now()

    delta = b - a
    return delta.days


@login_required
@tax_payer_only
def apply_for_existing_permit(request):
    # ref_id = generate_ref_id()
    # EXISITING: APPLY FOR EXISTING PERMIT
    # form = PermitExForm()
    upload_form = BulkUploadForm()
    current_year = []
    for year in range(int(datetime.now().year), 2001, -1):
        current_year.append(year)
        
    infrastructures= Infrastructure.objects\
        .filter(Q(is_existing = True) \
            & Q(company=request.user) & Q(processed=False) & Q(created_by=request.user)) \
            .order_by('-created_at')
        
    context = {
        # 'form':form,
        'infra': 'Mast',
        'referenceid': "",
        'current_year': current_year,
        'company': request.user,
        'infrastructures': infrastructures,
        'infra_types': InfrastructureType.objects.all(),
        'infrastructure': InfrastructureType.objects.all().first(),
        'infra_types': InfrastructureType.objects.all().order_by('pk'),
        'upload_form': upload_form
    }

    return render(request, 'tax-payers/existing_infra_temp/apply_for_exist.html', context)



@login_required
def generate_ex_demand_notice(request):
    # ref_id = generate_ref_id()
    company = request.user
    if not Infrastructure.objects.select_related('infra_type') \
        .filter(Q(company=company) & Q(processed=False) & Q(is_existing=True) & Q(created_by=company)).exists():
        messages.error(request, "No infrastructure entered.")
        return redirect('apply_existing_infra')
    
    total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra = total_due(company, True)
    # print("TOTAL DUES: ", total_sum, sum_cost_infrastructure, application_cost, admin_fees, sar_cost)

    penalty_fee, total_annual_fees = penalty_calculation(request, company)
    penalty = penalty_fee.filter(Q(is_existing=True) & Q(processed=False)).values('penalty_fee').aggregate(penal = Sum('penalty_fee'))
    penalty = int((penalty['penal'] // 10000)) * 10000

    annual_fees = total_annual_fees.filter(Q(is_existing=True) & Q(processed=False)).values('total_annual_fees').aggregate(total = Sum('total_annual_fees'))['total']
    
    # Save to Demand Notice Table
    # referenceid, company, created_by, status (unpaid, disputed, revised, paid, resolved)
    # infrastructure cost, 
    obj, created = DemandNotice.objects.update_or_create(
        referenceid="",
        created_by=request.user,
        company=request.user,
        is_exisiting = True,
        infra = infra,
        subtotal = subtotal,
        amount_due = subtotal + application_cost + admin_fees + sar_cost,
        annual_fee = annual_fees,
        penalty = penalty,
        application_fee = application_cost,
        admin_fee = admin_fees,
        site_assessment = sar_cost,
        total_due = total_sum + penalty + annual_fees,
        status="DEMAND NOTICE",
        defaults={'referenceid': obj.referenceid},
    )
    if obj or created:
        infra = Infrastructure.objects.filter(Q(is_existing=True) & Q(processed=False))
        infra.update(processed=True)
        messages.success(request, 'Demand notice created.')
        
        # Send Email here for demand notice
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
        send_email_function(html_content, text_content, settings.TAX_AUTHOURITY_EMAIL, "NEW DEMAND NOTICE")
        messages.success(request, "Notification sent.")
        print(f"Your email has been sent to {request.user.company_name}")
        return redirect('generate_ex_receipt', obj.referenceid)
    
    messages.error(request, 'Failed to generate demand notice')
    return redirect('apply_existing_infra')


@login_required
def generate_ex_receipt(request, ref_id):
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
        'annual_fees': demand_notice.annual_fee,
        'annual_fee': admin_settings.get(slug='annual-fee').rate,
        'total_due': demand_notice.total_due,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
        'infrastructure': infra,
        'penalty': demand_notice.penalty,
        'total_liability': demand_notice.total_due,
        'site_assessment_cost': demand_notice.site_assessment       
    }
    # Send Email here for demand notice
    # mail_subject = f"Your Demand Notice Has Been Created Successfully - Ref No: {ref_id}"
    # to_email = request.user.email
    
    # html_content = render_to_string("Emails/tax_payer/demand_notice.html", {
    #     "company":request.user,
    #     "amount_due":demand_notice.total_due,
    #     "referenceid":ref_id,
    #     "dn_date": demand_notice.created_at,
    #     "login":settings.URL,
    #     })
    # text_content = strip_tags(html_content)
    # send_email_function(html_content, text_content, to_email, mail_subject)
    # messages.success(request, "Notification sent.")
    # # print(f"Your email has been sent to {request.user.company_name}")
    return render(request, 'tax-payers/receipts/demand-notice-ex-receipt.html', context)


@login_required # Dispute Demand Notice - Issues
@tax_payer_only
def dispute_ex_demand_notice(request, ref_id):
    company = request.user
    remittance = DemandNotice.objects.get(Q(company=company) & Q(referenceid=ref_id))
    if Remittance.objects.filter(Q(company=company) & Q(referenceid=ref_id)).exists():
        remit = Remittance.objects.get(Q(company=company) & Q(referenceid=ref_id))
        form = RemittanceForm(request.POST or None, request.FILES or None, instance=remit)
    else:
        form = RemittanceForm(request.POST or None, request.FILES or None)

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)
    penalty = demand_notice.penalty
    remittance = demand_notice.remittance
    waiver_applied = demand_notice.waiver_applied
    amount_paid = demand_notice.amount_paid
    amount_due = demand_notice.amount_due
    annual_fee = demand_notice.annual_fee
    total_liability = demand_notice.total_due #- demand_notice.penalty

    context = {
        'ref_id': ref_id,
        'demand_notice': demand_notice,
        'penalty': penalty,
        'amount_paid': amount_paid,
        'amount_due': amount_due,
        'annual_fee': annual_fee,
        'remittance': remittance,
        'waiver_applied': waiver_applied,
        'total_liability': total_liability,
        'agency': Agency.objects.all().first(),
        'remittance': remittance,
        'form': form
    }
    return render(request, 'tax-payers/existing_infra_temp/apply_for_ex_permit_edit.html', context)


@login_required
# @tax_payer_only
def undispute_ex_demand_notice_receipt(request, ref_id):
    company = request.user

    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)
    if demand_notice:
        DemandNotice.objects.filter(referenceid=ref_id).update(status="UNDISPUTED UNPAID")

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)
    # print(type(infra), infra)

    context = {
        'infra': infra,
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
        'annual_fee':admin_settings.get(slug='annual-fee').rate,
        'infrastructure': infra,
        'penalty': demand_notice.penalty,
        'remittance': demand_notice.remittance,
        'annual_fees': demand_notice.annual_fee,
        'total_liability': demand_notice.total_due,
        'site_assessment_cost': demand_notice.site_assessment       
    }
    messages.success(request, "Demand notice updated.")
    return render(request, 'tax-payers/receipts/undisputed_ex_dn_receipt.html', context)


@login_required
def resolved_demand_notice_receipt(request, ref_id):

    company = request.user

    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)


    context = {
        'company': request.user,
        'demand_notice': demand_notice,
        'subtotal': demand_notice.subtotal,
        'penalty': demand_notice.penalty,
        'amount_paid': demand_notice.amount_paid,
        'amount_due': demand_notice.amount_due,
        'annual_fee': demand_notice.annual_fee,
        'remittance': demand_notice.remittance,
        'waiver_applied': demand_notice.waiver_applied,
        'total_liability': demand_notice.total_due, #- dn.waiver_applied,
        'agency': Agency.objects.all().first(),
        'remittance': demand_notice.remittance,
        'site_assessment_cost': demand_notice.site_assessment, 
        'infrastructure': infra,     
        
        
        'app_fee': admin_settings.get(slug='application-fee'),
        'total_app_fee': demand_notice.application_fee,
        'admin_pm_fees': demand_notice.admin_fee,
        'admin_pm_fees_sum': demand_notice.admin_fee,
        'site_assessment': demand_notice.site_assessment,
        'total_due': demand_notice.total_due,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
    }
    # all_paid = (demand_notice.amount_due + demand_notice.penalty + demand_notice.annual_fee) \
    #             - (demand_notice.remittance + demand_notice.waiver_applied)
    # if all_paid == 0:
    return render(request, "payments/paid_receipt.html", context)


@login_required
# @tax_payer_only
def revised_demand_notice_receipt(request, ref_id):
    company = request.user
    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)

    context = {
        'company': company,
        'ref_id': ref_id,
        'subtotal': demand_notice.subtotal,
        'agency': Agency.objects.all().first(),
        'app_fee': admin_settings.get(slug='application-fee'),
        'total_app_fee': demand_notice.application_fee,
        'admin_pm_fees': demand_notice.admin_fee,
        'admin_pm_fees_sum': demand_notice.admin_fee,
        'annual_fees': demand_notice.annual_fee,
        'annual_fee': admin_settings.get(slug='annual-fee').rate,
        'amount_due': demand_notice.amount_due + demand_notice.annual_fee,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
        'infrastructure': infra,
        'penalty': demand_notice.penalty,
        'total_liability': demand_notice.total_due,
        'waiver_applied': demand_notice.waiver_applied,
        'site_assessment_cost': demand_notice.site_assessment       
    }
    return render(request, 'tax-payers/receipts/revised_receipt.html', context)


