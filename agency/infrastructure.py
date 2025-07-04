from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tax.models import InfrastructureType
from tax.forms import InfrastructureForm, InfrastructureForm2
from django_htmx.http import HttpResponseClientRedirect
from datetime import datetime
from django.contrib import messages
from tax.models import Infrastructure, DemandNotice
from django.db.models import Q
# from tax.views.existing_infra_view import generate_ref_id
from account.models import User



@login_required
def agency_apply_for_permit(request, pk):

    company = User.objects.get(pk=pk)

    form = InfrastructureForm()
    
    # total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra = agency_total_due(company, False)
  
    current_year = datetime.now().year
    infrastructures= Infrastructure.objects\
        .filter(Q(is_existing = False) & Q(processed = False) \
            & Q(company=company)).order_by('-created_at')

    context = {
        'form':form,
        'infra': 'Mast',
        'company': request.user,
        'current_year': current_year,
        'infrastructures': infrastructures,
        'infrastructure': InfrastructureType.objects.all().first(),
        'infra_form': InfrastructureForm(),
        'infra_form2': InfrastructureForm2(),
        # 'referenceid':  generate_ref_id(),
        'company': company,
        'userid': company.id,
        'infra_types': InfrastructureType.objects.all().order_by('pk')

    }

    return render(request, 'agency/pages/forms/apply_for_permit.html', context)


@login_required
def agency_add_infrastructure_form(request):
    current_year = datetime.now().year
    infrastructure = InfrastructureType.objects.get(pk=request.GET.get('infrastructure'))
    userid = User.objects.get(pk=request.GET['userid'])

    if ('Mast' in infrastructure.infra_name) | ('Roof' in infrastructure.infra_name):
        context = {
            'infrastructure':infrastructure,
            'userid': userid.id,
            'current_year': current_year
        }
        return render(request, 'agency/pages/forms/infrastructureform.html', context)
    else:
        context = {
            'current_year': current_year,
            'userid': userid.id,
            'infrastructure':infrastructure
        }
        return render(request, 'agency/pages/forms/infrastructureform2.html', context)


@login_required
def add_infrastructure(request):
    if request.method == 'POST':
        company = User.objects.get(pk=request.POST['company'])

        if not request.POST['year_installed']:
            year_installed = int(datetime.now().year)
        else:
            year_installed = request.POST['year_installed']

        infra_type = InfrastructureType.objects.get(pk=request.POST['infra_type'])

        if (('Mast' in infra_type.infra_name) | ('Roof' in infra_type.infra_name)):
            cost = infra_type.rate
        else:
            cost = int(request.POST['length']) * int(infra_type.rate)

        form = InfrastructureForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.company = company
            form.created_by = request.user
            form.year_installed = year_installed
            form.cost = cost
            form.save()
            messages.success(request, f"{form.infra_type} added successfully")
        else:
            messages.error(request, f"{form.errors}")
    context = {
        'infrastructure': InfrastructureType.objects.all().first(),
    }
    return HttpResponseClientRedirect('/agency/infrastructure/add/'+str(company.id), context)


@login_required
def add_infrastructure2(request):
    if request.method == 'POST':
        company = User.objects.get(pk=request.POST['company'])

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
            form.company = company
            form.created_by = request.user
            form.year_installed = year_installed
            form.address = address
            form.cost = cost
            form.save()
            messages.success(request, f"{form.infra_type} added successfully")
    context = {
        'infrastructure': InfrastructureType.objects.all().first(),
    }
    return HttpResponseClientRedirect('/agency/infrastructure/add/'+str(company.id), context)

def agency_add_ex_infrastructure_form(request):
    current_year = []
    for year in range(int(datetime.now().year), 2001, -1):
        current_year.append(year)
    infrastructure = InfrastructureType.objects.get(pk=request.GET.get('infrastructure'))
    userid = User.objects.get(pk=request.GET['userid'])

    if ('Mast' in infrastructure.infra_name) | ('Roof' in infrastructure.infra_name):
        context = {
            'infrastructure':infrastructure,
            'userid': userid.id,
            'current_year': current_year
        }
        return render(request, 'agency/pages/forms/ex/infrastructureform.html', context)
    else:
        context = {
            'current_year': current_year,
            'userid': userid.id,
            'infrastructure':infrastructure
        }
        return render(request, 'agency/pages/forms/ex/infrastructureform2.html', context)



@login_required
def add_ex_infrastructure(request):
    company = User.objects.get(pk=request.POST['company'])
    if request.method == 'POST':
        if not request.POST['year_installed']:
            year_installed = int(datetime.now().year)
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
            form.company = company
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
    return HttpResponseClientRedirect('/agency/infrastructure/ex/'+str(company.id), context)


@login_required
def add_ex_infrastructure2(request):
    company = User.objects.get(pk=request.POST['company'])
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
            form.company = company
            form.created_by = request.user
            form.year_installed = year_installed
            form.address = address
            form.cost = cost
            form.is_existing = True
            form.save()
            messages.success(request, f"{form.infra_type} added successfully")
        else:
            # print(form.errors)
            messages.error(request, f"{form.errors}")
    context = {
        'infrastructure': InfrastructureType.objects.all().first(),
    }
    return HttpResponseClientRedirect('/agency/infrastructure/ex/'+str(company.id), context)