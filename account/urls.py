from django.urls import path
from agency.view import validation

from account.views import userlogin, signup, logout_user, setup_profile, forgot_password,change_password

urlpatterns = [
    path('', userlogin, name="login"),
    path('signup/', signup, name="signup"),
    path('logout/', logout_user, name="logout_user"),
    # path('dashboard/', dashboard, name="dashboard"),
    path('setup_profile/', setup_profile, name="setup_profile"),
    path('settings/', setup_profile, name="settings"),
    path('forgot_password/', forgot_password, name="forgot_password"),
    path('change_password/', change_password, name="change_password"),

    # Profile Validation
    path('validation/rc_number/', validation.ProfileRCValidation, name="ProfileRCValidation"),
    path('validation/phone/', validation.PhoneValidation, name="PhoneValidation"),
]
