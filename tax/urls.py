from django.urls import path
from .views import new_infra_view, existing_infra_view, page_view, import_export, htmx_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('apply/permit/', new_infra_view.new_infrastructure, name="apply_for_permit"),
    path('apply/demand_notice/<str:ref_id>/', new_infra_view.generate_demand_notice, name="generate_demand_notice"),
    path('apply/demand_notice/receipt/<str:ref_id>/', new_infra_view.generate_receipt, name="generate_receipt"),
    path('apply/permit/resources/', new_infra_view.resources, name="resources"),
    
    # HTMX endpoint
    path('apply/infra/', htmx_view.add_infrastructure_form, name="add_infrastructure_form"),
    path('apply/infra/ex/', htmx_view.add_ex_infrastructure_form, name="add_ex_infrastructure_form"),
    path('apply/infra/add/', htmx_view.add_infrastructure, name="add_infrastructure"),
    path('apply/infra/add2/', htmx_view.add_infrastructure2, name="add_infrastructure2"),
    path('apply/infra/ex/add/', htmx_view.add_ex_infrastructure, name="add_ex_infrastructure"),
    path('apply/infra/ex/add2/', htmx_view.add_ex_infrastructure2, name="add_ex_infrastructure2"),

    # HTMX SEARCH
    path('apply/search/', htmx_view.search_tax_dn, name="search_tax_dn"),
    path('apply/search/dashboard/', htmx_view.search_tax_dashboard, name="search_tax_dashboard"),
    path('apply/search/infratructure/', htmx_view.search_tax_infrastructure, name="search_tax_infrastructure"),

    ####### Exisiting Infrastructures
    path('apply/permit/exist/', existing_infra_view.apply_for_existing_permit, name="apply_existing_infra"),
    path('apply/demand_notice/ex/<str:ref_id>/', existing_infra_view.generate_ex_demand_notice, name="generate_ex_demand_notice"),
    path('apply/demand_notice/ex/receipt/<str:ref_id>/', existing_infra_view.generate_ex_receipt, name="generate_ex_receipt"),
    
    path('apply/permit/dispute_ex_notice/<str:ref_id>/', existing_infra_view.dispute_ex_demand_notice, name="dispute-ex-demand-notice"),
    path('apply/permit/undisputed_ex_notice_receipt/<str:ref_id>/', existing_infra_view.undispute_ex_demand_notice_receipt, name="undispute_ex_demand_notice_receipt"),
    path('apply/permit/resolved/<str:ref_id>/', existing_infra_view.resolved_demand_notice_receipt, name="resolved_demand_notice_receipt"),
    path('apply/permit/revised/receipt/<str:ref_id>/', existing_infra_view.revised_demand_notice_receipt, name="revised_demand_notice_receipt"),
    
    path('apply/waver/', existing_infra_view.apply_for_waver, name="apply_for_waver"),
    path('apply/remittance/', existing_infra_view.apply_remittance, name="apply_remittance"),
    
    #  PAGES URL
    path('dashboard/', page_view.dashboard, name="dashboard"),
    path('demand_notice/', page_view.demand_notice, name="demand-notice"),
    path('disputes/', page_view.disputes, name="disputes"),
    path('infrastructures/', page_view.infrastructures, name="infrastructures"),
    path('downloads/', page_view.downloads, name="downloads"),
    path('resources/', page_view.resources, name="resources"),
    # settings/ is in the account app

    # BULK UPLOAD (CSV / EXCEL)
    path('upload/new/', import_export.upload_new, name="upload_new"),
    path('upload/old/', import_export.upload_old, name="upload_old"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
