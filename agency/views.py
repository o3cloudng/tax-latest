from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorator import admin_only
from django.shortcuts import redirect
from django.contrib import messages
from tax.models import InfrastructureType, Waiver, Remittance, Infrastructure, DemandNotice
from account.models import AdminSetting
from django.urls import reverse_lazy
from django_htmx.http import HttpResponseClientRedirect
from django.db.models import Q, Count, Sum, Max
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from account.models import User, Sector
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from agency.tasks import task_func, send_email_func
from agency.forms import AgencyForm, InfrastructureSettingsForm, AddUserForm, NotificationForm, RevenueForm
from tax.forms import InfrastructureForm, InfrastructureForm2
from agency.models import Agency, Notification
from agency.forms import InfrastructureSettingsForm, RevenueForm, SectorForm
from django.urls import reverse_lazy
from tax.forms import WaiverForm 
from core.utils import send_email_function
from core import settings
from datetime import datetime
from django.utils import timezone
from tax.forms import RemittanceForm, BulkUploadForm
from tax.views.existing_infra_view import generate_ref_id
from core.services import total_due, subtotal_due, agency_total_due
from django.contrib.contenttypes.models import ContentType
from easyaudit.models import CRUDEvent, LoginEvent
import csv, io
from django.db import transaction


# Create your views here.
@login_required
@admin_only
def agency_dashboard(request):
    one_month = Q(created_at__gte=(now()-relativedelta(months=1)))
    # Total No of Registered Tax Payers
    companies = User.objects.filter(Q(is_tax_admin=False) & Q(is_disabled=False))
    if companies.exists():
        tax_payers = companies
    else:
        tax_payers = []

    # New Task Payers (In the last 30 days)
    if companies.filter(one_month).exists():
        tax_payers_month = companies.filter(one_month)
        tax_payers_month = tax_payers_month.count() / tax_payers.count() * 100
    else:
        tax_payers_month = 0

    # Total number of infrastructures
    infrastructures = Infrastructure.objects.filter(Q(processed=True))
    total_infrastructures = infrastructures.count()
    # New Infrastructure in last 30 days
    if infrastructures.filter(one_month).exists():
        infrastructures_month = infrastructures.filter(one_month)
        infrastructures_month = infrastructures_month.count() / infrastructures.count() * 100
        # print(f"Infrastructure / Month {infrastructures_month}")
    else:
        infrastructures_month = []
        
    # Demand Notices
    demand_notices = DemandNotice.objects.all()
    demand_notice = demand_notices.count() # demand_notices

    if demand_notices.filter(one_month).exists():
        demand_notices_month = demand_notices.filter(one_month)
        demand_notices_month = demand_notices_month.count() / demand_notices.count() * 100
    else:
        demand_notices_month = []
    
    # Comapany count by sector
    sectors = companies.select_related('sector').values('sector__name').filter(Q(is_tax_admin=False) & ~Q(sector=None)).annotate(sect=Count('sector')).order_by('sector')

    sector_name = []
    sector_count = []
    for s in sectors:
        sector_name.append(s['sector__name'])
        sector_count.append(s['sect'])
        
    # REVENUE BY SECTORS
    revenue_dn = DemandNotice.objects.select_related('company').values('company__sector__name')\
        .annotate(revenue = Sum('total_due'))
    # print(f"Revenue: {revenue_dn}")
    
    revenue_name = []
    revenue_sum = []
    for rdn in revenue_dn:
        revenue_name.append(rdn['company__sector__name'])
        revenue_sum.append(rdn['revenue'])

    infra_rev = infrastructures.select_related('infra_type').values('infra_type__infra_name')\
        .annotate(count = Count('infra_type'), costing=Sum('cost'))
    infra_name = []
    infra_count = []
    infra_sum = []
    for s in infra_rev:
        infra_name.append(s['infra_type__infra_name'])
        infra_count.append(s['count'])
        infra_sum.append(s['costing'])
    
    # Demand Notices
    resolved = demand_notices.filter(Q(status='RESOLVED')).values('total_due')\
        .annotate(count=Count('referenceid'), paid=Sum('total_due'))
    unresolved = demand_notices.filter(~Q(status='RESOLVED')).values('total_due')\
        .annotate(count=Count('referenceid'), paid=Sum('total_due'))
    resolved_count = resolved.count()
    unresolved_count = unresolved.count()

    resolved_sum = []
    for x in resolved:
        resolved_sum.append(x['total_due'])

    unresolved_sum = []
    for x in unresolved:
        unresolved_sum.append(x['total_due'])
        
    # AUDIT TRAIL
    audit_trail = CRUDEvent.objects.all().order_by('-datetime')[:5]
    # for a in audit_trail:

    log_events = LoginEvent.objects.all().order_by('-datetime')[:9]
    # for x in log_events:


    context = {
        "tax_payers": tax_payers,
        "tax_payers_month": tax_payers_month,
        "infrastructures": infrastructures,
        "total_infrastructures": total_infrastructures,
        "infrastructures_month": infrastructures_month,
        "demand_notices": demand_notices,
        "demand_notice": demand_notice,
        "demand_notices_month": demand_notices_month,
        "revenue_name": revenue_name,
        "revenue_sum":revenue_sum,
        "infra_name": infra_name,
        "infra_count":infra_count,
        "infra_sum":infra_sum,
        "sector_name": sector_name,
        "sector_count": sector_count,
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
        "resolved_sum": resolved_sum,
        "unresolved_sum": unresolved_sum,
        "audit_trail": audit_trail,
        "log_events": log_events,
    }
    return render(request, 'agency/pages/admin-dashboard.html', context)

