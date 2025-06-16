from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Payment, UserWallet
from django.conf import settings
from django.db.models import Sum
from tax.models import DemandNotice
from account.models import AdminSetting
from agency.models import Agency
from django.db import transaction
import requests
import json
from core import settings
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date
from core.services import send_demand_notice_email
# from payments.paystack import verify_payment


@transaction.atomic
def initiate_payment(request):
    if request.method == "POST":
        # amount = int(float(request.POST['amount'])) * 100
        email = request.POST['email']
        referenceid = request.POST['referenceid']

        demand_notice = DemandNotice.objects.get(referenceid=request.POST['referenceid'])

        total = (demand_notice.amount_due + demand_notice.penalty) \
            - (demand_notice.remittance + demand_notice.waiver_applied + demand_notice.amount_paid)

        # print("TOTAL LIABILITY: ", demand_notice.total_due, " Sum: ", total)
        amount = demand_notice.total_due

        pk = settings.PAYSTACK_PUBLIC_KEY

        payment = Payment.objects.create(amount=amount, email=email, user=request.user, referenceid=referenceid)
        payment.save()
        # demand_notice.amount_paid = (amount / 100)
        # demand_notice.save()

        print(f"PAY REF: {payment.ref}")
        
        context = {
            'payment': payment,
            'field_values': request.POST,
            'paystack_pub_key': pk,
            'amount_value': payment.amount,
            'referenceid': referenceid,
            'display_amount_value': payment.amount
        }
        return render(request, 'payments/make_payment.html', context)

    return render(request, 'payments/payment.html')


@transaction.atomic  
def pay4it_initiate(request):
    if request.method == 'POST':
        ref = request.POST['ref']
        pay = Payment.objects.get(ref=ref)
        print(f"Transaction Reference: {pay.ref}")
        # SESSION FOR REFERENCE TO VERIFY
        request.session['payment_reference'] = pay.ref
        
        # https://doc.usepay4it.com/accept-payment/standard-checkout
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "pid": "N-2160784",
            "amount": pay.amount,
            "appliedDate": str(date.today()),
            "revenueCode": settings.REVENUE_CODE,
            "agencyCode": settings.AGENCY_CODE
            }
        # try:
        # print(f"CBS URL: {settings.CBS_URL} | {type(settings.CBS_URL)}")
        res = requests.put(settings.CBS_URL, headers=headers, json=payload)
        response = res.json()

        # print(f"MESSAGE: {response['RespondCode']}")
        
        if res.status_code == 200 and response['Status'] == "SUCCESS":
            # print(f"STATUS MESSAGE: {response['StatusMessage']}")
            bill_reference = response['WebGuid']
            # pay = Payment.objects.filter(ref=ref)
            pay.reference=bill_reference
            pay.save()
            print(f"BILL REFERENCE: {bill_reference}")

            return HttpResponseRedirect(f"https://usepay4it.com/payment/collection?mda={settings.PAY4IT_API_KEY}&tx_reference={bill_reference}&callbackUrl={settings.PAY4IT_CALLBACK_URL}") 

        else:
            # return JsonResponse({'error': data.get('message')}, status=400)
            return render(request, 'payments/make_payment.html')



@transaction.atomic
@csrf_exempt
def pay4it_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            # Process the webhook payload here
            print(f"Reference: {payload['reference']}")
            if Payment.objects.filter(reference = payload['reference']).exists():
                payment = Payment.objects.get(reference = payload['reference'])
                
                payment.paymentReference = str(payload['paymentReference'])
                payment.status = payload['Status']
                # payment.amount = int(payload['amountPaid']),
                payment.receipt = payload['Receipt']

                print(f"PaymentRef: {payment.paymentReference} | Status: {payment.status}")
                
                payment.save()
                return HttpResponse(status=200) # Return HTTP 200 to acknowledge receipt
            else:
                return HttpResponse(status=400) # Return HTTP 400 if the payload is invalid

        except json.JSONDecodeError:
            return HttpResponse(status=400) # Return HTTP 400 if the payload is invalid
    else:
        return HttpResponse(status=405) # Return HTTP 405 for non-POST requests


