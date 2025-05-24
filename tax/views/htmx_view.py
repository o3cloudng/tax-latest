from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tax.models import InfrastructureType
from tax.forms import InfrastructureForm, InfrastructureForm2
from django_htmx.http import HttpResponseClientRedirect
from datetime import datetime
from django.contrib import messages
from tax.models import Infrastructure, DemandNotice
from django.db.models import Q


@login_required
def search_tax_dashboard(request):
    search = request.POST.get('search')
    all_demand_notices = DemandNotice.objects.filter(company=request.user)
    if search:
        demand_notices = all_demand_notices.filter(Q(referenceid__icontains=search))
    else:
        demand_notices = all_demand_notices.all()[:20]
    context = {
        "search": search,
        "demand_notices": demand_notices
    }
    return render(request, "tax-payers/partials/search/search-result-dn.html", context)


@login_required
def search_tax_infrastructure(request):
    search = request.POST.get('search')
    all_infrastructures = Infrastructure.objects.filter(company=request.user)
    if search:
        infrastructures = all_infrastructures.filter(Q(referenceid__icontains=search))
    else:
        infrastructures = all_infrastructures.all()[:20]
    context = {
        "search": search,
        "infrastructures": infrastructures
    }
    return render(request, "tax-payers/partials/search/search-result-dn.html", context)


@login_required
def search_tax_dn(request):
    search = request.POST.get('search')
    all_demand_notices = DemandNotice.objects.all()
    if search:
        demand_notices = all_demand_notices.filter(Q(referenceid__icontains=search))
    else:
        demand_notices = all_demand_notices.all()[:20]
    context = {
        "search": search,
        "all": demand_notices
    }
    return render(request, "tax-payers/partials/search/search-result-dn.html", context)

@login_required
def add_infrastructure_form(request):
    current_year = datetime.now().year
    infrastructure = InfrastructureType.objects.get(pk=request.GET.get('infrastructure'))

    if ('Mast' in infrastructure.infra_name) | ('Roof' in infrastructure.infra_name):
        context = {
            'infrastructure':infrastructure,
            'current_year': current_year
        }
        return render(request, 'tax-payers/partials/infrastructureform.html', context)
    else:
        context = {
            'current_year': current_year,
            'infrastructure':infrastructure
        }
        return render(request, 'tax-payers/partials/infrastructureform2.html', context)

@login_required
def add_ex_infrastructure_form(request):
    current_year = []
    for year in range(int(datetime.now().year), 2001, -1):
        current_year.append(year)
    infrastructure = InfrastructureType.objects.get(pk=request.GET.get('infrastructure'))

    if ('Mast' in infrastructure.infra_name) | ('Roof' in infrastructure.infra_name):
        context = {
            'infrastructure':infrastructure,
            'current_year': current_year
        }
        return render(request, 'tax-payers/partials/ex/infrastructureform.html', context)
    else:
        context = {
            'current_year': current_year,
            'infrastructure':infrastructure
        }
        return render(request, 'tax-payers/partials/ex/infrastructureform2.html', context)


@login_required
def add_infrastructure(request):
    if request.method == 'POST':
        if not request.POST['year_installed']:
            year_installed = int(datetime.now().year)
            # print(year_installed, type(year_installed))
            # print(request.POST['year_installed'], type(request.POST['year_installed']))
        else:
            year_installed = request.POST['year_installed']

        infra_type = InfrastructureType.objects.get(pk=request.POST['infra_type'])

        if (('Mast' in infra_type.infra_name) | ('Roof' in infra_type.infra_name)):
            cost = infra_type.rate
        else:
            cost = request.POST['length'] * infra_type.rate

        form = InfrastructureForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.company = request.user
            form.created_by = request.user
            form.year_installed = year_installed
            form.cost = cost
            form.save()
            messages.success(request, f"{form.infra_type} added successfully")
        else:
            # print(form.errors)
            messages.error(request, f"{form.errors}")
    context = {
        'infrastructure': InfrastructureType.objects.all().first(),
    }
    return HttpResponseClientRedirect('/tax/apply/permit/', context)


@login_required
def add_infrastructure2(request):
    if request.method == 'POST':

        if not request.POST['year_installed']:
            year_installed = datetime.now().year
        else:
            year_installed = request.POST['year_installed']

        if request.POST['addfrom']:
            address = request.POST['addfrom']+" - "+request.POST['addto']

        infra_type = InfrastructureType.objects.get(pk=request.POST['infra_type'])

        if (('Mast' in infra_type.infra_name) | ('Roof' in infra_type.infra_name)):
            cost = infra_type.rate
        else:
            cost = int(request.POST['length']) * int(infra_type.rate)

        form = InfrastructureForm2(request.POST or None, request.FILES or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.company = request.user
            form.created_by = request.user
            form.year_installed = year_installed
            form.address = address
            form.cost = cost
            form.save()
            messages.success(request, f"{form.infra_type} added successfully")
        
    context = {
        'infrastructure': InfrastructureType.objects.all().first(),
    }
    return HttpResponseClientRedirect('/tax/apply/permit/', context)

@login_required
def add_ex_infrastructure(request):
    if request.method == 'POST':
        if not request.POST['year_installed']:
            year_installed = int(datetime.now().year)
            # print(year_installed, type(year_installed))
            # print(request.POST['year_installed'], type(request.POST['year_installed']))
        else:
            year_installed = request.POST['year_installed']

        infra_type = InfrastructureType.objects.get(pk=request.POST['infra_type'])

        if (('Mast' in infra_type.infra_name) | ('Roof' in infra_type.infra_name)):
            cost = infra_type.rate
        else:
            cost = request.POST['length'] * infra_type.rate

        form = InfrastructureForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.company = request.user
            form.created_by = request.user
            form.year_installed = year_installed
            form.cost = cost
            form.is_existing = True
            form.save()
            messages.success(request, f"{form.infra_type} added successfully")
        else:
            messages.error(request, f"{form.errors}")
    context = {
        'infrastructure': InfrastructureType.objects.all().first(),
    }
    return HttpResponseClientRedirect('/tax/apply/permit/exist/', context)


@login_required
def add_ex_infrastructure2(request):
    if request.method == 'POST':

        if not request.POST['year_installed']:
            year_installed = datetime.now().year
        else:
            year_installed = request.POST['year_installed']

        if request.POST['addfrom']:
            address = request.POST['addfrom']+" - "+request.POST['addto']

        infra_type = InfrastructureType.objects.get(pk=request.POST['infra_type'])

        if (('Mast' in infra_type.infra_name) | ('Roof' in infra_type.infra_name)):
            cost = infra_type.rate
        else:
            cost = int(request.POST['length']) * int(infra_type.rate)

        form = InfrastructureForm2(request.POST or None, request.FILES or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.company = request.user
            form.created_by = request.user
            form.year_installed = year_installed
            form.address = address
            form.cost = cost
            form.is_existing = True
            form.save()
            messages.success(request, f"{form.infra_type} added successfully")
        else:
            messages.error(request, f"{form.errors}")
    context = {
        'infrastructure': InfrastructureType.objects.all().first(),
    }
    return HttpResponseClientRedirect('/tax/apply/permit/exist/', context)