@login_required
@admin_only
def agency_demand_notice(request):
    # All, Unpaid, Disputed, Revised, Paid
    all = DemandNotice.objects.all().order_by('-created_at')
    demand_notices = all.all()
    undisputed_unpaid = all.filter(Q(status='UNDISPUTED UNPAID'))
    undisputed_paid = all.filter(Q(status='UNDISPUTED'))
    revised = all.filter(Q(status='REVISED'))
    resolved = all.filter(Q(status='RESOLVED'))
    demand_notice = all.filter(Q(status='DEMAND NOTICE'))
    disputed = all.filter(Q(status__icontains='UNDISPUTED'))

    total_demand_notices = demand_notices.aggregate(total = Sum('total_due'))['total']
    total_undisputed_paid = undisputed_paid.aggregate(total = Sum('total_due'))['total']
    total_undisputed_unpaid = undisputed_unpaid.aggregate(total = Sum('total_due'))['total']
    total_revised = revised.aggregate(total = Sum('total_due'))['total']
    total_resolved = resolved.aggregate(total = Sum('total_due'))['total']

    if not total_demand_notices:
        total_demand_notices = 0.00

    if not total_undisputed_paid:
        total_undisputed_paid = 0.00

    if not total_undisputed_unpaid:
        total_undisputed_unpaid = 0.00

    if not total_revised:
        total_revised = 0.00

    if not total_resolved:
        total_resolved = 0.00

    context = {
        "is_profile_complete" : False,
        "demand_notices": demand_notices,
        "total_demand_notices": total_demand_notices,
        "total_undisputed_paid": total_undisputed_paid,
        "total_undisputed_unpaid": total_undisputed_unpaid,
        "total_revised": total_revised,
        "total_resolved": total_resolved,
        "resolved": resolved,
        "revised": revised,
        "disputed": disputed,
        "demand_notice": demand_notice,
    }
    return render(request, 'agency/pages/admin-demand-notices.html', context)

# TESTING TABLES
# import django_tables2 as tables
from agency.tables import DemandNoticeTables
from django_tables2 import RequestConfig
# from django.views.generic import ListView
from django_tables2 import SingleTableView

def demand_notice_table(request):
    table = DemandNoticeTables(DemandNotice.objects.all())
    table.paginate(page=request.GET.get("page", 1), per_page=5)
    # RequestConfig(request, paginate={"per_page": 5}).configure(table)
    return render(request, "demand-notice-table.html", {"table": table})
    
    
class DemandTable(SingleTableView):
    model = DemandNotice
    paginate_by = 5
    table_class = DemandNoticeTables
    template_name = "demand-notice-table.html"

@login_required
@admin_only
def agency_disputes(request):
    one_month = Q(created_at__gte=(now()-relativedelta(months=1)))

    all = DemandNotice.objects.all().order_by('-updated_at')
    disputed = all.filter(Q(status__icontains="DISPUTED") | Q(status__icontains="RESOLVED"))
    if disputed.exists():
        all_last_month =  disputed.filter(one_month)
        all_last_month_perc = all_last_month.count() / disputed.count() * 100
    else:
        all_last_month_perc = 0

    resolved = all.filter(Q(status="RESOLVED"))
    if resolved.exists():
        resolved_last_month =  all.filter(one_month & Q(status="RESOLVED"))
        resolved_last_month_perc = resolved_last_month.count() / resolved.count() * 100
    else:
        resolved_last_month_perc = 0


    unresolved = disputed.all()
    if unresolved.exists():
        unresolved_last_month =  disputed.filter(one_month)
        unresolved_last_month_perc = unresolved_last_month.count() / unresolved.count() * 100
        
    else:
        unresolved_last_month_perc = 0

    context = {
        "all": disputed,
        "all_last_month_perc": all_last_month_perc,
        "resolved": resolved,
        "resolved_last_month_perc": resolved_last_month_perc,
        "unresolved_last_month_perc": unresolved_last_month_perc,
        "unresolved": unresolved,
    }
    return render(request, 'agency/pages/admin-disputes.html', context)

@login_required
@admin_only
def agency_infrastructure(request):
    infrastructures = Infrastructure.objects.all()
    masts = infrastructures.filter(Q(infra_type__infra_name__icontains="mast"))
    rooftop = infrastructures.filter(Q(infra_type__infra_name__icontains="rooftop"))
    m = Q(infra_type__infra_name__icontains="mast")
    r = Q(infra_type__infra_name__icontains="roof")
    f = Q(infra_type__infra_name__icontains="fibre")
    others = infrastructures.filter(~m & ~r & ~f)
    # mast_roof = Q(infra_type__infra_name__icontains="roof") | Q(infra_type__infra_name__icontains="mast")
    
    one_month = Q(created_at__gte=(now()-relativedelta(months=1)))
    # roof = Permit.objects.filter(is_disp & roof)
    fibre = infrastructures.filter(Q(infra_type__infra_name__icontains="fibre"))
    power_line = infrastructures.filter(Q(infra_type__infra_name__icontains="power"))
    pipeline = infrastructures.filter(Q(infra_type__infra_name__icontains="pipe"))
    gas_powerline = infrastructures.filter(Q(infra_type__infra_name__icontains="gas") &\
                                            Q(infra_type__infra_name__icontains="line"))

    # infrastructures = Permit.objects.all()

    # Percentage in the past 1 Month
    if masts.exists():
        mast_last_month =  infrastructures.filter(one_month)
        mast_last_month_perc = mast_last_month.count() / masts.count() * 100
    else:
        mast_last_month_perc = 0 

    if fibre.exists():
        fibre_last_month =  infrastructures.filter(one_month & Q(infra_type__infra_name__icontains="fibre"))
        fibre_last_month_perc = fibre_last_month.count() / fibre.count() * 100
        
    else:
        fibre_last_month_perc = 0

    if power_line.exists():
        power_line_last_month =  infrastructures.filter(one_month & Q(infra_type__infra_name__icontains="power"))
        power_line_last_month_perc = power_line_last_month.count() / power_line.count() * 100
        
    else:
        power_line_last_month_perc = 0
    if pipeline.exists():
        pipeline_last_month =  infrastructures.filter(one_month & Q(infra_type__infra_name__icontains="pipe"))
        pipeline_last_month_perc = pipeline_last_month.count() / pipeline.count() * 100
        
    else:
        pipeline_last_month = 0

    

    # mast_count = masts.aggregate(no_m = Sum('amount'))
    
    context = {
        "infrastructures": infrastructures,
        "rooftop": rooftop,
        "masts": masts,
        "others": others,
        "mast_last_month_perc": mast_last_month_perc,
        "power_line": power_line,
        "power_line_last_month_perc": power_line_last_month_perc,
        "pipeline": pipeline,
        "fibre": fibre,
        "fibre_last_month_perc": fibre_last_month_perc,
        "gas_powerline": gas_powerline
    }
    return render(request, 'agency/pages/admin-infrastructure.html', context)

