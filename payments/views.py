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
            'display_amount_value': payment.amount / 100
        }
        return render(request, 'payments/make_payment.html', context)

    return render(request, 'payments/payment.html')


# def verify_payment(request, ref):
#     payment = Payment.objects.get(ref=ref)
#     verified = payment.verify_payment()

#     demand_notice = DemandNotice.objects.get(referenceid=payment.referenceid)

#     total = demand_notice.amount_due + demand_notice.penalty + demand_notice.annual_fee\
#         - demand_notice.remittance - demand_notice.waiver_applied - demand_notice.amount_paid

#     print("TOTAL LIABILITY: ", demand_notice.total_due, " Sum: ", total)
#     amount = demand_notice.total_due * 100



#     if verified:
#         if (total == (payment.amount / 100)):
#             DemandNotice.objects.filter(referenceid=payment.referenceid).update(amount_paid=total, status='RESOLVED')
#         else:
#             DemandNotice.objects.filter(referenceid=payment.referenceid).update(amount_paid=total, status='UNDISPUTED PAID')
#         # user_wallet = UserWallet.objects.get(user=request.user)
#         # user_wallet.balance += payment.amount
#         # user_wallet.save()
#         # print(request.user.username, " funded wallet successfully")
#         # return render(request, "success.html")
#     return render(request, "success.html")

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


    # authorization="Authorization: Bearer YOUR_SECRET_KEY"
    # curl "$url" -H "$authorization" -X GET