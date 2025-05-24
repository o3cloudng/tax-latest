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
from core.services import generate_demand_notice, total_due, generate_ref_id
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
    infrastructures= Infrastructure.objects\
        .filter(Q(is_existing = False) & Q(processed = False) \
            & Q(company=request.user)).order_by('-created_at')

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
        'referenceid':  generate_ref_id(),
        'infra_types': InfrastructureType.objects.all().order_by('pk')

    }
    return render(request, 'tax-payers/apply_for_permit.html', context)

@login_required
def generate_demand_notice(request, ref_id):
    company = request.user
    if not Infrastructure.objects.select_related('infra_type') \
        .filter(Q(company=company) & Q(processed=False) & Q(created_by=company)).exists():
        messages.error(request, "No infrastructure entered.")
        return redirect('apply_for_permit')
    
    total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra = total_due(company, False)
    # Save to Demand Notice Table
    # referenceid, company, created_by, status (unpaid, disputed, revised, paid, resolved)
    # infrastructure cost, 
    obj, created = DemandNotice.objects.update_or_create(
        referenceid=ref_id,
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
        defaults={'referenceid': ref_id},
    )
    if obj or created:
        infra = Infrastructure.objects.filter(Q(is_existing=False) & Q(processed=False))
        infra.update(processed=True, referenceid=ref_id)
        # infra.save()
        messages.success(request, 'Demand notice created.')
        # return redirect('generate_receipt', ref_id)
        from core.utils import send_email_function
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        # Send Email here for demand notice
        mail_subject = f"Your Demand Notice Has Been Created Successfully - Ref No: {ref_id}"
        to_email = request.user.email
        
        html_content = render_to_string("Emails/tax_payer/demand_notice.html", {
            "company":request.user,
            "amount_due":obj.total_due,
            "referenceid":ref_id,
            "dn_date": obj.created_at,
            "login":settings.URL,
            })
        text_content = strip_tags(html_content)
        send_email_function(html_content, text_content, to_email, mail_subject)
        send_email_function(html_content, text_content, settings.TAX_AUTHOURITY_EMAIL, "NEW DEMAND NOTICE")
        messages.success(request, "Notification sent.")
        print(f"Your email has been sent to {request.user.company_name}")
        return redirect('generate_receipt', ref_id)
    
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


# @login_required
# def generate_receipt(request, ref_id):
#     company = request.user
#     admin_settings = AdminSetting.objects.all()
#     all = Infrastructure.objects.select_related('infra_type').filter(company=company)
#     infrastructure = all.values('infra_type__infra_name', 'cost')\
#         .annotate(num = Count('infra_type'), costing = Sum('cost'))\
#             .order_by('-created_at')

#     # downloads = all.values('infra_type__infra_name','upload_asBuilt_drawing', 'upload_application_letter').all()

#     # Sub Total
#     subtotal = infrastructure.aggregate(total = Sum('costing'))
#     # Application
#     app_fees = admin_settings.get(slug='application-fee')

#     total_app_fee = all.count() * app_fees.rate

#     admin_pm_fees = admin_settings.get(slug='admin-pm-fees')
#     # print(admin_pm_fees.rate, type(admin_pm_fees.rate))

#     admin_pm_fees_sum = admin_pm_fees.rate * subtotal['total'] / 100

#     sar_count = all.filter(Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')).count()
#     # print("SAR: ", admin_settings.get(slug='site-assessment'))
#     site_assessment = admin_settings.get(slug='site-assessment')
#     site_assessment_cost = sar_count * site_assessment.rate

#     print("SUB TOTAL: ", site_assessment_cost)
#     total_due = subtotal['total'] + total_app_fee + admin_pm_fees_sum + site_assessment_cost

#     remittance = 0
#     penalty = 0

#     total_liability = total_due + remittance + penalty
    
#     context = {
#         'infrastructure': infrastructure,
#         # 'downloads': downloads,
#         'ref_id': ref_id,
#         'subtotal': subtotal,
#         'agency': Agency.objects.all().first(),
#         'app_fee':admin_settings.get(slug='application-fee'),
#         'total_app_fee': total_app_fee,
#         'admin_pm_fees': admin_pm_fees,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'site_assessment': site_assessment,
#         'total_due': total_due,
#         'sar_count': sar_count,
#         'total_liability': total_liability,
#         'site_assessment_cost': site_assessment_cost        
#     }
    
