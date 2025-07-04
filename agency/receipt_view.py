# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from core.decorator import admin_only
# from django.shortcuts import redirect
# from tax.models import Waiver, Remittance
# from account.models import AdminSetting
# from django.db.models import Q, Sum
# from agency.models import Agency
# from agency.penalty_calculation import penalty_calculation 



# @login_required
# @admin_only
# def company_dispute_receipt(request, ref_id):
#     permits = Permit.objects.filter(referenceid = ref_id, is_disputed=True)
#     # company = User.objects.get(pk=company_id)
#     company = permits.first().company

#     for p in permits:
#         print(p.company)
    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")
#     penalty = AdminSetting.objects.get(slug="penalty")

#     mast_roof = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')))
#     length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='Optic') | Q(infra_type__infra_name__icontains='Gas') | Q(infra_type__infra_name__icontains='Power') | Q(infra_type__infra_name__icontains='Pipeline')))
#     #application number = number of masts and rooftops 

#     mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
    
#     # PENALTY CALCULATION
#     refid = Q(referenceid = ref_id)
#     is_exist = Q(is_existing=True)
#     is_disputed = Q(is_disputed=True)
#     if Permit.objects.filter(refid & is_exist).exists():
#         age_sum = Permit.objects.filter(refid & is_exist & is_disputed).aggregate(ages = Sum('age'))['ages']
#     else:
#         age_sum = 0

#     print("AGE Calculated: ", age_sum)
    
#     penalty_sum = age_sum * penalty.rate
#     print("PENALTY SUM: ", penalty_sum)
    

#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
#         mast_roof_no = mast_roof_no['no_sites']
#     else:
#         mast_roof_no = 0
#         # mast_roof_no['no_sites'] = 0

#     print("MAST & ROOF NO: ", mast_roof_no)
#     if length.exists():
#         length = length.count()
#     else:
#         length = 0

#     app_count = mast_roof_no + length
#     total_app_fee = app_count * app_fee.rate

#     # print("TOTAL SUM: ", mast_roof_no)

#     # print("APPLICATION COUNT: ", app_count)

#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True)).aggregate(no_sum = Sum('infra_cost'))
#     print("Tot Sum: ", tot_sum_infra)

#     # Site assessment report rate
#     sar_rate = mast_roof_no * site_assessment.rate

#     admin_pm_fees_sum = admin_pm_fees.rate * tot_sum_infra['no_sum'] / 100
#     print("TOTAL SUM OF INFRA: ", tot_sum_infra['no_sum'])

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref_id).exists():
#         waver = Waiver.objects.get(referenceid=ref_id).wave_amount
#         print("Waiver: ", waver)
#     else:
#         waver = 0

#     total_liability = total_due - waver    

#     if Remittance.objects.filter(referenceid=ref_id, company=company.id).exists():
#         remittance = Remittance.objects.get(referenceid=ref_id, company=company.id)
#         total_liability = total_liability - remittance.remitted_amount
#     else:
#         remittance = 0

#     if penalty_sum:
#         total_liability = total_liability + penalty_sum

#     # print("WAVER: ", waver)

#     context = {
#         'permits': permits,
#         'company': company,
#         'ref': ref,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no,
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'remittance': remittance,
#         'penalty': penalty,
#         'penalty_sum': penalty_sum,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'agency/receipts/undisputed_receipt.html', context)

# @login_required
# def company_revised_receipt(request, ref_id):
#     permits = Permit.objects.filter(referenceid = ref_id, is_disputed=True)
#     # UPDATE PERMIT TO REVISED
#     print("UPDATE PERMIT TO REVISED")
#     permits.update(is_revised = True)

#     company = permits.first().company    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")
#     penalty = AdminSetting.objects.get(slug="penalty")

#     mast_roof = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')))
#     length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='Optic') | Q(infra_type__infra_name__icontains='Gas') | Q(infra_type__infra_name__icontains='Power') | Q(infra_type__infra_name__icontains='Pipeline')))
#     #application number = number of masts and rooftops 
#     # PENALTY CALCULATION
#     refid = Q(referenceid = ref_id)
#     is_exist = Q(is_existing=True)
#     is_disputed = Q(is_disputed=True)
#     if Permit.objects.filter(refid & is_exist).exists():
#         age_sum = Permit.objects.filter(refid & is_exist & is_disputed).aggregate(ages = Sum('age'))['ages']
#     else:
#         age_sum = 0