@login_required
@admin_only
def agency_companies(request):
    companies = User.objects.filter(Q(is_tax_admin = False) & Q(is_superuser = False))
    comp_count = companies.count()
    one_month = Q(created_at__gte=(now()-relativedelta(months=1)))

    company_month =  User.objects.filter(one_month & Q(is_tax_admin = False))
    company_month_perc = company_month.count() * comp_count / 100

    nullified = User.objects.filter(is_disabled=True)
    if User.objects.filter(is_disabled=True).exists():
        nullified_month =  User.objects.filter(one_month & Q(is_disabled = True))
        
        nullified_perc = nullified_month.count() / nullified.count() * 100
    else:
        nullified_perc = 0

    if request.method=='POST':
        search = request.POST.get('search')
        
        all_companies = User.objects.filter(is_tax_admin=False)
        if search:
            companies = all_companies.filter(Q(company_name__icontains=search)) #& Q(is_tax_admin=False))
        else:
            companies = User.objects.filter(is_tax_admin=False)

        context = {
            "companies": companies
        }
        return render(request, 'agency/pages/companies.html#company', context)


    context = {
        "companies": companies,
        "company_month": company_month,
        "company_month_perc": company_month_perc,
        "nullified": nullified.count(),
        "nullified_perc": nullified_perc,
        "company_form": AddUserForm(),
        "comp_count": comp_count
    }
    return render(request, 'agency/pages/companies.html', context)

@login_required
@admin_only
def agency_companies_details(request, pk):
    if User.objects.filter(pk=pk).exists():
        company = User.objects.get(pk=pk)

        infrastructures = Infrastructure.objects.filter(company=company)
        mast = infrastructures.filter(infra_type__infra_name__icontains='mast')
        roof = infrastructures.filter(infra_type__infra_name__icontains='roof')
        fibre_optics = infrastructures.filter(infra_type__infra_name__icontains='fibre')
        others = infrastructures.filter(~Q(infra_type__infra_name__icontains='mast') & \
                                        ~Q(infra_type__infra_name__icontains='roof') & \
                                        ~Q(infra_type__infra_name__icontains='fibre') \
                                        )

        all = DemandNotice.objects.filter(company=company).order_by('-created_at')
        demand_notices = all.all()
        # undisputed_unpaid = all.filter(Q(status='UNDISPUTED UNPAID'))
        # undisputed_paid = all.filter(Q(status='UNDISPUTED'))
        revised = all.filter(Q(status='REVISED'))
        resolved = all.filter(Q(status='RESOLVED'))
        demand_notice = all.filter(Q(status='DEMAND NOTICE'))
        disputed = all.filter(Q(status__icontains='UNDISPUTED'))
        unresolved = all.filter(~Q(status="PAID") & ~Q(status="REVISED"))

        context = {
            "is_profile_complete" : False,
            'company': company,
            'disputed': disputed,
            'revised': revised,
            'demand_notices': demand_notices,
            'mast': mast,
            'roof': roof,
            'fibre_optics': fibre_optics,
            'others': others,
            'resolved': resolved,
            'unresolved': unresolved,
            
            # "total_demand_notices": total_demand_notices,
            # "total_undisputed_paid": total_undisputed_paid,
            # "total_undisputed_unpaid": total_undisputed_unpaid,
            # "total_revised": total_revised,
            # "total_resolved": total_resolved,
            "demand_notice": demand_notice,
        }
    return render(request, 'agency/pages/company_detail.html', context)


@login_required
@admin_only
def agency_help(request):
    context = {}
    return render(request, 'agency/pages/downloads.html', context)


@login_required
@admin_only
def agency_settings(request):
    if Agency.objects.all().exists():
        agency = Agency.objects.first()
        angency_create_form = AgencyForm(instance=agency)
    else:
        angency_create_form = AgencyForm()
    if request.method == 'POST':
        form = AgencyForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            agency = form.save(commit=False)
            agency.is_tax_admin = True
            agency.save()

            messages.success(request, "Agent created successfully.")
            return redirect(reverse_lazy("agency_settings"))
        else:
            messages.error(request, "Agent creation failed.")
            return redirect(reverse_lazy("agency_settings"))
            
    context = {
        "angency_create_form": angency_create_form,
        "agency": Agency.objects.all(),
        'infrastructure_form': InfrastructureSettingsForm(),
        'infrastructure': InfrastructureType.objects.all(),
        'sectors': Sector.objects.all(),
        'sector_form': SectorForm(),
        'admin_settings': AdminSetting.objects.all(),
        'company_form': AddUserForm(),
        'companies': User.objects.filter(is_superuser=False),
        'notifications': Notification.objects.all(),
        'notification_form': NotificationForm(),
        'revenue_form': RevenueForm(),
    }
    return render(request, 'agency/pages/admin-settings.html', context)