#     return render(request, 'tax-payers/receipts/demand-notice.html', context)


# @login_required
# # @tax_payer_only
# def undispute_demand_notice_receipt(request, ref_id):
#     permits = Permit.objects.filter(referenceid = ref_id, is_disputed=True)
#     if not permits.first().company == request.user:
#         return redirect('apply_for_permit')
    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")

#     mast_roof = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')))
#     length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='Optic') | Q(infra_type__infra_name__icontains='Gas') | Q(infra_type__infra_name__icontains='Power') | Q(infra_type__infra_name__icontains='Pipeline')))
#     #application number = number of masts and rooftops 
#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
#         mast_roof_no = mast_roof_no['no_sites']
#     else:
#         app_count = length.count()
#         mast_roof_no = 0
    
#     if length.exists():
#         length = length.count()
#     else:
#         length = 0

    
#     app_count = mast_roof_no + length
#     total_app_fee = app_count * app_fee.rate

#     # print("APPLICATION COUNT: ", app_count)

#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True)).aggregate(no_sum = Sum('infra_cost'))
#     # print("Tot Sum: ", tot_sum_infra)

#     # Site assessment report rate
#     sar_rate = mast_roof_no['no_sites'] * site_assessment.rate

#     admin_pm_fees_sum = admin_pm_fees.rate * tot_sum_infra['no_sum'] / 100

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref).exists():
#         waver = Waiver.objects.get(referenceid=ref).wave_amount
#     else:
#         waver = 0
    
#     # print("WAVER: ", waver)
#     total_liability = total_due - waver

#     # Agency Details
#     agency = Agency.objects.all().first()
#     print("AGENCY: ", agency)
    

#     context = {
#         'permits': permits,
#         'ref': ref,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no['no_sites'],
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'tax-payers/receipts/undisputed_dn_receipt.html', context)

# @login_required
# @tax_payer_only
# def add_dispute_dn_edit(request):
#     ref_id = str(request.POST['referenceid'])
#     # print("REF: ", ref_id)
#     if request.htmx:
#         form = PermitEditForm(request.POST or None, request.FILES or None)

#         infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])
#         # print("READY POST: ", infra_rate.rate, type(infra_rate.rate))
#         # print("Permit type: ", request.POST['amount'], type(request.POST['amount']))
#         if "mast" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         elif "roof" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         else:
#             infra_cost = infra_rate.rate * int(request.POST['length'])
#             qty = 0
#             len = request.POST['length']

#         print("AMOUNT OR NUMBER: ", infra_rate.infra_name.lower())

#         if form.is_valid():
#             # print("Form is valid")
#             permit = form.save(commit=False)
#             permit.referenceid = ref_id
#             permit.company = request.user
#             permit.amount = qty
#             permit.length = len
#             permit.year_installed = str(datetime.now().date())
#             permit.infra_cost = infra_cost
#             permit.is_disputed = True
#             permit.is_existing = False
#             permit.save()

#             context = {
#                 'form':form,
#                 'referenceid': ref_id,
#                 'company': request.user
#             }
#             return HttpResponseClientRedirect('/tax/apply/permit/dispute_notice/'+permit.referenceid)
#             # return render(request, 'tax-payers/partials/inc/added_permit', context)
#         else:
#             print("FILE FORMAT INVALID")
#     form = PermitForm()

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return HttpResponseClientRedirect('/tax/apply/permit/dispute_notice/'+permit.referenceid)


# @login_required
# @tax_payer_only
# def add_undispute_edit(request):
#     ref_id = request.POST['referenceid']
#     if request.method == 'POST':
#         form = PermitEditForm(request.POST or None, request.FILES or None)

#         infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])
        
#         if "mast" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         elif "roof" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         else:
#             infra_cost = infra_rate.rate * int(request.POST['length'])
#             qty = 0
#             len = request.POST['length']

#         print("REFERENCE ID: ", ref_id)

#         if form.is_valid():
#             # print("Form is valid")
#             permit = form.save(commit=False)
#             permit.referenceid = ref_id
#             permit.company = request.user
#             permit.amount = qty
#             permit.year_installed = str(datetime.now().date())
#             permit.length = len
#             permit.infra_cost = infra_cost
#             permit.is_disputed = True
#             permit.save()

#             context = {
#                 'form':form,
#                 'referenceid': ref_id,
#                 'company': request.user
#             }
#             return HttpResponseClientRedirect('/tax/apply/permit/dispute_notice/'+permit.referenceid)