#     penalty_sum = age_sum * penalty.rate
    

#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
#         mast_roof_no = mast_roof_no['no_sites']
#     else:
#         mast_roof_no = 0
#         # mast_roof_no['no_sites'] = 0

#     print("MAST & ROOF NO: ", mast_roof_no)
#     if length.exists():
#         length = length.count()
#     else:
#         length = 0

#     app_count = mast_roof_no + length
#     total_app_fee = app_count * app_fee.rate

#     # print("TOTAL SUM: ", mast_roof_no)

#     # print("APPLICATION COUNT: ", app_count)

#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True)).aggregate(no_sum = Sum('infra_cost'))
#     print("Tot Sum: ", tot_sum_infra)

#     # Site assessment report rate
#     sar_rate = mast_roof_no * site_assessment.rate

#     admin_pm_fees_sum = admin_pm_fees.rate * tot_sum_infra['no_sum'] / 100
#     print("TOTAL SUM OF INFRA: ", tot_sum_infra['no_sum'])

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref_id).exists():
#         waver = Waiver.objects.get(referenceid=ref_id).wave_amount
#         print("Waiver: ", waver)
#     else:
#         waver = 0
#     if Remittance.objects.filter(referenceid=ref_id, company=company.id).exists():
#         remittance = Remittance.objects.get(referenceid=ref_id, company=company.id)
#         total_liability = total_liability - remittance.remitted_amount
#     else:
#         remittance = 0

#     total_liability = total_due - waver + penalty_sum 


#     # print("WAVER: ", waver)

#     context = {
#         'permits': permits,
#         'company': company,
#         'ref': ref,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no,
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'remittance': remittance,
#         'penalty': penalty,
#         'penalty_sum': penalty_sum,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'agency/receipts/revised_receipt.html', context)


# @login_required
# @admin_only
# def demand_notice_receipt(request, ref_id):
#     permits = Permit.objects.filter(Q(referenceid = ref_id))
#     company = permits.first().company  

#     if not permits.exists(): # If permit does not exist
#         return redirect('apply_for_permit')
    
#     # if not permits.first().company == request.user: # If permite does not belong to signed in company
#     #     return redirect('apply_for_permit')
    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")
#     penalty = AdminSetting.objects.get(slug="penalty")

#     mast_roof = Permit.objects.filter((Q(referenceid = ref_id) & Q(is_disputed=False) & Q(is_existing=True)) & (Q(infra_type__infra_name__istartswith='Mast') | Q(infra_type__infra_name__istartswith='Roof')))
    
#     length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=False) & Q(is_existing=True) & (Q(infra_type__infra_name__istartswith='Optic') | Q(infra_type__infra_name__istartswith='Gas') | Q(infra_type__infra_name__istartswith='Power') | Q(infra_type__infra_name__istartswith='Pipe')))
#     #application number = number of masts and rooftops 

#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))['no_sites']
#     else:
#         mast_roof_no = 0
#     # print("MAST & ROOF NO: ", mast_roof.count())
#     if length.exists():
#         app_count = mast_roof_no + length.count()
#         others_sum = length.aggregate(no_sites = Sum('amount'))['no_sites']
#         print("GAS SUM: ", others_sum)
#     else:
#         app_count = mast_roof_no + 0

#     total_app_fee = app_count * app_fee.rate
#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id)).aggregate(no_sum = Sum('infra_cost'))['no_sum']
#     if not tot_sum_infra:
#         tot_sum_infra = 1

#     # Site assessment report rate
#     sar_rate = mast_roof_no * site_assessment.rate
#     admin_pm_fees_sum = (admin_pm_fees.rate * tot_sum_infra) / 100

#     total_due = tot_sum_infra + total_app_fee + admin_pm_fees_sum + sar_rate

