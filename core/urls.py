
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from core import services

from django.conf.urls import handler404

handler404 = 'tax.views.page_view.handler404'

# Sentry
# def trigger_error(request):
#     division_by_zero = 1 / 0

admin.autodiscover()

urlpatterns = [
    path('', services.landingPage, name="landingPage"),
    path('admin/', admin.site.urls),
    path('clients/', include("account.urls")),
    path('tax/', include("tax.urls")),
    path('payments/', include("payments.urls")),
    path('agency/', include("agency.urls")),
    # path('adminarea/', include("admin.urls")),
    # path('sentry-debug/', trigger_error),
]


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  
    # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()