#         else:
#             print("FILE FORMAT INVALID")
#     form = PermitForm()

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return HttpResponseClientRedirect('/tax/apply/permit/dispute_notice/'+ref_id)


# @login_required
# @tax_payer_only
# def add_ex_undispute_edit(request):
#     ref_id = request.POST['referenceid']
#     if request.method == 'POST':
#         form = PermitEditForm(request.POST or None, request.FILES or None)

#         infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])
#         # print("READY POST: ", infra_rate.rate, type(infra_rate.rate))
#         # print("Permit type: ", request.POST['amount'], type(request.POST['amount']))
#         if "mast" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         elif "roof" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         else:
#             infra_cost = infra_rate.rate * int(request.POST['length'])
#             qty = 0
#             len = request.POST['length']

#         print("REFERENCE ID: ", ref_id)
#         year = int(request.POST['year']) + 1
#         str_year = str(year)+"-01-01"
#         installed_date = datetime.strptime(str(str_year), '%Y-%m-%d').date()
#         print("INSTALLED DATE: ", installed_date, type(installed_date))

#         if form.is_valid():
#             # print("Form is valid")
#             permit = form.save(commit=False)
#             permit.referenceid = ref_id
#             permit.company = request.user
#             permit.amount = qty
#             permit.length = len
#             permit.year_installed = installed_date
#             permit.infra_cost = infra_cost
#             permit.is_disputed = True
#             permit.is_existing = True
#             permit.save()

#             context = {
#                 'form':form,
#                 'referenceid': ref_id,
#                 'company': request.user
#             }
#             return HttpResponseClientRedirect('/tax/apply/permit/dispute_ex_notice/'+permit.referenceid)

#         else:
#             print("FILE FORMAT INVALID")
#     form = PermitForm()

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return HttpResponseClientRedirect('/tax/apply/permit/dispute_notice/'+permit.referenceid)


# @login_required
# @tax_payer_only
# def del_undisputed_edit(request, pk):
#     permit = Permit.objects.get(pk=pk)
#     permit.delete()
#     print("DELETE NEW WORKING....: ")

#     return HttpResponseClientRedirect('/tax/apply/permit/dispute_notice/'+permit.referenceid)



# @login_required
# @tax_payer_only
# def accept_undisputed_edit(request, pk):
#     permit = Permit.objects.get(pk=pk)

#     pm = Permit.objects.create(
#         company= permit.company,
#         referenceid= permit.referenceid,
#         infra_type= permit.infra_type,
#         amount= permit.amount,
#         length= permit.length,
#         add_from= permit.add_from,
#         add_to= permit.add_to,
#         year_installed= str(permit.year_installed), 
#         age= permit.age,
#         upload_application_letter= permit.upload_application_letter,
#         upload_asBuilt_drawing= permit.upload_asBuilt_drawing,
#         upload_payment_receipt= permit.upload_payment_receipt,
#         status= permit.status,
#         is_disputed= True,
#         is_undisputed= permit.is_undisputed,
#         is_revised= permit.is_revised,
#         is_paid= permit.is_paid,
#         is_existing= False
#     )
#     # context = {
#     #     pm:pm
#     # } 
#     print("ACCEPTED DN: .....", pm)
#     return redirect('dispute-demand-notice', permit.referenceid)
#     # return render(request, 'tax-payers/partials/inc/added_permit.html', context)
#     # return HttpResponseClientRedirect(reverse_lazy('dispute-ex-demand-notice', permit.referenceid))
#     # return HttpResponseClientRedirect('/tax/apply/permit/dispute_ex_notice/'+permit.referenceid)


# @login_required
# @tax_payer_only
# def dispute_dn_edit(request, pk):
#     permit = Permit.objects.get(pk=pk)
#     form = PermitEditForm(instance = permit)
#     context = {
#         'form': form
#     }
#     return render(request, 'tax-payers/partials/apply_permit_edit_form.html', context)


# @login_required
# @tax_payer_only
# def dispute_demand_notice(request, ref_id):

#     ref = Q(referenceid=ref_id)
#     coy = Q(company=request.user)
#     is_dis = Q(is_disputed = True)
#     not_dis = Q(is_disputed = False)
#     not_exist = Q(is_existing = False)
#     permits = Permit.objects.filter(ref & coy & not_dis & not_exist)
#     undisputed_permits = Permit.objects.filter(ref & coy & is_dis & not_exist)
#     # print("PERMIT COUNT: ", permits)
#     # print("UNDISPUTED COUNT: ", undisputed_permits)
    