@login_required
def add_company(request):
    if request.htmx:
        form = AddUserForm(request.POST or None)
        if form.is_valid():
            company = form.save(commit=False)
            if company.is_tax_admin != 0:
                company.is_tax_admin = 1
            company.save()

            messages.success(request, "Agency created successfully.")
            context = {
                "company": company
            }
            return render(request,"agency/pages/admin-settings.html#company", context)
        else:
            messages.error(request, "Agency creation failed.")
            return render(request,"agency/pages/admin-settings.html#company", context)

@login_required
def create_company(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST or None)
        if form.is_valid():
            company = form.save(commit=False)
            if company.is_tax_admin != 0:
                company.is_tax_admin = 1
            company.save()

            messages.success(request, "Company created successfully.")
            context = {
                "company": company
            }

            return redirect(reverse_lazy("agency_companies"))
        else:
            messages.error(request, "Company creation failed.")
            return redirect(reverse_lazy("agency_companies"))

@login_required
def add_update_infrastructure(request):
    infra_rate = str(request.POST.get('rate')).split('.')[0].replace(',','')
    
    form = InfrastructureSettingsForm(request.POST)
    if request.htmx:
        if form.is_valid():
            if InfrastructureType.objects.filter(infra_name=request.POST.get('infra_name')).exists():
                infra_settings = InfrastructureType.objects.filter(infra_name=request.POST.get('infra_name'))
                infra_settings.update(rate=infra_rate, updated_at=datetime.now())
                messages.success(request, "Infrastructure type updated successfully")
            else:
                InfrastructureType.objects.create(\
                    infra_name=request.POST.get('infra_name'),\
                        rate=request.POST.get('rate'))
                messages.success(request, "Infrastructure type added successfully")
        else:
            return HttpResponseClientRedirect(reverse_lazy("agency_settings"))

@login_required
def add_update_sector(request):
    if request.htmx:
        sector_name = request.POST.get('sector')
        if Sector.objects.filter(name=sector_name).exists():
            sector = Sector.objects.filter(name__icontains=sector_name)
            sector.update(name=sector_name, modified_at=timezone.now())
            messages.success(request, "Sector updated successfully")
        else:
            Sector.objects.create(name=sector_name, modified_at=timezone.now())
            messages.success(request, "Sector added successfully")
            
        return HttpResponseClientRedirect(reverse_lazy("agency_settings"))

@login_required
def add_update_revenue(request):
    rev_name = str(request.POST.get('name')).replace(' ', '-').lower()
    rev_rate = str(request.POST.get('rate')).split('.')[0].replace(',','')
    description = request.POST.get('description')
    
    if request.htmx:
        if AdminSetting.objects.filter(slug__icontains=rev_name).exists():
            admin_settings = AdminSetting.objects.filter(slug=rev_name)
            admin_settings.update(description=description, rate=rev_rate, updated_at=datetime.now())
            messages.success(request, "Revenue updated successfully")
        else:
            AdminSetting.objects.create(name=request.POST.get('name'),\
                description=description, rate=rev_rate,\
                    updated_at=datetime.now())
            messages.success(request, "Revenue added successfully")
            
        return HttpResponseClientRedirect(reverse_lazy("agency_settings"))

@login_required
def edit_company(request, pk):
    if request.htmx:
        company = User.objects.get(pk=pk)
        company_form = AddUserForm(instance=company)
        if request.method == 'POST':
            form = AddUserForm(request.POST or None, instance=company)
            if form.is_valid():
                
                form.save(commit=False)
                if request.POST.get("is_tax_admin") != 0:
                    form.is_tax_admin = 1
                form.save()

                messages.success(request, f"{company.company_name} updated successfully.")
                return HttpResponseClientRedirect(reverse_lazy("agency_settings"))
            
                # context = {
                #     "company": company
                # }
                # return render(request,"agency/partials/edit_company.html", context)
            else:
                messages.error(request, f"{company.company_name} failed.")
                return HttpResponseClientRedirect(reverse_lazy("agency_settings"))
        context = {
            "company_form": company_form,
            "company": company
        }
        return render(request,"agency/partials/edit_company.html", context)

@login_required
def deactivate_company(request, pk):
    if request.htmx:
        company = User.objects.get(pk=pk)
        if request.method == 'POST':
            company.is_disabled = True
            company.save()

            messages.error(request, f"{company.company_name} has been disabled.")
            return HttpResponseClientRedirect(reverse_lazy("agency_settings"))
           
        context = {
            "company": company
        }
        return render(request,"agency/partials/deactivate_company.html", context)

@login_required
def reactivate_company(request, pk):
    if request.htmx:
        company = User.objects.get(pk=pk)
        if request.method == 'POST':
            company.is_disabled = False
            company.save()

            messages.success(request, f"{company.company_name} is now enabled.")
            return HttpResponseClientRedirect(reverse_lazy("agency_settings"))
           
        context = {
            "company": company
        }
        return render(request,"agency/partials/deactivate_company.html", context)

