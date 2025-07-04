from django.urls import path
from payments.views import initiate_payment, paystack_verify, pay4it_initiate, pay4it_callback, pay4it_webhook

urlpatterns = [
    path('initiate-payment/', initiate_payment, name='initiate_payment'),
    path('verify-payment/<str:ref>/', paystack_verify, name='verify_payment'),
    # Pay4it
    path('initiate/', pay4it_initiate, name='initiate'),
    # path('verify/<str:ref>/', pay4it_callback, name='verify'),
    path('verify/', pay4it_callback, name='verify'),
    path('webhook/', pay4it_webhook, name='webhook'),
]

