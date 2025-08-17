from django.shortcuts import render, redirect
from tax.forms import InfrastructureForm, InfrastructureForm2
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tax.models import InfrastructureType, Waiver, Infrastructure, DemandNotice, Remittance
from datetime import date, datetime
from django_htmx.http import HttpResponseClientRedirect
from django.db.models import Q, Sum, Count
from core.decorator import tax_payer_only
from agency.models import Agency
from core.services import generate_demand_notice, total_due, agency_total_due, agency_penalty_calculation
from account.models import AdminSetting, User
import json
# from agency.penalty_calculation import penalty_calculation
from agency.forms import WaiverForm
# EMAIL
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.utils import send_email_function
from core import settings 
from core.services import send_demand_notice_email


@login_required
def agency_process_infrastructure(request, pk):
    company = User.objects.get(pk=pk)
    agency = request.user

    infrastructures = Infrastructure.objects.filter(Q(company=company) & Q(processed=False) & Q(created_by=agency))
    infrastructures.update(processed=True, updated_at=datetime.now())
    return redirect('agency_add_infrastructure', company.id)

@login_required
def agency_generate_demand_notice(request, pk):
    # GENERATE DEMAND NOTICE FOR NEW INFRASTRUCTURES
    # ref_id = generate_ref_id()
    company = User.objects.get(pk=pk)
    agency = request.user

    if not Infrastructure.objects.select_related('infra_type') \
        .filter(Q(company=company) & Q(is_existing=False) & \
                Q(processed=False) & Q(created_by=agency)).exists():
         messages.error(request, "No infrastructure")
         return redirect('agency_add_infrastructure', company.id)
    
    total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra = agency_total_due(company, False, agency)
    
    annual_fees = AdminSetting.objects.get(slug="annual-fee").rate

    try: 
        demand_notice = DemandNotice.objects.create(
            created_by=request.user,
            company=company,
            is_exisiting = True,
            infra = infra,
            subtotal = subtotal,
            amount_due = subtotal + application_cost + admin_fees + sar_cost,
            annual_fee = annual_fees,
            penalty = 0,
            application_fee = application_cost,
            admin_fee = admin_fees,
            site_assessment = sar_cost,
            total_due = total_sum + annual_fees,
            status="DEMAND NOTICE"
        )

        if demand_notice:
            obj = DemandNotice.objects.get(id=demand_notice.id)
            # Mark infrastructure as processed
            infra = Infrastructure.objects.filter(Q(processed=False))
            infra.update(processed=True)
                # Send Email here for demand notice
            mail_subject = f"Your Demand Notice Has Been Created Successfully - Ref No: {obj.referenceid}"
            to_email = company.email
            
            html_content = render_to_string("Emails/tax_payer/demand_notice.html", {
                "company":request.user,
                "amount_due":obj.total_due,
                "referenceid":obj.referenceid,
                "dn_date": obj.created_at,
                "login":settings.URL,
                })
            text_content = strip_tags(html_content)
            # Email User
            send_email_function(html_content, text_content, to_email, mail_subject) 
            # Email Agent
            send_email_function(html_content, text_content, settings.TAX_AUTHOURITY_EMAIL, "NOTICE: NEW DEMAND NOTICE")
            send_email_function(html_content, text_content, agency.email, "NOTICE: NEW DEMAND NOTICE")
            messages.success(request, 'Demand notice created.')
            # messages.success(request, "Notification sent.")
            return redirect('agency_generate_receipt', obj.referenceid)
        
        messages.error(request, 'Failed to generate demand notice')
        return redirect('agency_add_infrastructure', company.id)
                 

    except Exception as e:
        messages.error(request, 'Failed to generate demand notice')
        return redirect('agency_add_infrastructure', company.id)




    # obj, created = DemandNotice.objects.update_or_create(
    #     # referenceid=ref_id,
    #     created_by=agency,
    #     company=company,
    #     infra = infra,
    #     subtotal = subtotal,
    #     total_due = total_sum,
    #     penalty = 0,
    #     application_fee = application_cost,
    #     admin_fee = admin_fees,
    #     site_assessment = sar_cost,
    #     amount_due = subtotal + application_cost + admin_fees + sar_cost,
    #     status="DEMAND NOTICE",
    #     defaults={'referenceid': ref_id},
    # )
    # if obj or created:
    #     infra = Infrastructure.objects.filter(Q(is_existing=False) & Q(processed=False))
    #     infra.update(processed=True, referenceid=ref_id, updated_at=datetime.now())
    #     # infra.save()
    #     messages.success(request, 'Demand notice created.')
    #     return redirect('agency_generate_receipt', ref_id)
    
    # messages.error(request, 'Failed to generate demand notice')
    # return redirect('apply_for_permit')