@login_required
def add_notification(request):
    if request.htmx:
        form = NotificationForm(request.POST or None)
        if form.is_valid():
            # HTMX NOTIFICATION FORM...
            note = form.save()

            messages.success(request, "Agency created successfully.")
            context = {
                "notifications": note
            }
            return render(request,"agency/pages/admin-settings.html#notification", context)
        # else:
        #     print(form.errors)
        # context = {
        #     "company_form": form,
        # }
        # return render(request,"agency/pages/admin-settings.html", context)
    

@login_required
def agency_account(request):
    if request.method == 'POST':
        agency = Agency.objects.get(agency_email=request.POST.get('agency_email'))
        # instance = Agency.objects.get(id=agency[0].id)
        form = AgencyForm(request.POST or None, request.FILES or None, instance=agency)
        if form.is_valid():
            # agency = form.save(commit=False)
            form.save()

            messages.success(request, "Agency updated successfully.")
            # context = {}
            return redirect('agency_settings')
            # return render(request,"agency/pages/admin-settings.html#agent", context)
            
        context = {
            "angency_create_form": form
        }
        return render(request,"agency/pages/admin-settings.html", context)
    

@login_required
def company_approve_waiver(request):
    if request.method == 'POST':
        form = WaiverForm(request.POST or None)
        if not Waiver.objects.filter(referenceid=request.POST["referenceid"]).exists():
            if form.is_valid():
                form.save()

                messages.success(request, "Waiver applied successfully.")
                return redirect('company_dispute_receipt', request.POST.get("referenceid"))
        else:
            if form.is_valid():
                waiver = Waiver.objects.get(referenceid=request.POST["referenceid"])
                waiver.wave_amount = request.POST["wave_amount"]
                waiver.save()

    return redirect('company_dispute_receipt', request.POST.get("referenceid"))
        
@login_required
def send_revised_notice(request):
    # EMAIL TO NEW COMPANY 
    agency = Agency.objects.first()
    
    company = User.objects.get(email=request.POST['company'])
    # Send email to new user company
    mail_subject = f"Revised Demand Notice - Ref No: {request.POST['referenceid']}"
    to_email = company.email
    
    html_content = render_to_string("Emails/admin/revised_notice.html", {
        "company":company,
        "agency_email":agency.agency_email,
        "agency_phone":agency.phone_number,
        "revised_amount":request.POST['revised_amount'],
        "referenceid":request.POST['referenceid'],
        "login":settings.URL,
        })
    text_content = strip_tags(html_content)
    send_email_function(html_content, text_content, to_email, mail_subject)
    messages.success(request, "Notification sent.")
    return redirect('company_revised_receipt', request.POST.get("referenceid"))



def notification_view(request):
    pass

def validate_name(request):
    pass

def test_celery(request):
    task_func.delay_on_commit()
    return HttpResponse("Done")


def sendemail(request):
    send_email_func.delay_on_commit()
    return HttpResponse("Email sent.")

def send_email_html(request):
    # EMAIL TEST
    mail_subject = "VIEW CELERY EMAIL"
    to_email = "o3cloudng@gmail.com"
    html_content = render_to_string("Emails/tax_payer/new_company_reg.html", {
        "user_name":"Olumide", 
        "password":"Password",
        "to_email":to_email,
        })
    text_content = strip_tags(html_content)
    send_email_function(html_content, text_content, to_email, mail_subject)
    return HttpResponse("HTML Email sent.")

def email_template(request):
    return render(request, 'Emails/tax_payer/forgot_password.html', context={})



@login_required
# @tax_payer_only
@transaction.atomic
def agency_upload_new(request):
    ref_id = generate_ref_id()
    if request.method == 'POST':
        bulk_upload = request.FILES['bulk_upload']
        company = User.objects.get(pk=request.POST['company'])
        # resource = InfrastructureResource()
        # return f"COMPANY: {company}"
    
        if not bulk_upload.name.endswith('csv'):
            messages.error(request, 'Wrong file format')
            return redirect('apply_existing_infra')
        
        dataset = bulk_upload.read().decode('UTF-8')
        io_string = io.StringIO(dataset)
        next(io_string)

        for column in csv.reader(io_string, delimiter=",", quotechar="|"):
            if int(column[3])==0:
                cost = int(InfrastructureType.objects.get(pk=column[1]).rate)
            else:
                cost = int(InfrastructureType.objects.get(pk=column[1]).rate) * int(column[3])

            created = Infrastructure.objects.update_or_create(
                infra_type=InfrastructureType.objects.get(pk=column[1]),
                company=company, 
                length=column[3],
                address=column[4],
                year_installed=column[5],
                cost=cost,
                created_by=request.user,
                is_existing = True,
                processed = False,
                referenceid = ref_id,
                upload_application_letter=column[6],
                upload_asBuilt_drawing=column[7]
                )
                
        messages.success(request, "Bulk upload successful")
    return redirect('agency_apply_for_exist', company.id)

@login_required
# @tax_payer_only
def agency_add_permit_ex_form(request, pk):
    print("ADDING EXISITING INFRASTRUCTURE FORM")
    if Permit.objects.all().exists(): 
        last = Permit.objects.latest("pk").id
        ref_id = "LA"+generate_ref_id() + str(last + 1).zfill(5)
    else:
        ref_id = "LA"+generate_ref_id() + "00001"

    company = User.objects.get(pk=pk)
    
    permits = Permit.objects.all()
    if request.method == "POST":
        form = PermitForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            permit = form.save(commit=False)
            permit.referenceid = ref_id
            permit.company = company
            permit.is_existing = True
            permit.save()
            permits = Permit.objects.all()
            context = {
                'permits': permits
            }

            return render(request, 'agency/pages/forms/permit_details.html', context)
        else:
            print("ERROR: ", form.errors)

    context = {
        'form':form,
        'referenceid': ref_id,
        'company': company
    }
    return render(request, 'agency/pages/forms/apply_permit_ex_form.html', context)


