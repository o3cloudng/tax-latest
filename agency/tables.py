import django_tables2 as tables
from tax.models import DemandNotice

class DemandNoticeTables(tables.Table):
    class Meta:
        # attrs = {
        #     'class': 'w-full overflow-auto',
        #     'thead': {
        #         'class': 'bg-gray-50 border-b-2 border-gray-200',
        #         },
        #     }
        model = DemandNotice
        fields = ("referenceid","amount_due", "annual_due", "remittance", 
                  "amount_paid", "penalty","waiver_amount","total_due", "created_at", "status")

# amount_due
# subtotal
# penalty
# application_fee
# admin_fee
 
# annual_fee
# remittance
# waiver_applied
# amount_paid
# total_due