@login_required
def agency_generate_receipt(request, ref_id):

    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)
    # company = demand_notice.company.company_name

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)

    context = {
        # 'infrastructure': infrastructure,
        'ref_id': ref_id,
        'company': demand_notice.company,
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
    # messages.success(request, "Demand notice generated.")
    
    return render(request, 'agency/receipts/demand-notice.html', context)


# ##############################################################
# EXISITING INFRASTRUCTURES


@login_required
def apply_for_existing_permit(request, pk):
    # EXISTING: APPLY FOR EXISTING PERMIT
    company = User.objects.get(pk=pk)
    agency = request.user
    # ref_id = generate_ref_id()
    current_year = []
    for year in range(int(datetime.now().year), 2001, -1): 
        current_year.append(year)
        
    infrastructures= Infrastructure.objects\
        .filter(Q(is_existing = True) & Q(created_by=agency) \
            & Q(company=company) & Q(processed=False)) \
            .order_by('-created_at')
        
    context = {
        'infra': 'Mast',
        # 'referenceid': ref_id,
        'current_year': current_year,
        'company': company,
        'userid': company.id,
        'infrastructures': infrastructures,
        'infra_types': InfrastructureType.objects.all(),
        'infrastructure': InfrastructureType.objects.all().first(),
        'infra_types': InfrastructureType.objects.all().order_by('pk'),
    }

    return render(request, 'agency/pages/forms/apply_for_exist.html', context)

# @admin_only
@login_required
def generate_ex_demand_notice(request):
    company = User.objects.get(pk=request.POST.get("company"))
    agency = request.user
    # ref_id = request.POST.get("referenceid")
    
    total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra = agency_total_due(company, True, agency)

    penalty_fee, total_annual_fees = agency_penalty_calculation(request, company)
    penalty = penalty_fee
    annual_fees = total_annual_fees

    messages.error(request, 'No infrastructure')
    if not (total_sum or infra or subtotal or application_cost or admin_fees or sar_cost):
        messages.error(request, 'No infrastructure')
        return redirect('agency_apply_for_exist', company.id)

    try: 
        demand_notice = DemandNotice.objects.create(
        created_by=request.user,
        company=company,
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
        status="DEMAND NOTICE"
        )

        if demand_notice:
            obj = DemandNotice.objects.get(id=demand_notice.id)
            # Mark infrastructure as processed
            infra = Infrastructure.objects.filter(Q(is_existing=True) & Q(processed=False))
            infra.update(processed=True)
                # Send Email here for demand notice
            mail_subject = f"Your Demand Notice Has Been Created Successfully - Ref No: {obj.referenceid}"
            # to_email = request.user.email
            to_email = company.email
            
            html_content = render_to_string("Emails/tax_payer/demand_notice.html", {
                "company":company,
                "amount_due":obj.total_due,
                "referenceid":obj.referenceid,
                "dn_date": obj.created_at,
                "login":settings.URL,
                })
            text_content = strip_tags(html_content)
            # Email User
            send_email_function(html_content, text_content, to_email, mail_subject) 
            # Email Agent
            html_content = render_to_string("Emails/admin/new_demand_notice.html", {
                "company":company,
                "amount_due":obj.total_due,
                "referenceid":obj.referenceid,
                "dn_date": obj.created_at,
                "login":settings.URL,
                })
            text_content = strip_tags(html_content)
            send_email_function(html_content, text_content, settings.TAX_AUTHOURITY_EMAIL, "NOTICE: NEW DEMAND NOTICE")
            send_email_function(html_content, text_content, request.user.email, "NOTICE: NEW DEMAND NOTICE")
            messages.success(request, 'Demand notice created.')
            return redirect('agency_generate_ex_receipt', obj.referenceid)
                

    except Exception as e:
        messages.error(request, 'Failed to generate demand notice')
        return redirect('agency_apply_for_exist', company.id)
    
    # obj, created = DemandNotice.objects.update_or_create(
    #     referenceid=ref_id,
    #     created_by=request.user,
    #     company=company,
    #     is_exisiting = True,
    #     infra = infra,
    #     subtotal = subtotal,
    #     amount_due = subtotal + application_cost + admin_fees + sar_cost,
    #     annual_fee = annual_fees,
    #     penalty = penalty,
    #     application_fee = application_cost,
    #     admin_fee = admin_fees,
    #     site_assessment = sar_cost,
    #     total_due = total_sum + penalty + annual_fees,
    #     status="DEMAND NOTICE",
    #     defaults={'referenceid': ref_id},
    # )
    # if obj or created:
    #     infra = Infrastructure.objects.filter(Q(is_existing=True) & Q(processed=False))
    #     infra.update(processed=True, referenceid=ref_id, updated_at=datetime.now())
    #     messages.success(request, 'Demand notice created.')
    #     # return redirect('agency_generate_ex_receipt')
    #     return redirect('agency_generate_ex_receipt', ref_id)
    
    # messages.error(request, 'Failed to generate demand notice')
    # return redirect('agency_apply_for_exist', company.id)


@login_required
def agency_generate_ex_receipt(request, ref_id):
    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)

    context = {
        # 'infrastructure': infrastructure,
        'ref_id': ref_id,
        'company': demand_notice.company,
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
    messages.success(request, "Demand notice receipt generated")
    return render(request, 'agency/receipts/demand-notice-ex-receipt.html', context)


@login_required
# @tax_payer_only
def undispute_ex_demand_notice_receipt(request, ref_id):
    company = request.user

    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)
    if demand_notice:
        DemandNotice.objects.filter(referenceid=ref_id)\
            .update(status="UNDISPUTED UNPAID", updated_at=datetime.now())

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)

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
    return render(request, 'tax-payers/receipts/undisputed_ex_dn_receipt.html', context)