@csrf_exempt
def pay4it_callback(request):
    if request.method == 'GET':
        # TXFHTAX3CO1749806340128
        # https://usepay4it.com/api/v1/abc/GetTransactionByPaymentRef
        # Verify the transaction
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        print(f"REF: {request.session.get('payment_reference')}")
        
        payment = Payment.objects.get(ref=request.session.get('payment_reference'))
        referenceid = payment.referenceid

        payload = {
            "paymentRef": payment.paymentReference # 21607840-8945746-192
            }
        
        print(f"REF: {request.session.get('payment_reference')} | PAYREF {payment.paymentReference} | ")
        verify_response = requests.put(settings.CBS_URL_VERIFY, headers=headers, json=payload)

        verify_response.raise_for_status()
        verification = verify_response.json()
        print("VERIFICATION: ", verification['Transaction']['NotificationDetails']['ResponseCode'])
        try:
            if verification['Transaction']['NotificationDetails']['ResponseCode'] == 'SUCCESSFULL':
                Payment.objects.filter(ref=payment.ref).update(verified=True)
            
            if Payment.objects.filter(referenceid=referenceid, verified=True).exists():
                total_paid = Payment.objects.filter(referenceid=referenceid, verified=True).aggregate(total=Sum('amount'))['total']   
            else:
                total_paid = 0
            
            demand_notice = DemandNotice.objects.get(referenceid=payment.referenceid)

            total = demand_notice.amount_due + demand_notice.penalty + demand_notice.annual_fee \
                - (demand_notice.remittance + demand_notice.waiver_applied + total_paid)
            # print("SUCCESS")
            # print(data['message'])
            if total <= 0:
                DemandNotice.objects.filter(referenceid=payment.referenceid) \
                .update(amount_paid=total_paid, status='RESOLVED', total_due=total)

                mail_subject = f"Resolved Demand Notice - Ref No: {referenceid}"
                email_template = "Emails/tax_payer/paid_notice.html"
                agency_email_subject = f"RESOLVED DEMAND NOTICE - {request.user.company_name}"
                send_demand_notice_email(request, mail_subject, referenceid, demand_notice.created_at,\
                                          demand_notice.total_due, email_template, agency_email_subject)
            else:
                DemandNotice.objects.filter(referenceid=payment.referenceid) \
                    .update(amount_paid=total_paid, status='UNDISPUTED PAID', total_due=total)
                
                mail_subject = f"Undisputed Paid Demand Notice - Ref No: {referenceid}"
                email_template = "Emails/tax_payer/paid_undisputed.html"
                agency_email_subject = f"RESOLVED DEMAND NOTICE - {request.user.company_name}"
                send_demand_notice_email(request, mail_subject, referenceid, demand_notice.created_at,\
                                          demand_notice.total_due, email_template, agency_email_subject)

            infra = demand_notice.infra
            infra = infra.replace("'", '"')
            infra = json.loads(infra)
            # print(type(infra), infra)
            admin_settings = AdminSetting.objects.all()

            context = {
                'ref_id': payment.referenceid,
                'company': request.user,
                'demand_notice': demand_notice,
                'subtotal': demand_notice.subtotal,
                'penalty': demand_notice.penalty,
                'amount_paid': demand_notice.amount_paid,
                'amount_due': demand_notice.amount_due,
                'annual_fee': demand_notice.annual_fee,
                'remittance': demand_notice.remittance,
                'waiver_applied': demand_notice.waiver_applied,
                'total_liability': demand_notice.total_due, #- dn.waiver_applied,
                'agency': Agency.objects.all().first(),
                'remittance': demand_notice.remittance,
                'site_assessment_cost': demand_notice.site_assessment, 
                'infrastructure': infra,     
                
                
                'app_fee': admin_settings.get(slug='application-fee'),
                'total_app_fee': demand_notice.application_fee,
                'admin_pm_fees': demand_notice.admin_fee,
                'admin_pm_fees_sum': demand_notice.admin_fee,
                'site_assessment': demand_notice.site_assessment,
                'total_due': demand_notice.total_due,
                'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
                'sar_fee':admin_settings.get(slug='site-assessment').rate,
            }
            all_paid = (demand_notice.amount_due + demand_notice.penalty + demand_notice.annual_fee) \
                        - (demand_notice.remittance + demand_notice.waiver_applied + total_paid)
            if all_paid == 0:
                return render(request, "payments/paid_receipt.html", context)
            
            return render(request, "payments/undisputed_paid_receipt.html", context)

        
        except Exception as e:
            # Log the error
            return HttpResponse(status=400)
    
    return HttpResponse(status=405)


