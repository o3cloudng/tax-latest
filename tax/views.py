from django.shortcuts import render
from tax.forms import PermitForm
from django.contrib.auth.decorators import login_required
from account.models import User
from .models import Permit
from datetime import date
from django.http import HttpResponseRedirect
from django.urls import reverse




def generate_ref_id():
    today = date.today()
    year = str(today.year)
    month = str(today.month).zfill(2)
    return year+month

@login_required
def apply_for_permit(request):
    print("GETTING HERE.......")
    if Permit.objects.all().exists(): 
        last = Permit.objects.latest("pk").id
        ref_id = "LA"+generate_ref_id() + str(last + 1).zfill(5)
        # print("No Ref: ", ref_id)
    else:
        ref_id = generate_ref_id() + "00001"
        # print("No Ref here: ", ref_id)

    if request.method == "POST":
        form = PermitForm(request.POST, request.FILES)

        if form.is_valid():
            print("Form is valid")
            permit = form.save(commit=False)
            permit.referenceid = ref_id
            permit.company = request.user
            permit.save()
            # context = {
            #     'referenceid': ref_id
            # }
            return HttpResponseRedirect(reverse('payment-receipt', ref_id))
            # return render(request, "tax-payers/payment-receipt.html", context)
        
        else:
            print("FILE FORMAT INVALID")
    form = PermitForm()

    context = {
        'form':form,
        'referenceid': ref_id,
        'company': request.user
    }

    return render(request, 'tax-payers/apply_for_permit.html', context)

@login_required
def demand_notice(request):
    user = User.objects.get(id=request.user.id)
    context = {
        "user": user
    }
    return render(request, 'tax-payers/demand_notice.html', context)

@login_required
def add_permit_form(request):
    
    permits = Permit.objects.all()
    if request.method == "POST":
        form = PermitForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            permit = form.save(commit=False)
            # permit.referenceid = ref_id
            permit.referenceid = request.user
            permit.save()
            permits = Permit.objects.all()
            context = {
                'permits': permits
            }

            print("USER ID: ", permits)
            return render(request, 'tax-payers/partials/permit_details.html', context)
        else:
            print("ERROR: ", form.errors)

    context = {
        'form':form,
        # 'referenceid': ref_id,
        'company': request.user
    }
    return render(request, 'tax-payers/partials/apply_permit_form.html', context)


@login_required
def dashboard(request):
    user = User.objects.get(id = request.user.id)
    if user.is_profile_complete:
        context = {
            "is_profile_complete" : True,
            "user":user
        }
    context = {
         "is_profile_complete" : False
    }
    return render(request, 'tax-payers/dashboard.html', context)


@login_required
def disputes(request):
    user = User.objects.get(id = request.user.id)
    context = {
        "user":user
    }
    return render(request, 'tax-payers/disputes.html', context)


def infrastructures(request):
    context = {}
    return render(request, 'tax-payers/infrastructure.html', context)


def downloads(request):
    context = {}
    return render(request, 'tax-payers/downloads.html', context)


def admin_settings(request):
    context = {}
    return render(request, 'tax-payers/admin-settings.html', context)


def resources(request):
    context = {}
    return render(request, 'tax-payers/resources.html', context)


def upload_existing_facilities(request):
    context = {}
    return render(request, 'tax-payers/upload-existing-facility.html', context)


def payment_receipt(request, ref_id):
    permits = Permit.objects.filter(referenceid = ref_id)
    # print("REF ID: ", permit.reference)
    ref = permits.first()
    print("REF: ", ref.referenceid)
    context = {
        'permits': permits,
        'ref': ref
    }
    return render(request, 'tax-payers/undisputed-receipt.html', context)


def template(request):
    context = {}
    return render(request, 'tax-payers/template.html', context)