#     print("TOTAL SUM INFRA: ", tot_sum_infra)
#     print("TOTAL DUE: ", total_due)
#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref).exists():
#         waver = Waiver.objects.get(referenceid=ref).wave_amount
#     else:
#         waver = 0
#     # PENALTY CALCULATION
#     refid = Q(referenceid = ref_id)
#     is_exist = Q(is_existing=True)
#     not_dispute = Q(is_disputed=False)
#     not_paid = Q(is_paid=False)
#     # current_user = Q(comapny = request.user)
#     if Permit.objects.filter(refid & is_exist).exists():
#         penalty_sum = penalty_calculation() 
#         penalty_sum = penalty_sum.filter(refid & is_exist & not_paid)
#         if penalty_sum.exists():
#             penalty_sum = penalty_sum.aggregate(sum_penalties = Sum('penalty'))['sum_penalties'] // 10000 * 10000
#             print("PENALTY SUM: ", penalty_sum)
#         else:
#             penalty_sum = 0

#     else:
#         penalty_sum = 0

#     total_liability = total_due + penalty_sum - waver

#     context = {
#         'permits': permits,
#         'ref': ref,
#         'company': company,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no,
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'penalty_sum': penalty_sum,
#         'penalty': penalty,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'agency/receipts/undisputed_receipt.html', context)


# @login_required
# @admin_only
# def company_revised_receipt(request, ref_id):
#     permits = Permit.objects.filter(referenceid = ref_id, is_disputed=True)
#     # UPDATE PERMIT TO REVISED
#     print("UPDATE PERMIT TO REVISED")
#     permits.update(is_revised = True)

#     company = permits.first().company    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")
#     penalty = AdminSetting.objects.get(slug="penalty")

#     mast_roof = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')))
#     length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True) & (Q(infra_type__infra_name__icontains='Optic') | Q(infra_type__infra_name__icontains='Gas') | Q(infra_type__infra_name__icontains='Power') | Q(infra_type__infra_name__icontains='Pipeline')))
#     #application number = number of masts and rooftops 

#     # PENALTY CALCULATION
#     refid = Q(referenceid = ref_id)
#     is_exist = Q(is_existing=True)
#     is_disputed = Q(is_disputed=True)
#     if Permit.objects.filter(refid & is_exist).exists():
#         age_sum = Permit.objects.filter(refid & is_exist & is_disputed).aggregate(ages = Sum('age'))['ages']
#     else:
#         age_sum = 0

#     print("AGE Calculated: ", age_sum)
    
#     penalty_sum = age_sum * penalty.rate
#     print("PENALTY SUM: ", penalty_sum)
#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
#         mast_roof_no = mast_roof_no['no_sites']
#     else:
#         mast_roof_no = 0
#         # mast_roof_no['no_sites'] = 0

#     print("MAST & ROOF NO: ", mast_roof_no)
#     if length.exists():
#         length = length.count()
#     else:
#         length = 0

#     # mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))
    
#     app_count = mast_roof_no + length
#     total_app_fee = app_count * app_fee.rate

#     # print("TOTAL SUM: ", mast_roof_no)

#     # print("APPLICATION COUNT: ", app_count)

#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=True)).aggregate(no_sum = Sum('infra_cost'))
#     print("Tot Sum: ", tot_sum_infra)

#     # Site assessment report rate
#     sar_rate = mast_roof_no * site_assessment.rate

#     admin_pm_fees_sum = admin_pm_fees.rate * tot_sum_infra['no_sum'] / 100
#     print("TOTAL SUM OF INFRA: ", tot_sum_infra['no_sum'])

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref_id).exists():
#         waver = Waiver.objects.get(referenceid=ref_id).wave_amount
#         print("Waiver: ", waver)
#     else:
#         waver = 0

#     total_liability = total_due - waver    

#     if Remittance.objects.filter(referenceid=ref_id, company=company.id).exists():
#         remittance = Remittance.objects.get(referenceid=ref_id, company=company.id)
#         total_liability = total_liability - remittance.remitted_amount
#     else:
#         remittance = 0

#     if penalty_sum:
#         total_liability = total_liability + penalty_sum

#     context = {
#         'permits': permits,
#         'company': company,
#         'ref': ref,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no,
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'remittance': remittance,
#         'penalty_sum': penalty_sum,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'tax-payers/receipts/revised_receipt.html', context)
