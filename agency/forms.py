from django import forms
from django.contrib.auth.forms import UserCreationForm
from account.models import User, AdminSetting
from tax.models import InfrastructureType, DemandNotice
from agency.models import Agency, Notification
from django.urls import reverse_lazy
from account.models import Sector


class SectorForm(forms.ModelForm):
    name = forms.CharField(
        max_length=255,
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                'hx-get': reverse_lazy('SectorValidation'),
                'hx-target': '#sector-error',
                'hx-trigger': 'input changed delay:500ms, infra_name',
                'hx-swap': 'innerHTML',
                "placeholder": "Enter agency name", 
                "type":"text",
                "class": "w-full py-4", 
                "required": True, 
                }),
            )
    class Meta:
        model = Sector
        fields = ['name']

class AddUserForm(UserCreationForm):
    USER_TYPE_CHOICES =( 
        (0, "Company"), 
        (1, "Agency Admin 1"), 
        (1, "Agency Admin 2"), 
        (1, "Agency Admin 3"), 
    ) 
    is_tax_admin = forms.ChoiceField(
        choices = USER_TYPE_CHOICES,
        required=True, 
        widget=forms.widgets.Select(
            attrs={
                "placeholder": "Choose a user type", 
                "type":"text",
                "class": "w-full py-4", 
                }),
            )
    company_name = forms.CharField(
        max_length=255,
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Company name", 
                # "hx-post": reverse_lazy("validate_name"),
                # "hx-target": "#usernameError",
                # "hx-trigger": "keyup[target.value.length > 3]",
                "type":"text",
                "class": "w-full py-4", 
                }),
            )
    email = forms.EmailField(
        max_length=255, 
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                 "placeholder": "Company email", 
                 "type":"email",
                 "class": "w-full py-4", 
                 }),
            label="Email address",)
    password1 = forms.CharField(
        max_length=50,
        required=True, 
        widget=forms.PasswordInput(
            attrs={
                  "placeholder": "Enter password",
                  "type":"password",
                  "class": "w-full py-4",
                  }),)
    password2 = forms.CharField(
        max_length=50,
        required=True, 
        widget=forms.PasswordInput(
            attrs={
                  "placeholder": "Confirm password",
                  "type":"password",
                  "class": "w-full py-4",
                  }),)

    class Meta:
        model = User
        fields = ['company_name', 'email', 'password1', 'password2', 'company_logo', 'is_tax_admin']


class AgencyForm(forms.ModelForm):
    agency_name = forms.CharField(
        max_length=255,
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Enter agency name", 
                "type":"text",
                "class": "w-full py-4", 
                "required": True, 
                }),
            )
    agency_email = forms.EmailField(
        max_length=255, 
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                 "placeholder": "Enter agency email", 
                 "type":"email",
                 "class": "w-full py-4", 
                 "requires": True,
                 }),
            label="Email address",)
    phone_number = forms.CharField(
        max_length=50, 
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                 "placeholder": "Enter agency phone number", 
                 "type":"text", 
                 "class": "w-full py-4", 
                 }),
            label="Phone number",)
    address = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Enter agency office address",
                "type":"text", 
                "class": "w-full py-4", }),)
    agency_logo = forms.ImageField()

    class Meta:
        model = Agency
        fields = ['agency_name', 'address', 'agency_email', 'phone_number', 'agency_logo']


class InfrastructureSettingsForm(forms.ModelForm):

    # def clean_infra_name(self):
    #     infra_name = self.cleaned_data['infra_name']
    #     if InfrastructureType.objects.filter(infra_name=infra_name).exists():
    #         raise forms.ValidationError(f"{infra_name} already exisits")
    #     return infra_name
    
    infra_name = forms.CharField(
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                'hx-get': reverse_lazy('InfraTypeValidation'),
                'hx-target': '#infra-type-error',
                'hx-trigger': 'input changed delay:500ms, infra_name',
                'hx-swap': 'innerHTML',
                'class': "form-control",
                "placeholder": "Infrastructure name", 
                "type":"text",
                "class": "w-full py-4", 
                }),
            )
    rate = forms.CharField(
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                'hx-get': reverse_lazy('RateValidation'),
                'hx-target': '#rate-error',
                'hx-trigger': 'input changed delay:500ms, infra_name',
                'hx-swap': 'innerHTML',
                "placeholder": "Amount", 
                "type":"text",
                "class": "border-0 focus:ring-0 bg-transparent", 
                }),
            )
    class Meta:
        model = InfrastructureType
        fields = ['infra_name', 'rate']


