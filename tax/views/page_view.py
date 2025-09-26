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
@tax_payer_only
def dashboard(request):
    # user = User.objects.get(id = request.user.id)
    all_notices = DemandNotice.objects.filter(company=request.user).order_by('-updated_at')

    # Prefetch all needed statuses in a single query
    notices_by_status = {
        notice.status.upper(): notice
        for notice in all_notices
    }

    # Use list comprehensions to filter by status in memory
    demand_notices = all_notices
    zero = []
    undisputed_unpaid = [n for n in all_notices if n.status.upper() == 'UNDISPUTED UNPAID']
    undisputed_paid = [n for n in all_notices if n.status.upper() == 'UNDISPUTED PAID']
    revised = [n for n in all_notices if 'REVISED' in n.status.upper()]
    resolved = [n for n in all_notices if n.status.upper() == 'RESOLVED']
    demand_notice = [n for n in all_notices if 'DEMAND NOTICE' in n.status.upper()]
    disputed = [n for n in all_notices if 'DISPUTED' in n.status.upper()]

    context = {
        "is_profile_complete": False,
        "demand_notices": demand_notices,
        "undisputed_unpaid": undisputed_unpaid,
        "undisputed_paid": undisputed_paid,
        "disputed": disputed,
        "revised": revised,
        "resolved": resolved,
        "demand_notice": demand_notice,
    }
    return render(request, 'tax-payers/dashboard.html', context)


@login_required
@tax_payer_only
def demand_notice(request):
    all_notices = list(DemandNotice.objects.filter(company=request.user).order_by('-updated_at'))

    # Use list comprehensions to filter by status in memory
    undisputed_unpaid = [n for n in all_notices if n.status.upper() == 'UNDISPUTED UNPAID']
    undisputed_paid = [n for n in all_notices if n.status.upper() == 'UNDISPUTED PAID']
    revised = [n for n in all_notices if 'REVISED' in n.status.upper()]
    resolved = [n for n in all_notices if n.status.upper() == 'RESOLVED']
    demand_notice = [n for n in all_notices if 'DEMAND NOTICE' in n.status.upper()]
    disputed = [n for n in all_notices if 'DISPUTED' in n.status.upper()]

    # Aggregate sums using generator expressions
    total_demand_notices = sum(n.amount_paid or 0 for n in all_notices)
    total_undisputed_paid = sum(n.amount_paid or 0 for n in undisputed_paid)
    total_undisputed_unpaid = sum(getattr(n, 'total_due', 0) or 0 for n in undisputed_unpaid)
    total_revised = sum(n.amount_paid or 0 for n in revised)
    total_resolved = sum(n.amount_paid or 0 for n in resolved)

    context = {
        "is_profile_complete": False,
        "demand_notices": all_notices,
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
    infrastructures = list(
        Infrastructure.objects.select_related('infra_type')
        .filter(company=request.user)
        .order_by('-created_at')
    )

    # Categorize infrastructures using list comprehensions
    masts = [i for i in infrastructures if 'mast' in i.infra_type.infra_name.lower()]
    roof = [i for i in infrastructures if 'roof' in i.infra_type.infra_name.lower()]
    fibre = [i for i in infrastructures if 'fibre' in i.infra_type.infra_name.lower()]
    pipe = [i for i in infrastructures if 'pipe' in i.infra_type.infra_name.lower()]
    gas_powerline = [
        i for i in infrastructures
        if 'gas' in i.infra_type.infra_name.lower() or 'line' in i.infra_type.infra_name.lower()
    ]
    others = [
        i for i in infrastructures
        if all(x not in i.infra_type.infra_name.lower() for x in ['mast', 'roof', 'fibre'])
    ]

    context = {
        "infrastructures": infrastructures,
        "masts": masts,
        "masts_count": len(masts),
        "roof": roof,
        "roof_count": len(roof),
        "others": others,
        "fibre": fibre,
        "pipe": pipe,
        "gas_powerline": gas_powerline,
    }
    return render(request, 'tax-payers/infrastructure.html', context)


@login_required
@tax_payer_only
def disputes(request):
    dispute_notices = list(DemandNotice.objects.filter(company=request.user, status__icontains="DISPUTED").order_by('-updated_at'))
    dispute_notices_paid = [n for n in dispute_notices if n.status.upper() == 'PAID']
    dispute_notices_unpaid = [n for n in dispute_notices if n.status.upper() == 'UNPAID']
    dispute_notices_disputed = [n for n in dispute_notices if n.status.upper() == 'DISPUTED']
    dispute_notices_resolved = [n for n in dispute_notices if n.status.upper() == 'RESOLVED']

    context = {
        "is_profile_complete": False,
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
    context = {
        "pdf_urls":Infrastructure.objects.filter(company=request.user).distinct()
    }
    return render(request, 'tax-payers/downloads.html', context)



@login_required
@tax_payer_only
def resources(request):
    context = {}
    return render(request, 'tax-payers/downloads.html', context)