@login_required # Dispute Demand Notice - Issues
def edit_disputed_demand_notice(request, ref_id):
    if Remittance.objects.filter(referenceid=ref_id).exists():
        remit = Remittance.objects.get(referenceid=ref_id)
        form = RemittanceForm(instance=remit)
        print("REMITTANCE: ", remit.receipt)
    else:
        form = RemittanceForm()

    # print("REFID: ", ref_id)

    ref = Q(referenceid=ref_id)
    coy = Q(company=70)
    is_dis = Q(is_disputed = False)
    not_dis = Q(is_disputed = True)
    is_existing = Q(is_existing = True)
    permits = Permit.objects.filter(ref)
    company = permits.first().company.company_name
    referenceid = permits.first().referenceid
    # undisputed_permits = Permit.objects.filter(ref)

    # print("PERMITS: ", permits)

    if Remittance.objects.filter(Q(referenceid=ref_id) & Q(company=request.user)).exists():
        remittance = Remittance.objects.get(Q(referenceid=ref_id) & Q(company=request.user))
    else:
        remittance = 0
   
    context = {
        'ref_id': ref_id,
        'permits': permits,
        'company': company,
        'referenceid': referenceid,
        'remittance': remittance,
        'form': form
    }
    return render(request, 'agency/edit_demand_notice.html', context)

@login_required
def dispute_dn_edit(request, pk):
    permit = Permit.objects.get(pk=pk)
    form = PermitEditForm(instance = permit)
    print("Permit ID: ", permit.id)
    context = {
        'form': form,
        'permit_id':permit.id
    }
    return render(request, 'agency/apply_permit_edit_form.html', context)


@login_required
def update_dispute_dn_edit(request):
    ref_id = str(request.POST['referenceid'])
    # print("REF: ", ref_id)
    if request.htmx:
        perm = Permit.objects.get(pk=request.POST.get('permit_id'))
        # form = PermitEditForm(request.POST or None, request.FILES or None)
        form = PermitEditForm(request.POST or None, request.FILES or None, instance = perm)

        infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])
        # print("READY POST: ", infra_rate.rate, type(infra_rate.rate))
        # print("Permit type: ", request.POST['amount'], type(request.POST['amount']))
        if "mast" in infra_rate.infra_name.lower():
            infra_cost = infra_rate.rate * int(request.POST['amount'])
            len = 0
            qty = request.POST['amount']
        elif "roof" in infra_rate.infra_name.lower():
            infra_cost = infra_rate.rate * int(request.POST['amount'])
            len = 0
            qty = request.POST['amount']
        else:
            infra_cost = infra_rate.rate * int(request.POST['length'])
            qty = 0
            len = request.POST['length']

        print("AMOUNT OR NUMBER: ", infra_rate.infra_name.lower())
        year = str(request.POST['year']+"-01-01")
        installed_date = datetime.strptime(year, '%Y-%m-%d')

        if form.is_valid():
            # print("Form is valid")
            permit = form.save(commit=False)
            permit.referenceid = ref_id
            permit.company = perm.company
            permit.created_by = request.user.email
            permit.amount = qty
            permit.length = len
            permit.year_installed = installed_date
            permit.infra_cost = infra_cost
            permit.is_disputed = True
            permit.is_existing = False
            permit.save()

            context = {
                'form':form,
                'referenceid': ref_id,
                'company': request.user
            }
            return HttpResponseClientRedirect('/agency/companies/disputed/edit/'+permit.referenceid)
            # return render(request, 'tax-payers/partials/inc/added_permit', context)
        else:
            print("FILE FORMAT INVALID")
    form = PermitForm()

    context = {
        'form':form,
        'referenceid': ref_id,
        'company': request.user
    }
    return HttpResponseClientRedirect('/agency/companies/disputed/edit/'+permit.referenceid)


@login_required
def undispute_dn_receipt(request, ref_id):
    permits = Permit.objects.filter(referenceid = ref_id, is_disputed=True)
    # if not permits.first().company == request.user:
    #     return redirect('apply_for_permit')
    
    ref = permits.first()
    app_fee = AdminSetting.objects.get(slug="application-fee")
    site_assessment = AdminSetting.objects.get(slug="site-assessment")
    admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")

    mast_roof = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')))
    length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='Optic') | Q(infra_type__infra_name__icontains='Gas') | Q(infra_type__infra_name__icontains='Power') | Q(infra_type__infra_name__icontains='Pipeline')))
    #application number = number of masts and rooftops 
    if mast_roof.exists():
        mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
        mast_roof_no = mast_roof_no['no_sites']
    else:
        app_count = length.count()
        mast_roof_no = 0
    
    if length.exists():
        length = length.count()
    else:
        length = 0

    
    app_count = mast_roof_no + length
    total_app_fee = app_count * app_fee.rate

    # print("APPLICATION COUNT: ", app_count)

    tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True)).aggregate(no_sum = Sum('infra_cost'))
    # print("Tot Sum: ", tot_sum_infra)

    # Site assessment report rate
    sar_rate = mast_roof_no['no_sites'] * site_assessment.rate

    admin_pm_fees_sum = admin_pm_fees.rate * tot_sum_infra['no_sum'] / 100

    total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

    # ADD WAVER
    if Waiver.objects.filter(referenceid=ref).exists():
        waver = Waiver.objects.get(referenceid=ref).wave_amount
    else:
        waver = 0
    
    # print("WAVER: ", waver)
    total_liability = total_due - waver

    # Agency Details
    agency = Agency.objects.all().first()
    print("AGENCY: ", agency)
    

    context = {
        'permits': permits,
        'ref': ref,
        'site_assessment': site_assessment,
        'site_assess_count': mast_roof_no['no_sites'],
        'admin_pm_fees': admin_pm_fees,
        'app_fee': app_fee,
        'app_count': app_count,
        'total_app_fee': total_app_fee,
        'sar_rate': sar_rate,
        'tot_sum_infra': tot_sum_infra,
        'admin_pm_fees_sum': admin_pm_fees_sum,
        'total_due': total_due,
        'waver': waver,
        'total_liability': total_liability,
        'ref_id': ref_id,
        'agency': Agency.objects.all().first()
    }
    return render(request, 'agency/receipts/undisputed_receipt.html', context)