class RevenueForm(forms.ModelForm):
    name = forms.CharField(
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                'hx-get': reverse_lazy('RevenueNameValidation'),
                'hx-target': '#revenue-name-error',
                'hx-trigger': 'input changed delay:500ms, infra_name',
                'hx-swap': 'innerHTML',
                "placeholder": "Revenue type", 
                "type":"text",
                "class": "w-full py-4", 
                }),
            )
    description = forms.CharField(
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Description", 
                "type":"text",
                "class": "w-full py-4", 
                }),
            )
    rate = forms.ChoiceField(
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                'hx-get': reverse_lazy('RevenueRateValidation'),
                'hx-target': '#revenue-rate-error',
                'hx-trigger': 'input changed delay:500ms, infra_name',
                'hx-swap': 'innerHTML',
                "placeholder": "Amount", 
                "type":"text",
                "class": "border-0 focus:ring-0 bg-transparent", 
                }),
            )
    class Meta:
        model = AdminSetting
        fields = ['name', 'rate']


class NotificationForm(forms.ModelForm):
    NOTICES_CHOICES =( 
        ("new-account", "New account"), 
        ("default_notification", "Default notification"), 
        ("change-of-password", "Change of password"), 
        ("tax-payers-account", "Tax payer account"), 
    ) 
    notification = forms.ChoiceField(
        choices = NOTICES_CHOICES,
        required=True, 
        widget=forms.widgets.Select(
            attrs={
                "placeholder": "Select infrastructure", 
                "type":"text",
                "class": "w-full py-4", 
                }),
            )
    message = forms.CharField(
        max_length=500,
        required=True, 
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Message ", 
                "type":"text",
                "class": "w-full py-4", 
                }),
            )
    class Meta:
        model = Notification
        fields = ['notification', 'message']


class WaiverForm(forms.ModelForm):
    class Meta:
        model = DemandNotice
        fields = ['waiver_applied']

# class ProfileForm(forms.ModelForm):
#     company_name = forms.CharField(max_length=50, required=True,
#         widget=forms.widgets.Input(
#             attrs={
#                 "placeholder": "Enter company name.",
#                 "class": "!w-full", 
#                 }),
#             label="Company name",)
#     address = forms.CharField(max_length=50, required=True,
#         widget=forms.widgets.Input(
#             attrs={
#                 "placeholder": "Enter company address.",
#                 "class": "w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-2 label text-sm text-gray600", }),
#             label="Company address",)
#     rc_number = forms.CharField(
#         required=True,
#         widget=forms.widgets.Input(
#             attrs={
#                 "placeholder": "Enter RC Number.",
#                 "class": "!w-full", }),
#             label="RC Number",)
#     email = forms.EmailField(max_length=255, required=True, 
#                                 widget=forms.widgets.Input(
#             attrs={"placeholder": "Enter email address.","class": "w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-2 label text-sm text-gray600", }),
#             label="Email address", disabled=True)
#     phone_number = forms.CharField(max_length=50, required=True, 
#                                 widget=forms.widgets.Input(
#             attrs={"placeholder": "Enter phone number.","class": "w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-2 label text-sm text-gray600", }),
#             label="Phone number",)
    
#     class Meta:
#         model = User
#         fields = ['company_name', 'address', 'rc_number', 'phone_number', 'email']
        
 

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['email', 'sector', 'company_name', 'rc_number', 'phone_number', 'country', 'address',
#                   'company_logo', 'bio_data']

#         widgets = {
#              'sector': forms.Select(
#                 attrs={
#                 'class': "form-control",
#                 'required': True,
#                 'placeholder': 'Sector'
#                 }),
#             'email': forms.TextInput(
#                 attrs={
#                 'class': "form-control",
#                 'required': True,
#                 'placeholder': 'Contact Email'
#                 }),
#             'company_name': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'required': False,
#                 'placeholder': 'Compnay name'
#                 }),
#             'rc_number': forms.TextInput(attrs={
#                 'class': "form-control !w-full",
#                 'placeholder': 'RC Number',
#                 'required': False
#                 }),
#             'phone_number': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'required': False,
#                 'placeholder': 'Phone number'
#                 }),
#             'country': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'required': False,
#                 'placeholder': 'Country'
#                 }),
#             # 'state': forms.TextInput(attrs={
#             #     'class': "form-control",
#             #     'required': False,
#             #     'placeholder': 'State'
#             #     }),
#             'address': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'required': False,
#                 'placeholder': 'Address'
#                 }),
#             # 'postal_code': forms.TextInput(attrs={
#             #     'class': "form-control",
#             #     'required': False,
#             #     'placeholder': 'Postal code'
#             #     }),
#             'bio_data': forms.Textarea(attrs={
#                 'class': "form-control",
#                 'required': False,
#                 'style': 'max-height: 100px;',
#                 'placeholder': 'Company bio data'
#                 }),
#             # 'date_enrolled': forms.DateInput(attrs={
#             #     'class': "form-control",
#             #     'required': True,
#             #     'placeholder': 'Date enrolled',
#             #     'type':"Date"
#             #     }),
#         }
#         def __init__(self, *args, **kwargs):
#                 super().__init__(*args, **kwargs)
#                 self.fields['infra_type'] = forms.ModelChoiceField(
#                 queryset=Sector.objects.all(),
#                 widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
#                 )