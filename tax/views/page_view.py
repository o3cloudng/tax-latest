from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import User
from tax.models import DemandNotice, Infrastructure
from django.db.models import (Q, Count, Sum, Max, Func)
from core.decorator import tax_payer_only
from django.http import HttpResponseNotFound
# from agency.penalty_calculation import penalty_calculation

def handler404(request, exception=None):
    return render(request, '404.html', {}, status=404)

# Ensure to use the appropriate database function for date difference
class DateDiff(Func):
    function = 'DATEDIFF'
    template = '%(function)s(%(expressions)s)'

@login_required
# @tax_payer_only
def dashboard(request):
    # user = User.objects.get(id = request.user.id)
    all = DemandNotice.objects.filter(company=request.user).order_by('-updated_at')

    demand_notices = all.all()
    undisputed_unpaid = all.filter(status='UNDISPUTED UNPAID')
    undisputed_paid = all.filter(status='UNDISPUTED PAID')
    undisputed = all.filter(Q(status__icontains='UNDISPUTED'))
    revised = all.filter(status__icontains='REVISED')
    resolved = all.filter(status='RESOLVED')
    demand_notice = all.filter(status__icontains='DEMAND NOTICE')
    disputed = all.filter(status__icontains='UNDISPUTED')

    # print(demand_notice.count())    
    context = {
         "is_profile_complete" : False,
         "demand_notices": demand_notices,
         "undisputed_unpaid": undisputed_unpaid,
         "undisputed_paid": undisputed_paid,
         "disputed": undisputed,
         "revised": revised,
         "resolved": resolved,
         "disputed": disputed,
         "demand_notice": demand_notice,
    }
    return render(request, 'tax-payers/dashboard.html', context)


@login_required
# @tax_payer_only
def demand_notice(request):
    all = DemandNotice.objects.filter(company=request.user).order_by('-updated_at')
    demand_notices = all.all()
    undisputed_unpaid = all.filter(Q(status__icontains='UNDISPUTED UNPAID'))
    undisputed_paid = all.filter(Q(status__icontains='UNDISPUTED PAID'))
    # undisputed = all.filter(Q(status='UNDISPUTED UNPAID') | Q(status='UNDISPUTED UNPAID'))
    revised = all.filter(Q(status__icontains='REVISED'))
    resolved = all.filter(Q(status__icontains='RESOLVED'))
    demand_notice = all.filter(Q(status__icontains='DEMAND NOTICE'))
    disputed = all.filter(Q(status__icontains='UNDISPUTED'))

    total_demand_notices = demand_notices.aggregate(total = Sum('amount_paid'))['total']
    total_undisputed_paid = undisputed_paid.aggregate(total = Sum('amount_paid'))['total']
    total_undisputed_unpaid = undisputed_unpaid.aggregate(total = Sum('total_due'))['total']
    total_revised = revised.aggregate(total = Sum('amount_paid'))['total']
    total_resolved = resolved.aggregate(total = Sum('amount_paid'))['total']
    # print("TOTAL: ", total_demand_notices)

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
        "disputed": disputed,
        "demand_notice": demand_notice,
        "undisputed_unpaid": undisputed_unpaid,
        "revised": revised,
        "resolved": resolved,
    }
    return render(request, 'tax-payers/demand_notices.html', context)

@login_required
@tax_payer_only
def infrastructures(request):
    # Infrastructure should appear for only paid
    all = Infrastructure.objects.select_related('infra_type').\
        filter(Q(company=request.user) & Q(processed=True)).order_by('-updated_at')
    # all = all.values('infra_type__infra_name', 'cost')\
    #     .annotate(num = Count('infra_type'), dt = Max('created_at'))\
    #         .order_by('infra_type')
    # all = Infrastructure.objects.select_related('infra_type').filter(company=request.user)
    masts = all.filter(infra_type__infra_name__icontains='mast')
    masts_count = masts.count()

    roof = all.filter(infra_type__infra_name__icontains='roof')
    roof_count = roof.count()

    fibre = all.filter(infra_type__infra_name__icontains='fibre')
    pipe = all.filter(infra_type__infra_name__icontains='pipe')
    gas = all.filter(Q(infra_type__infra_name__icontains='gas') | \
                     Q(infra_type__infra_name__icontains='line'))
    others = all.filter(~Q(infra_type__infra_name__icontains='mast') & \
                        ~Q(infra_type__infra_name__icontains='roof') & \
                            ~Q(infra_type__infra_name__icontains='fibre'))
    context = {
        "infrastructures": infrastructures,
         "masts": masts,
         "masts_count": masts_count,
         "roof": roof,
         "roof_count": roof_count,
         "others": others,
         "fibre": fibre,
        "pipe": pipe,
        "gas": gas
    }
    return render(request, 'tax-payers/infrastructure.html', context)


@login_required
@tax_payer_only
def disputes(request):
    all = DemandNotice.objects.filter(Q(company=request.user) & Q(status="DISPUTED")).order_by('-updated_at')
    dispute_notices = all.all()
    dispute_notices_paid = all.filter(Q(status='PAID'))
    dispute_notices_unpaid = all.filter(Q(status='UNPAID'))
    dispute_notices_disputed = all.filter(Q(status='DISPUTED'))
    dispute_notices_resolved = all.filter(Q(status='RESOLVED'))
    
    context = {
         "is_profile_complete" : False,
         "dispute_notices": dispute_notices,
         "dispute_notices_paid": dispute_notices_paid,
         "dispute_notices_unpaid": dispute_notices_unpaid,
        "dispute_notices_disputed": dispute_notices_disputed,
        "dispute_notices_resolved": dispute_notices_resolved,
    }
    return render(request, 'tax-payers/disputes.html', context)

@login_required
@tax_payer_only
def downloads(request):
    files = DemandNotice.objects.filter(company=request.user)
    # for file in files:
        # print("File Here", file.referenceid)
        # print("File Here", file.upload_application_letter)
        # print("File Here", file.infra_type)

    context = {
        "files": files
    }
    return render(request, 'tax-payers/downloads.html', context)



@login_required
@tax_payer_only
def resources(request):
    context = {}
    return render(request, 'tax-payers/downloads.html', context)


