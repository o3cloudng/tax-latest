from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from tax.resources import InfrastructureResource

from tablib import Dataset
# import tablib
from core.decorator import tax_payer_only
# from core.services import generate_ref_id
from tax.models import Infrastructure, InfrastructureType
from django.contrib import messages
import csv, io
from django.db import transaction


@login_required
@tax_payer_only
@transaction.atomic
def upload_old(request):
    # ref_id = generate_ref_id()
    if request.method == 'POST':
        # print("FILES: ", request.FILES['bulk_upload'])
        
        if not request.FILES.get('bulk_upload', False):
            messages.error(request, 'No file attached.')
            return redirect('apply_existing_infra')
        
        bulk_upload = request.FILES['bulk_upload']
        # resource = InfrastructureResource()
        
        if not (bulk_upload.name.endswith('csv') | bulk_upload.name.endswith('xlxs')):
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
                company=request.user, 
                length=column[3],
                address=column[4],
                year_installed=column[5],
                cost=cost,
                created_by=request.user,
                is_existing = True,
                processed = False,
                # referenceid = ref_id,
                upload_application_letter=column[6],
                upload_asBuilt_drawing=column[7]
                )
                
        messages.success(request, "Bulk upload successful")
    return redirect('apply_existing_infra')

@login_required
@tax_payer_only
@transaction.atomic
def upload_new(request):
    # ref_id = generate_ref_id()
    if request.method == 'POST':
        # print("FILES: ", request.FILES['bulk_upload_new'])

        if not request.FILES.get('bulk_upload_new', False):
            messages.error(request, 'No file attached.')
            return redirect('apply_for_permit')
        
        bulk_upload = request.FILES['bulk_upload_new']
        # resource = InfrastructureResource()

        if not (bulk_upload.name.endswith('csv') | bulk_upload.name.endswith('xlxs')):
            messages.error(request, 'Wrong file format')
            return redirect('apply_for_permit')
        
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
                company=request.user, 
                length=column[3],
                address=column[4],
                year_installed=column[5],
                cost=cost,
                created_by=request.user,
                is_existing = False,
                processed = False,
                # referenceid = ref_id,
                upload_application_letter=column[6],
                upload_asBuilt_drawing=column[7]
                )
                
        messages.success(request, "Bulk upload successful")
    return redirect('apply_for_permit')