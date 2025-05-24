from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from tax.models import InfrastructureType, Waiver, Remittance, Infrastructure, DemandNotice
# from import_export.admin import ImportExportModelAdmin 
# admin.site.register(Permit)
admin.site.register(Waiver)
admin.site.register(Remittance)
# admin.site.register(DemandNotice)

@admin.register(InfrastructureType)
class InfrastructureTypeAdmin(ImportExportModelAdmin):
    list_display = ['infra_name', 'rate']


@admin.register(Infrastructure)
class InfrastructureAdmin(ImportExportModelAdmin):
    list_display = ['company', 'created_by', 'infra_type', 'referenceid', 'cost', 'is_existing','processed']

@admin.register(DemandNotice)
class DemandNoticeAdmin(ImportExportModelAdmin):
    list_display = ['id','referenceid', 'company', 'status', 'annual_fee', 'remittance',\
                    'waiver_applied', 'amount_paid','created_by']

# @admin.register(Infrastructure)
# class InfrastructureAdmin(ImportExportModelAdmin):
#     list_display = ('infra_type', 'length', 'address','year_installed', 'upload_application_letter',
#                   'upload_asBuilt_drawing')

