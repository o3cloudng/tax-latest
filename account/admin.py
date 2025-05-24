from django.contrib import admin
from account.models import User, Sector, AdminSetting
# Register your models here.

admin.site.register(User)
admin.site.register(Sector)
admin.site.register(AdminSetting)