@transaction.atomic
def paystack_verify(request, ref):

    if not Payment.objects.filter(ref=ref).exists():
        messages.error(request, "Payment not initialized.")
        return redirect('dashboard')
    payment = Payment.objects.get(ref=ref)
    referenceid = payment.referenceid
    # print("REFERENCEID: ", payment.referenceid)
    # print("REF: ", payment.ref)
    
    url=f"https://api.paystack.co/transaction/verify/{payment.ref}"

    bearer_token = settings.PAYSTACK_SECRET_KEY

    headers = {"Authorization": f"Bearer {bearer_token}"}
    # print(bearer_token, type(bearer_token))

    response = requests.get(url, headers=headers)

    data = response.json()
    # print("SUCCESS: ",response.json())
    
    if payment.ref == ref:
        # print("REF: ", data['data']['amount'], type(data['data']['amount']), payment.amount, total)
        if (data['status'] == True) & (data['data']['amount']==payment.amount):
            Payment.objects.filter(ref=payment.ref).update(verified=True)
            
            if Payment.objects.filter(referenceid=referenceid, verified=True).exists():
                total_paid = Payment.objects.filter(referenceid=referenceid, verified=True).aggregate(total=Sum('amount'))['total'] / 100    
            else:
                total_paid = 0
            demand_notice = DemandNotice.objects.get(referenceid=payment.referenceid)

            total = demand_notice.amount_due + demand_notice.penalty + demand_notice.annual_fee \
                - (demand_notice.remittance + demand_notice.waiver_applied + total_paid)
            # print("SUCCESS")
            # print(data['message'])
            if total <= 0:
                DemandNotice.objects.filter(referenceid=payment.referenceid) \
                .update(amount_paid=total_paid, status='RESOLVED', total_due=total)
                # print("RESOLVED: ")
            else:
                DemandNotice.objects.filter(referenceid=payment.referenceid) \
                    .update(amount_paid=total_paid, status='UNDISPUTED PAID', total_due=total)
                # print("UNDISPUETD PAID: ")
            # Payment.objects.filter(ref=payment.ref).update(verified=True)

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)
    # print(type(infra), infra)
    admin_settings = AdminSetting.objects.all()

    context = {
        'ref_id': payment.referenceid,
        'company': request.user,
        'demand_notice': demand_notice,
        'subtotal': demand_notice.subtotal,
        'penalty': demand_notice.penalty,
        'amount_paid': demand_notice.amount_paid,
        'amount_due': demand_notice.amount_due,
        'annual_fee': demand_notice.annual_fee,
        'remittance': demand_notice.remittance,
        'waiver_applied': demand_notice.waiver_applied,
        'total_liability': demand_notice.total_due, #- dn.waiver_applied,
        'agency': Agency.objects.all().first(),
        'remittance': demand_notice.remittance,
        'site_assessment_cost': demand_notice.site_assessment, 
        'infrastructure': infra,     
        
        
        'app_fee': admin_settings.get(slug='application-fee'),
        'total_app_fee': demand_notice.application_fee,
        'admin_pm_fees': demand_notice.admin_fee,
        'admin_pm_fees_sum': demand_notice.admin_fee,
        'site_assessment': demand_notice.site_assessment,
        'total_due': demand_notice.total_due,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
    }
    all_paid = (demand_notice.amount_due + demand_notice.penalty + demand_notice.annual_fee) \
                - (demand_notice.remittance + demand_notice.waiver_applied + total_paid)
    if all_paid == 0:
        return render(request, "payments/paid_receipt.html", context)
    
    return render(request, "payments/undisputed_paid_receipt.html", context)