@login_required
def del_undisputed(request, pk):
    permit = Permit.objects.get(pk=pk)
    permit.delete()
    print("DELETE NEW WORKING....: ")

    return HttpResponseClientRedirect('/agency/companies/disputed/edit/'+permit.referenceid)

# @login_required
# def accept_undisputed_edit(request, pk):
#     permit = Permit.objects.get(pk=pk)
#     print("PERMIT: ", permit)
#     # permit.company= company,
#     # permit.referenceid= referenceid,
#     # permit.infra_type= infra_type,
#     # permit.amount= amount,
#     # permit.length= length,
#     # permit.add_from= add_from,
#     # permit.add_to= add_to,
#     # permit.year_installed= str(permit.year_installed), 
#     # permit.age= age,
#     # permit.upload_application_letter= upload_application_letter,
#     # permit.upload_asBuilt_drawing= upload_asBuilt_drawing,
#     # permit.upload_payment_receipt= upload_payment_receipt,
#     # permit.status= status,
#     # permit.is_disputed= True,
#     # permit.is_undisputed= is_undisputed,
#     # permit.is_revised= is_revised,
#     # permit.is_paid= is_paid,
#     # permit.is_existing= False
#     # pm = Permit.objects.create(
#     #     company= permit.company,
#     #     referenceid= permit.referenceid,
#     #     infra_type= permit.infra_type,
#     #     amount= permit.amount,
#     #     length= permit.length,
#     #     add_from= permit.add_from,
#     #     add_to= permit.add_to,
#     #     year_installed= str(permit.year_installed), 
#     #     age= permit.age,
#     #     upload_application_letter= permit.upload_application_letter,
#     #     upload_asBuilt_drawing= permit.upload_asBuilt_drawing,
#     #     upload_payment_receipt= permit.upload_payment_receipt,
#     #     status= permit.status,
#     #     is_disputed= True,
#     #     is_undisputed= permit.is_undisputed,
#     #     is_revised= permit.is_revised,
#     #     is_paid= permit.is_paid,
#     #     is_existing= False
#     # )
#     # context = {
#     #     pm:pm
#     # } 
#     # print("ACCEPTED DN: .....", pm)
#     return redirect('dispute-demand-notice', permit.referenceid)



@login_required 
def agency_add_permit_form(request, ref_id):
    
    permits = Permit.objects.all()
    if request.method == "POST":
        company = Permit.objects.filter(referenceid=ref_id).first().company
        form = PermitForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            permit = form.save(commit=False)
            permit.referenceid = ref_id
            permit.company = company
            permit.save()
            permits = Permit.objects.all()
            context = {
                'permits': permits
            }

            print("USER ID: ", permits)
            return render(request, 'agency/partials/permit_details.html', context)
        else:
            print("ERROR: ", form.errors)

    context = {
        'form':form,
        'referenceid': ref_id,
        'company': request.user
    }
    return render(request, 'agency/partials/apply_permit_form.html', context)


@login_required
def add_dispute_dn(request):
    ref_id = str(request.POST['referenceid'])
    print("REF: ", ref_id)
    if request.htmx:
        form = PermitEditForm(request.POST or None, request.FILES or None)

        infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])
        # print("READY POST: ", infra_rate.rate, type(infra_rate.rate))
        # print("Permit type: ", request.POST['amount'], type(request.POST['amount']))
        if "mast" in infra_rate.infra_name.lower():
            infra_cost = infra_rate.rate * int(request.POST['amount'])
            len = 0
            qty = request.POST['amount']
        elif "roof" in infra_rate.infra_name.lower():
            infra_cost = infra_rate.rate * int(request.POST['amount'])
            len = 0
            qty = request.POST['amount']
        else:
            infra_cost = infra_rate.rate * int(request.POST['length'])
            qty = 0
            len = request.POST['length']

        print("AMOUNT OR NUMBER: ", infra_rate.infra_name.lower())

        if form.is_valid():
            # print("Form is valid")
            permit = form.save(commit=False)
            permit.referenceid = ref_id
            permit.company = request.user
            permit.amount = qty
            permit.length = len
            permit.year_installed = str(datetime.now().date())
            permit.infra_cost = infra_cost
            permit.is_disputed = True
            permit.is_existing = False
            permit.save()

            context = {
                'form':form,
                'referenceid': permit.referenceid,
                'company': request.user
            }
            return HttpResponseClientRedirect('/agency/companies/dn/edit/'+permit.referenceid)
            # return render(request, 'tax-payers/partials/inc/added_permit', context)
        else:
            print("FILE FORMAT INVALID")
    form = PermitForm()

    context = {
        'form':form,
        'referenceid': ref_id,
        'ref_id': ref_id,
        'company': request.user
    }
    return HttpResponseClientRedirect('/agency/companies/dn/edit/'+permit.referenceid)

