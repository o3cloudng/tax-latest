from django.urls import path
from agency.views import *
from agency.receipt_view import *
from agency.view.searches import *
from agency.infrastructure import *
from agency.demand_notice import *
from agency.view import validation
from core import services

urlpatterns = [
    # PAGES
    path('', agency_dashboard, name="agency_dashboard"),
    path('demand-notice/', agency_demand_notice, name="agency_demand_notice"),
    path('table/', demand_notice_table, name="demand_notice_table"),
    path('table2/', DemandTable.as_view(), name="demand_notice_table2"),
    path('dispute-notice/', agency_disputes, name="agency_disputes"),
    path('infrastructure/', agency_infrastructure, name="agency_infrastructure"),
    path('companies/', agency_companies, name="agency_companies"),
    path('companies/details/<int:pk>/', agency_companies_details, name="agency_companies_details"),
    path('companies/revised/notify/', send_revised_notice, name="send_revised_notice"),
    path('help/', agency_help, name="agency_help"),
    path('settings/', agency_settings, name="agency_settings"),
    path('settings/revenue/', delete_revenue_settings, name="delete_revenue_settings"),
    path('settings/sector/', delete_sector_settings, name="delete_sector_settings"),

    # Infrastructure
    path('infrastructure/add/<int:pk>/', agency_apply_for_permit, name="agency_add_infrastructure"),
    path('infrastructure/forms/', agency_add_infrastructure_form, name="agency_add_infrastructure_form"),
    path('infrastructure/add/new/', add_infrastructure, name="agency_add_company_infrastructure"),
    path('infrastructure/add/new2/', add_infrastructure2, name="agency_add_company_infrastructure2"),
    path('infrastructure/demand_notice/<int:pk>/', agency_generate_demand_notice, name="agency_generate_demand_notice"),
    path('infrastructure/demand_notice/receipt/<str:ref_id>/', agency_generate_receipt, name="agency_generate_receipt"),
    path('infrastructure/process/<int:pk>/', agency_process_infrastructure, name="agency_infrastructure_add"),

    # DEMAND NOTICE WAIVER
    path('waiver/<str:ref_id>/', agency_waiver, name="agency_waiver"),
    path('waiver/apply/', agency_apply_waiver, name="agency_apply_waiver"),
    
    # Infrastructure Existing
    path('infrastructure/ex/<int:pk>/', apply_for_existing_permit, name="agency_apply_for_exist"),
    path('infrastructure/forms2/', agency_add_ex_infrastructure_form, name="agency_add_ex_infrastructure_form"),
    path('infrastructure/add/ex/', add_ex_infrastructure, name="agency_add_ex_company_infrastructure"),
    path('infrastructure/add/ex2/', add_ex_infrastructure2, name="agency_add_ex_company_infrastructure2"),
    path('infrastructure/add/form/<int:pk>/', agency_add_permit_ex_form, name="agency_add_permit_ex_form"),

    # DEMAND NOTICE
    path('infrastructure/demand_notice/ex/', generate_ex_demand_notice, name="agency_company_ex_add"),
    path('infrastructure/process/<str:ref_id>/ex/', agency_generate_ex_receipt, name="agency_generate_ex_receipt"),
    
    # Edit Demand Notice
    path('companies/disputed/edit/<str:ref_id>/', edit_disputed_demand_notice, name="edit_disputed_demand_notice"),
    path('companies/dn/edit/<int:pk>/', dispute_dn_edit, name="dn_edit"),
    # path('companies/dn/accept/<int:pk>/', accept_undisputed_edit, name="accept_undisputed"),
    path('companies/dn/addform/<str:ref_id>/', agency_add_permit_form, name="agency_add_permit_form"),
    path('companies/dn/edit/add/', add_dispute_dn, name="add_dispute_dn"),
    path('companies/dn/add/', agency_add_undispute_edit, name="agency_add_undispute_edit"),
    path('companies/dn/update/', update_dispute_dn_edit, name="update_dispute_dn_edit"),
    path('companies/undisputed_notice_receipt/<str:ref_id>/', undispute_dn_receipt, name="undispute_dn_receipt"),
    path('companies/dn/delete/<int:pk>/', del_undisputed, name="del_undisputed"),
    path('companies/waivers/', waiver_requests, name="waiver_requests"),

    # RECEIPT
    path('companies/disputed/receipt/', company_approve_waiver, name="company_approve_waiver"),
    path('companies/undisputed_ex_notice_receipt/<str:ref_id>/', undispute_dn_receipt, name="undispute_dn_receipt"),
    # path('companies/dn/receipt/<str:ref_id>/', demand_notice_receipt, name="dn_receipt"),
    # path('companies/disputed/receipt/<str:ref_id>/', company_dispute_receipt, name="company_dispute_receipt"),
    # path('companies/revised/receipt/<str:ref_id>/', company_revised_receipt, name="company_revised_receipt"),
    
    # HTMX CALLS
    path('add_agency/', agency_account, name="add_agency"),
    path('add_company/', add_company, name="add_company"),
    path('create_company/', create_company, name="create_company"),
    path('add_update_infrastructure/', add_update_infrastructure, name="add_update_infrastructure"),
    path('add_update_sector/', add_update_sector, name="add_update_sector"),
    path('add_update_revenue/', add_update_revenue, name="add_update_revenue"),
    path('edit_company/<int:pk>/', edit_company, name="edit_company"),
    path('deactivate_company/<int:pk>/', deactivate_company, name="deactivate_company"),
    path('reactivate_company/<int:pk>/', reactivate_company, name="reactivate_company"),
    path('add_notification/', add_notification, name="add_notification"),
    path('validate_name/', validate_name, name="validate_name"),

    path('notification/', notification_view, name="notification"),
    # HTMX DELETE
    path('infrastructure/delete/', delete_infra_settings, name="delete_infra_settings"),


    path('email/', email_template, name="email_template"),

    # Search Company
    path('company/search/', company_search, name="search_company"),
    path('company/search/disputed/', search_disputed, name="search_disputed"),
    path('company/search/infrastructure/', search_infrastructure, name="search_infrastructure"),
    path('company/search/dn/', search_demand_notices, name="search_demand_notices"),
    path('company/search/details/', search_company_details, name="search_company_details"),

    path('test/', test_celery, name="test_celery"),
    path('sendemail/', sendemail, name="sendemail"),
    path('sendhtml/', send_email_html, name="send_email_html"),
    path('upload/ex/', agency_upload_new, name="agency_upload_new"),

    # Form Validation with htmx
    path('validation/email/', validation.InfraTypeValidation, name="InfraTypeValidation"),
    path('validation/rate/', validation.RateValidation, name="RateValidation"),
    path('validation/revnue/name/', validation.RevenueNameValidation, name="RevenueNameValidation"),
    path('validation/revnue/rate/', validation.RevenueRateValidation, name="RevenueRateValidation"),
    path('validation/sector/', validation.SectorValidation, name="SectorValidation"),

    # NOTIFICATION STREAMING
    path('streaming/stream/', services.DemandNoticeStream, name="DemandNoticeStream"),
    path('streaming/', services.stream, name="test_stream"),
]