#     # if request.method == "POST":
#     #     print("POST SHOWS HERE....")
   
#     context = {
#         'ref_id': ref_id,
#         'permits': permits,
#         'undisputed_permits': undisputed_permits
#     }
#     return render(request, 'tax-payers/apply_for_permit_edit.html', context)



# @login_required
# @tax_payer_only
# def apply_for_permit_edit(request, ref_id):

#     permits = Permit.objects.filter(referenceid = ref_id)
#     infra_type = InfrastructureType.objects.all()

#     if request.htmx:
#         form = PermitForm(request.POST or None, request.FILES or None)
#         infra = InfrastructureType.objects.get(id=request.POST['infra_type'])
#         print("INFRA: ", infra)
#         form.infra_type = infra

#         # Get the rate for each infrastructure from the InfrastructureType Table
#         infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])

#         # If Infrastructure is a Mast or Roof - Make length = 0 and infra_cost = the rate * quantity
#         # If Infrastructure is a  - Make length = 0 and infra_cost = the rate * length
#         if "mast" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         elif "roof" in infra_rate.infra_name.lower():
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#             len = 0
#             qty = request.POST['amount']
#         else:
#             infra_cost = infra_rate.rate * int(request.POST['length'])
#             qty = 0
#             len = request.POST['length']

#         if form.is_valid():
#             print("Dispute Form is valid")
#             permit = form.save(commit=False)
#             permit.referenceid = ref_id
#             permit.company = request.user
#             permit.amount = qty
#             permit.length = len
#             permit.infra_cost = infra_cost
#             permit.save()
#         else:
#             print(form.errors)
        

#     # form = PermitForm(instance = permits)
#     context = {
#         'permits': permits,
#         'ref_id': ref_id,
#         'infra_type': infra_type,
#         'form': form
#     }
#     print("APPLY PERMIT EDIT CONTEXT: ", context)
#     if request.htmx:
#         messages.success(request,"Infrastructure disputed successfully.")
#         return HttpResponseClientRedirect('/tax/apply/permit/edit/'+ref_id)
    
#     return render(request, 'tax-payers/apply_for_permit_edit.html', context)


# @login_required # Check this after
# # @tax_payer_only
# def add_permit_form(request):
#     if Permit.objects.all().exists(): 
#         last = Permit.objects.latest("pk").id
#         ref_id = "LA"+generate_ref_id() + str(last + 1).zfill(5)
#     else:
#         ref_id = generate_ref_id() + "00001"
    
#     permits = Permit.objects.all()
#     if request.method == "POST":
#         form = PermitForm(request.POST or None, request.FILES or None)
#         if form.is_valid():
#             permit = form.save(commit=False)
#             # permit.referenceid = ref_id
#             permit.referenceid = request.user
#             permit.save()
#             permits = Permit.objects.all()
#             context = {
#                 'permits': permits
#             }

#             print("USER ID: ", permits)
#             return render(request, 'tax-payers/partials/permit_details.html', context)
#         else:
#             print("ERROR: ", form.errors)

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return render(request, 'tax-payers/partials/apply_permit_form.html', context)


# @login_required 
# def add_new_permit_form(request, ref_id):
    
#     permits = Permit.objects.all()
#     if request.method == "POST":
#         form = PermitForm(request.POST or None, request.FILES or None)
#         if form.is_valid():
#             permit = form.save(commit=False)
#             # permit.referenceid = ref_id
#             permit.referenceid = request.POST['referenceid']
#             permit.is_disputed = True
#             permit.is_existing = False
#             permit.save()
#             permits = Permit.objects.all()
#             context = {
#                 'permits': permits
#             }

#             return render(request, 'tax-payers/partials/permit_details.html', context)
#         else:
#             print(form.errors)

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return render(request, 'tax-payers/partials/apply_new_permit_form.html', context)


# @login_required 
# @tax_payer_only
# def add_new_ex_permit_form(request, ref_id):
    
#     permits = Permit.objects.all()
#     if request.method == "POST":
#         form = PermitForm(request.POST or None, request.FILES or None)
#         if form.is_valid():
#             permit = form.save(commit=False)
#             permit.referenceid = request.POST['referenceid']
#             permit.is_disputed = True
#             permit.is_existing = True
#             permit.save()
#             permits = Permit.objects.all()
#             context = {
#                 'permits': permits
#             }

