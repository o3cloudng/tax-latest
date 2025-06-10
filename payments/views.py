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
from django.http import HttpResponse
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
        amount = demand_notice.total_due * 100

        pk = settings.PAYSTACK_PUBLIC_KEY

        payment = Payment.objects.create(amount=amount, email=email, user=request.user, referenceid=referenceid)
        payment.save()
        # demand_notice.amount_paid = (amount / 100)
        # demand_notice.save()

        
        context = {
            'payment': payment,
            'field_values': request.POST,
            'paystack_pub_key': pk,
            'amount_value': payment.amount,
            'referenceid': referenceid,
            'display_amount_value': payment.amount / 100
        }
        return render(request, 'payments/make_payment.html', context)

    return render(request, 'payments/payment.html')


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


    
class Pay4ItInitiatePayment(View):
    def post(self, request):
        email = request.user.email
        referenceid = request.POST['referenceid']
        print(f"EMAIL: {email} | REF_ID: {referenceid}")

        demand_notice = DemandNotice.objects.get(referenceid=request.POST['referenceid'])
        
        amount = demand_notice.total_due * 100
        # Initiating Payment
        payment = Payment.objects.create(amount=amount, email=email, user=request.user, referenceid=referenceid)
        # payment.save()
        pay = Payment.objects.get(pk=payment.id)
        
        # payload = {
        #     "merchant_id": settings.PAY4IT_CONFIG['MERCHANT_ID'],
        #     "api_key": settings.PAY4IT_CONFIG['API_KEY'],
        #     "amount": pay.amount,
        #     "currency": "NGN",  # or your preferred currency
        #     "customer_email": request.user.email,
        #     "transaction_reference": pay.ref,  # your unique reference
        #     "callback_url": settings.PAY4IT_CONFIG['CALLBACK_URL'],
        #     "return_url": settings.PAY4IT_CONFIG['RETURN_URL'],
        # }
        
        # Doc: https://usepay4it.com/api/v1/docs/#/MDA%20Payment/post_api_v1_mda_InitiatePayment
        # payload1 = {
        #     "apiKey": settings.PAY4IT_CONFIG['API_KEY'],
        #     "amountPaid": pay.amount,
        #     "reference": pay.ref,
        #     "email": request.user.email,
        #     "AgencyName": request.user.company_name,
        #     "RevName": "string",
        #     "OraAgencyRev": "string",
        #     "RevenueCode": "string",
        #     "PayerName": "string",
        #     "AgencyCode": settings.PAY4IT_CONFIG['MERCHANT_ID'],
        #     "serviceCharge": "string",
        #     "mobile": request.user.phone_number,
        #     "Pid": "string",
        #     "CreditAccount": "string",
        #     "CbnCode": "string"
        # }

        # https://doc.usepay4it.com/accept-payment/standard-checkout
        payload = {
            # "publicKey": settings.PAY4IT_CONFIG['PAY4IT_API_KEY'],
            "mda": settings.PAY4IT_CONFIG['PAY4IT_API_KEY'],
            "amount":amount,
            "currency":"NGN",
            "country":"NG",
            "paymentReference":pay.ref,
            "email": request.user.email,
            "productId": pay.referenceid,
            "productDescription":"product description",
            "callbackUrl": settings.PAY4IT_CONFIG['CALLBACK_URL']
        }
        try:
            # https://usepay4it.com/payment/collection?mda=TEST-Key-68474a3a05ae8db6240f92dd&tx_reference={BILL_REFERENCE}&callbackUrl={YOUR_CALLBACK_URL}
            response = requests.post(
                # f"{settings.PAY4IT_CONFIG['BASE_URL']}?mda={settings.PAY4IT_CONFIG['PAY4IT_API_KEY']}&tx_reference={pay.ref}&callbackUrl={settings.PAY4IT_CONFIG['CALLBACK_URL']}",
                f"{settings.PAY4IT_CONFIG['BASE_URL']}",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                # return redirect(data['payment_url'])
                context = {
                    'payment': payment,
                    'field_values': request.POST,
                    'amount_value': pay.amount,
                    'display_amount_value': pay.amount
                }
                return render(request, 'payments/make_payment.html', context)

            else:
                # return JsonResponse({'error': data.get('message')}, status=400)
                return render(request, 'payments/payment.html')
                
        except requests.exceptions.RequestException as e:
            # return JsonResponse({'error': str(e)}, status=500)
            return render(request, 'payments/payment.html')
        
    def get(self, request):
        email = request.POST['email']
        referenceid = request.POST['referenceid']

        demand_notice = DemandNotice.objects.get(referenceid=referenceid, email=email)
        
        amount = demand_notice.total_due * 100
        # payment.save()
        context = {
            # 'payment': payment,
            'referenceid': referenceid,
            # 'ref': ref,
            'field_values': request.POST,
            'amount_value': amount,
            'display_amount_value': amount
        }
        return render(request, 'payments/make_payment.html', context)
        

@csrf_exempt
def pay4it_callback(request):
    if request.method == 'POST':
        # Verify the transaction
        transaction_ref = request.POST.get('transaction_reference')
        status = request.POST.get('status')
        
        # Get additional verification data
        verification_data = {
            'merchant_id': settings.PAY4IT_CONFIG['MERCHANT_ID'],
            'api_key': settings.PAY4IT_CONFIG['API_KEY'],
            'transaction_reference': transaction_ref
        }
        
        try:
            verify_response = requests.post(
                f"{settings.PAY4IT_CONFIG['BASE_URL']}payment/verify",
                json=verification_data
            )
            verify_response.raise_for_status()
            verification = verify_response.json()
            
            if verification.get('status') == 'success':
                # Update your database with successful payment
                # order = Order.objects.get(reference=transaction_ref)
                # order.mark_as_paid()
                return HttpResponse(status=200)
        
        except Exception as e:
            # Log the error
            return HttpResponse(status=400)
    
    return HttpResponse(status=405)