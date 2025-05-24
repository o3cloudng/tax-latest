from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tax.models import Infrastructure, DemandNotice, InfrastructureType
from account.models import AdminSetting, Sector
from django.db.models import Q
from account.models import User
from django_htmx.http import HttpResponseClientRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from agency.forms import InfrastructureSettingsForm
from django.http import HttpResponse

# Validation for InfratructureType Settings
def InfraTypeValidation(request):
    infra_name = request.GET.get('infra_name')
    if InfrastructureType.objects.filter(infra_name__iexact=infra_name.strip()).exists():
        return HttpResponse(f'<i>"{infra_name}" already exists</i>')
    else:
        return HttpResponse("")

def RateValidation(request):
    rate = request.GET.get('rate')
    rate = rate.replace(",","").replace(".","")
    if not rate.isnumeric():
        return HttpResponse(f'<i>"{rate}" must be numbers</i>')
    else:
        return HttpResponse("")
    
# REVENUE VALIDATION
def RevenueNameValidation(request):
    name = request.GET.get('name')
    name = name.replace(" ","-")
    if AdminSetting.objects.filter(slug__iexact=name).exists():
        return HttpResponse(f'<i>"{name}" already exists</i>')
    else:
        return HttpResponse("")
    
def RevenueRateValidation(request):
    rate = request.GET.get('rate')
    rate = rate.replace(",","").replace(".","")
    if not rate.isnumeric():
        return HttpResponse(f'<i>"{rate}" is invalid. Please, provide valid amount</i>')
    else:
        return HttpResponse("")

#  Sector Validation
def SectorValidation(request):
    sector = request.GET.get('sector')
    if Sector.objects.filter(name__iexact=sector).exists():
        return HttpResponse(f'<i>"{sector}" already exists.</i>')
    else:
        return HttpResponse("")

#  Profile RC Number Check
def ProfileRCValidation(request):
    rc_number = request.GET.get('rc_number')
    if User.objects.filter(rc_number__iexact=rc_number).exists():
        return HttpResponse(f'<i>"{rc_number}" already exists.</i>')
    else:
        return HttpResponse("")
    

#  Profile RC Number Check
def PhoneValidation(request):
    phone_number = request.GET.get('phone_number')
    if User.objects.filter(phone_number__iexact=phone_number).exists():
        return HttpResponse(f'<i>"{phone_number}" already exists.</i>')
    elif len(phone_number) < 11:
        return HttpResponse(f'<i>Phone number is not complete.</i>')
    elif len(phone_number) > 11:
        return HttpResponse(f'<i>Phone number is too long.</i>')
    else:
        return HttpResponse("")
    

