from django.urls import path
from payments.views import initiate_payment, paystack_verify, Pay4ItInitiatePayment

urlpatterns = [
    path('initiate-payment/', initiate_payment, name='initiate_payment'),
    path('verify-payment/<str:ref>/', paystack_verify, name='verify_payment'),
    # Pay4it
    path('initiate/', Pay4ItInitiatePayment.as_view(), name='initiate'),
    path('verify/<str:ref>/', paystack_verify, name='verify'),
]