@login_required
def agency_apply_waiver(request):
    if request.method == 'POST':
        pass
   
    return "DONE"


@login_required # Dispute Demand Notice - Issues
def agency_waiver(request, ref_id):
    demand_notice = DemandNotice.objects.filter(referenceid=ref_id)
    if request.method == 'POST':
        company = User.objects.get(pk=request.POST['company'])
        ref_id = request.POST['referenceid']
        waiver_applied = request.POST['waiver_applied']

        form = WaiverForm(request.POST or None, request.FILES or None)
        
        dn = demand_notice.get(Q(referenceid = ref_id))
        if form.is_valid():
            if not int(request.POST['waiver_applied']):
                total_due = dn.subtotal + dn.annual_fee + dn.penalty + dn.application_fee + \
                    dn.admin_fee + dn.site_assessment - (dn.remittance + dn.amount_paid + int(request.POST.get('waiver_applied')))
            else:
                total_due = dn.subtotal + dn.annual_fee + dn.penalty + dn.application_fee + \
                dn.admin_fee + dn.site_assessment - (dn.remittance + dn.amount_paid + int(request.POST.get('waiver_applied')))
            
            demand_notice.update(waiver_applied=waiver_applied, total_due=total_due, status="REVISED", \
                                 referenceid=ref_id, updated_at=datetime.now())
            messages.success(request, 'Waiver was added successfully.')

        else:
            messages.error(request, 'Waiver failed.')

        if demand_notice.exists():
            dn = demand_notice.get(Q(referenceid=ref_id))
            form = WaiverForm(request.POST or None, request.FILES or None, instance=dn)
            demand_notice = dn
            penalty = dn.penalty
            remittance = dn.remittance
            waiver_applied = dn.waiver_applied
            amount_paid = dn.amount_paid
            amount_due = dn.amount_due
            annual_fee = dn.annual_fee
            total_liability = dn.total_due #- dn.waiver_applied
            status = "REVISED"


            # SEND EMAIL TO TAX PAYER (REVISED)
            # mail_subject = "REVISED DEMAND NOTICE BY AGENCY!"
            # to_email = company.email
            agency = request.user
            html_content = render_to_string("Emails/admin/revised_notice.html", {
                "company":company,
                "agency_email":agency,
                "agency_phone":request.user.phone_number,
                "referenceid":ref_id,
                "waiver_applied":waiver_applied,
                "total_liability":total_liability,
                "login":settings.URL,
                })
            # text_content = strip_tags(html_content)
            # send_email_function(html_content, text_content, to_email, mail_subject)

            mail_subject = f"REVISED DEMAND NOTICE!: {ref_id}"
            email_template = "Emails/admin/revised_notice.html"
            agency_email_subject = f"NOTICE: REVISED DEMAND NOTICE - {company.company_name}"
            send_demand_notice_email(request, mail_subject, ref_id, dn.created_at, \
                                        total_due, email_template, agency_email_subject)
        else:
            form = WaiverForm(request.POST or None, request.FILES or None)

    company = User.objects.get(id=demand_notice.get(referenceid=ref_id).company.id)
    demand_notice = demand_notice.get(Q(referenceid=ref_id))
    
    penalty = demand_notice.penalty
    remittance = demand_notice.remittance
    waiver_applied = demand_notice.waiver_applied
    amount_paid = demand_notice.amount_paid
    amount_due = demand_notice.amount_due
    annual_fee = demand_notice.annual_fee
    total_liability = demand_notice.total_due 

    if Remittance.objects.filter(referenceid=ref_id).exists():
        receipt = Remittance.objects.get(referenceid=ref_id).receipt
    else:
        receipt = ''

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
        'receipt': receipt,
        'company': company,
        'form': WaiverForm(request.POST or None, request.FILES or None, instance=demand_notice)
    }
    return render(request, 'agency/pages/apply_waiver.html', context)

