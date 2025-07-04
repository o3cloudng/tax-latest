from  django.contrib  import  admin
from .models  import  Payment, UserWallet

class  PaymentAdmin(admin.ModelAdmin):
    list_display  = ["id","user", "referenceid", "reference", "paymentReference",  "amount", "verified", "ref", "date_created"]

admin.site.register(Payment, PaymentAdmin)
# admin.site.register(UserWallet)

 