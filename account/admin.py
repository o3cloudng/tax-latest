from django.contrib import admin
from account.models import User, Sector, AdminSetting
# Register your models here.
from import_export.admin import ImportExportModelAdmin

admin.site.register(User) 
# admin.site.register(DemandNotice) 
# @admin.site.register(User)
# class CompanyAdmin(ImportExportModelAdmin):
#     list_display = [
#         'email', 
#         'company_name', 'username', 'created_by',
#         'contact_name', 'phone_number'
#         ]

# admin.site.register(Sector)
@admin.register(Sector)
class SectorAdmin(ImportExportModelAdmin):
    list_display = ['name']

# admin.site.register(AdminSetting)
@admin.register(AdminSetting)
class AdminSettingAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug', 'description', 'rate']