@login_required
def agency_add_undispute_edit(request):
    ref_id = request.POST['referenceid']
    if request.method == 'POST':
        form = PermitEditForm(request.POST or None, request.FILES or None)

        infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])
        
        if "mast" in infra_rate.infra_name.lower():
            infra_cost = infra_rate.rate * int(request.POST['amount'])
            len = 0
            qty = request.POST['amount']
        elif "roof" in infra_rate.infra_name.lower():
            infra_cost = infra_rate.rate * int(request.POST['amount'])
            len = 0
            qty = request.POST['amount']
        else:
            infra_cost = infra_rate.rate * int(request.POST['length'])
            qty = 0
            len = request.POST['length']

        print("REFERENCE ID: ", ref_id)
        year = str(request.POST['year']+"-01-01")
        installed_date = datetime.strptime(year, '%Y-%m-%d')
        company = Permit.objects.filter(referenceid=ref_id).first().company
        print("COMPANY: ", company)

        if form.is_valid():
            # print("Form is valid")
            permit = form.save(commit=False)
            permit.referenceid = ref_id
            permit.company = company
            permit.amount = qty
            permit.year_installed = installed_date
            permit.length = len
            permit.infra_cost = infra_cost
            permit.created_by = request.user
            permit.is_disputed = True
            permit.save()

            context = {
                'form':form,
                # 'referenceid': ref_id,
                'company': request.user
            }
            return HttpResponseClientRedirect('/agency/companies/disputed/edit/'+permit.referenceid)

        else:
            print("FILE FORMAT INVALID")
    form = PermitForm()

    context = {
        'form':form
        # 'referenceid': ref_id,
        # 'company': request.user
    }
    return HttpResponseClientRedirect('/agency/companies/disputed/edit/'+ref_id)


@login_required
def waiver_requests(request):
    remittance = Remittance.objects.all()
    waiver = Waiver.objects.all()
    # print(remmittance)
    context = {
        'remittance': remittance,
        'waiver': waiver
    }
    return render(request, 'agency/waiver-requests.html', context)





# @login_required
# # @tax_payer_only
# def undispute_dn_receipt(request, ref_id):
#     permits = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_existing=True))
#     if not permits.exists():
#         return redirect('apply_existing_infra')

#     if not permits.first().company == request.user:
#         return redirect('apply_existing_infra')
#     # Update is_disputed
#     permits = permits.update(is_disputed = True)
#     permits = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed = True) & Q(is_existing=True))

#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")
#     penalty = AdminSetting.objects.get(slug="penalty")

#     mast_roof = Permit.objects.filter((Q(referenceid = ref_id) & Q(is_disputed=True) & Q(is_existing=True)) & (Q(infra_type__infra_name__istartswith='Mast') | Q(infra_type__infra_name__istartswith='Roof')))
    
#     length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & Q(is_existing=True) & (Q(infra_type__infra_name__istartswith='Optic') | Q(infra_type__infra_name__istartswith='Gas') | Q(infra_type__infra_name__istartswith='Power') | Q(infra_type__infra_name__istartswith='Pipeline')))
#     #application number = number of masts and rooftops 

#     if Remittance.objects.filter(Q(referenceid=ref_id) & Q(company=request.user)).exists():
#         remittance = Remittance.objects.get(Q(referenceid=ref_id) & Q(company=request.user))
#         remittance = remittance.remitted_amount
#     else:
#         remittance = 0

#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))['no_sites']
#     else:
#         mast_roof_no = 0
#         # mast_roof_no['no_sites'] = 0

#     print("MAST & ROOF NO: ", mast_roof_no)
#     if length.exists():
#         len_count = length.count()
#     else:
#         len_count = 0

#     app_count = mast_roof_no + len_count
#     total_app_fee = app_count * app_fee.rate

#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & Q(is_existing=True)).aggregate(no_sum = Sum('infra_cost'))
#     # tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_existing=True)).aggregate(no_sum = Sum('infra_cost'))
    
#     print("INFRA COST: ", tot_sum_infra)
#     # Site assessment report rate
#     sar_rate = mast_roof_no * site_assessment.rate
#     print("SUM: ", tot_sum_infra['no_sum'], type(tot_sum_infra['no_sum']))


#     admin_pm_fees_sum = (admin_pm_fees.rate * tot_sum_infra['no_sum']) / 100

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     print("TOTAL DUE: ", total_due, type(total_due))
#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref).exists():
#         waver = Waiver.objects.get(referenceid=ref).wave_amount
#     else:
#         waver = 0
#     # PENALTY CALCULATION
#     refid = Q(referenceid = ref_id)
#     is_exist = Q(is_existing=True)
#     is_dispute = Q(is_disputed=True)
#     # current_user = Q(comapny = request.user)
#     if Permit.objects.filter(refid & is_exist).exists():
#         age_sum = Permit.objects.filter(refid & is_exist & is_dispute).aggregate(ages = Sum('age'))['ages']
#     else:
#         age_sum = 0

#     print("AGE Calculated: ", age_sum)
    
#     penalty_sum = age_sum * penalty.rate
#     print("PENALTY Calculated: ", penalty_sum)

#     print("REMITTANCE: ", remittance)

    
#     # Remove penalty from the total calculation after dispute
#     total_liability = total_due  - remittance - waver
    

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
#         'penalty_sum': penalty_sum,
#         'penalty': penalty,
#         'remittance': remittance,
#         'age_sum': age_sum,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'tax-payers/receipts/undisputed_ex_dn_receipt.html', context)