#             return render(request, 'tax-payers/partials/permit_details.html', context)
#         else:
#             print(form.errors)

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return render(request, 'tax-payers/partials/apply_new_ex_permit_form.html', context)

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

# @login_required
# @tax_payer_only
# def demand_notice_receipt(request, ref_id):
#     permits = Permit.objects.filter(Q(referenceid = ref_id))
#     if not permits.exists():
#         return redirect('apply_for_permit')
    
#     if not permits.first().company == request.user:
#         return redirect('apply_for_permit')
    
#     if permits.first().is_existing:
#         return redirect('demand_notice_ex_receipt', ref_id)
    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")

#     # mast_roof = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=False), Q(infra_type__infra_name__istartswith='mast') | Q(infra_type__infra_name__istartswith='roof'))
#     length = Permit.objects.filter(Q(referenceid = ref_id, is_disputed=False), Q(infra_type__infra_name__istartswith='Optic') | Q(infra_type__infra_name__istartswith='Gas') | Q(infra_type__infra_name__istartswith='Power') | Q(infra_type__infra_name__istartswith='Pipeline'))
#     #application number = number of masts and rooftops 
#     mast_roof = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=False) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')))
   
    
#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
#         mast_roof_no = mast_roof_no['no_sites']
#     else:
#         mast_roof_no = 0
    
#     if length.exists():
#         length = length.count()
#     else:
#         length = 0

#     app_count = mast_roof_no + length
#     # print("APP COUNTs: ", app_count, "Masts: ", mast_roof_no)
#     total_app_fee = app_count * app_fee.rate

#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=False)).aggregate(no_sum = Sum('infra_cost'))
#     print("tot_sum_infra: ", Permit.objects.filter(Q(referenceid = ref_id)))
#     # Site assessment report rate
#     sar_rate = mast_roof_no * site_assessment.rate

#     admin_pm_fees_sum = admin_pm_fees.rate * tot_sum_infra['no_sum'] / 100

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref).exists():
#         waver = Waiver.objects.get(referenceid=ref).wave_amount
#     else:
#         waver = 0
    
#     # print("WAVER: ", waver)
#     total_liability = total_due - waver
    
#     context = {
#         'permits': permits,
#         'ref': ref,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no,
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'tax-payers/receipts/demand-notice-receipt.html', context)

# @login_required
# @tax_payer_only
# def dispute_demand_notice_receipt(request, ref_id):
#     print("DN - REF ID: ", ref_id)

#     if not Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & Q(is_existing=False)).exists():
#          return redirect('dashboard')
    
#     permits = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & Q(is_existing=False))
#     if not permits.first().company == request.user:
#         return redirect('dashboard')
    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")

#     mast_roof = Permit.objects.filter(Q(referenceid = ref_id, is_disputed=True), Q(infra_type__infra_name__istartswith='Mast') | Q(infra_type__infra_name__istartswith='Roof'))
#     length = Permit.objects.filter(Q(referenceid = ref_id, is_disputed=True), Q(infra_type__infra_name__istartswith='Optic') | Q(infra_type__infra_name__istartswith='Gas') | Q(infra_type__infra_name__istartswith='Power') | Q(infra_type__infra_name__istartswith='Pipeline'))
#     #application number = number of masts and rooftops 

#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
#         mast_roof_no = mast_roof_no['no_sites']
#     else:
#         app_count = length.count()
#         mast_roof_no = 0
    
#     if length.exists():
#         length = length.count()
#     else:
#         length = 0
    
#     app_count = mast_roof_no + length
#     total_app_fee = app_count * app_fee.rate

#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True)).aggregate(no_sum = Sum('infra_cost'))
#     # print(Permit.objects.filter(Q(referenceid = ref_id, is_disputed=True)))
#     # Site assessment report rate
#     sar_rate = mast_roof_no['no_sites'] * site_assessment.rate

#     admin_pm_fees_sum = admin_pm_fees.rate * tot_sum_infra['no_sum'] / 100

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref).exists():
#         waver = Waiver.objects.get(referenceid=ref).wave_amount
#     else:
#         waver = 0
    
#     # print("WAVER: ", waver)
#     total_liability = total_due - waver
    

#     context = {
#         'permits': permits,
#         'ref': ref,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no['no_sites'],
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'is_disputed': True,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'tax-payers/receipts/undisputed-receipt.html', context)

