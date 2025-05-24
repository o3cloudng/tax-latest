from django import forms
from django.contrib.auth.forms import UserCreationForm
from account.models import User, Sector
from django.urls import reverse_lazy


class SignupForm(UserCreationForm):
    
    email = forms.EmailField(max_length=255, required=True, 
                                widget=forms.widgets.Input(
            attrs={"placeholder": "Enter email address.", "type":"email","class": "bg-white py-3 focus:bg-white label text-sm !text-gray-600", }),
            label="Email address",)
    phone_number = forms.CharField(max_length=50, required=True, 
                                widget=forms.widgets.Input(
            attrs={"placeholder": "Enter phone number.", "type":"text", "class": "bg-white py-3 focus:bg-white label text-sm text-gray-600", }),
            label="Phone number",)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Enter password","type":"password","class": "bg-white py-3 label text-sm text-gray-600", }),
                                label="Enter password",)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm password","type":"password", "class": "bg-white py-3 focus:bg-white label text-sm text-gray-600", }),
                                label="Confirm password",)


    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password1', 'password2']


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=63, widget=forms.widgets.Input(
            attrs={"placeholder": "Enter email.","class": "w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-4", }),)
    password = forms.CharField(max_length=63,  widget=forms.PasswordInput(
        attrs={"placeholder": "**********","class": "mt-2 w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-4", }),)



class ProfileForm(forms.ModelForm):
    company_name = forms.CharField(max_length=50, required=True,
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Enter company name.",
                "class": "!w-full", 
                }),
            label="Company name",)
    address = forms.CharField(max_length=50, required=True,
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Enter company address.",
                "class": "w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-2 label text-sm text-gray600", }),
            label="Company address",)
    rc_number = forms.CharField(
        required=True,
        widget=forms.widgets.Input(
            attrs={
                "placeholder": "Enter RC Number.",
                "class": "!w-full", }),
            label="RC Number",)
    email = forms.EmailField(max_length=255, required=True, 
                                widget=forms.widgets.Input(
            attrs={"placeholder": "Enter email address.","class": "w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-2 label text-sm text-gray600", }),
            label="Email address", disabled=True)
    phone_number = forms.CharField(max_length=50, required=True, 
                                widget=forms.widgets.Input(
            attrs={"placeholder": "Enter phone number.","class": "w-full input input-bordered input-md bg-white block py-1 sm:text-sm sm:leading-2 label text-sm text-gray600", }),
            label="Phone number",)
    
    class Meta:
        model = User
        fields = ['company_name', 'address', 'rc_number', 'phone_number', 'email']
        
 

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'sector', 'company_name', 'rc_number', 'phone_number', 'country', 'address',
                  'company_logo', 'bio_data']

        widgets = {
             'sector': forms.Select(
                attrs={
                'class': "form-control",
                'required': True,
                'placeholder': 'Sector'
                }),
            'email': forms.TextInput(
                attrs={
                'class': "form-control",
                'required': True,
                'placeholder': 'Contact Email'
                }),
            'company_name': forms.TextInput(attrs={
                'class': "form-control",
                'required': False,
                'placeholder': 'Company name'
                }),
            'rc_number': forms.TextInput(attrs={
                'hx-get': reverse_lazy('ProfileRCValidation'),
                'hx-target': '#rc-number-error',
                'hx-trigger': 'input changed delay:500ms, rc_number',
                'hx-swap': 'innerHTML',
                'class': "form-control !w-full",
                'placeholder': 'RC Number',
                'required': False
                }),
            'phone_number': forms.TextInput(attrs={
                'hx-get': reverse_lazy('PhoneValidation'),
                'hx-target': '#phone-error',
                'hx-trigger': 'input changed delay:500ms, rc_number',
                'hx-swap': 'innerHTML',
                'class': "form-control",
                'required': False,
                'placeholder': 'Phone number'
                }),
            'country': forms.TextInput(attrs={
                'class': "form-control",
                'required': False,
                'placeholder': 'Country'
                }),
            # 'state': forms.TextInput(attrs={
            #     'class': "form-control",
            #     'required': False,
            #     'placeholder': 'State'
            #     }),
            'address': forms.TextInput(attrs={
                'class': "form-control",
                'required': False,
                'placeholder': 'Address'
                }),
            # 'postal_code': forms.TextInput(attrs={
            #     'class': "form-control",
            #     'required': False,
            #     'placeholder': 'Postal code'
            #     }),
            'bio_data': forms.Textarea(attrs={
                'class': "form-control",
                'required': False,
                'style': 'max-height: 100px;',
                'placeholder': 'Company bio data'
                }),
            # 'date_enrolled': forms.DateInput(attrs={
            #     'class': "form-control",
            #     'required': True,
            #     'placeholder': 'Date enrolled',
            #     'type':"Date"
            #     }),
        }
        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields['infra_type'] = forms.ModelChoiceField(
                queryset=Sector.objects.all(),
                widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
                )