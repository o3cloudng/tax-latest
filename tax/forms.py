from django import forms
from tax.models import InfrastructureType, Waiver, Remittance, Infrastructure
from django.urls import reverse_lazy


class InfrastructureForm(forms.ModelForm):
    class Meta:
        model = Infrastructure
        fields = ['infra_type', 'address', 'year_installed', 'upload_application_letter', 'upload_asBuilt_drawing']

        widgets = {
            'infra_type': forms.Select(
                # choices = InfrastructureType.objects.all(), 
                attrs={
                'style': 'max-width: 150px;',
                'required': True,
                'placeholder': 'Infrastructure Type'
                }),
            'year_installed': forms.NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100%',
                'placeholder': 'Year',
                'required': False,
                'type': "number"
                }),
            'address': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 150px;',
                'required': True,
                'placeholder': 'Address'
                }),
            'upload_application_letter': forms.FileInput(attrs={
                'class': "form-control",
                'style': 'max-width: 150px;',
                'required': False,
                'accept': '.pdf,.jpg,.png,.gif',
                'placeholder': 'Upload application letter'
                }),
            'upload_asBuilt_drawing': forms.FileInput(attrs={
                'class': "form-control",
                'style': 'max-width: 150px;',
                'required': False,
                'accept': '.pdf,.jpg,.png,.gif',
                'placeholder': 'Upload as-built drawing'
                })
        }

    def __init__(self, *args, **kwargs):
        #  question_id = kwargs.pop('question_id')
        # self.referenceid = referenceid
        super().__init__(*args, **kwargs)
        self.fields['infra_type'] = forms.ModelChoiceField(
            queryset=InfrastructureType.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
         )


class InfrastructureForm2(forms.ModelForm):
    class Meta:
        model = Infrastructure
        fields = ['infra_type', 'length', 'address', 'year_installed', 'upload_application_letter',
                  'upload_asBuilt_drawing']

        widgets = {
            'infra_type': forms.Select(
                # choices = InfrastructureType.objects.all(), 
                attrs={
                'class': "border-2 border-rose-600",
                'style': 'border:2px solid #999; width:100%',
                'required': True,
                'placeholder': 'Infrastructure Type'
                }),
            'year_installed': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 100%',
                'placeholder': 'Length',
                'required': False,
                'type': "text"
                }),
            'length': forms.TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 150px;',
                'placeholder': 'Length',
                'required': True,
                'type': "text"
                }),
            'address': forms.TextInput(attrs={
                'class': "",
                'style': 'border:2px solid #999;',
                'required': True,
                'placeholder': 'Address'
                }),
            'upload_application_letter': forms.HiddenInput(attrs={
                'class': "form-control",
                'style': 'border:2px solid #999;',
                'required': False,
                'accept': '.pdf,.jpg,.png,.gif',
                'placeholder': 'Upload application letter'
                }),
            'upload_asBuilt_drawing': forms.HiddenInput(attrs={
                'class': "form-control",
                'style': 'max-width: 150px;',
                'required': False,
                'accept': '.pdf,.jpg,.png,.gif',
                'placeholder': 'Upload as-built drawing'
                })
        }

    def __init__(self, *args, **kwargs):
        #  question_id = kwargs.pop('question_id')
        # self.referenceid = referenceid
        super().__init__(*args, **kwargs)
        self.fields['infra_type'] = forms.ModelChoiceField(
            queryset=InfrastructureType.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
         )


class InfrastructureTypeForm(forms.ModelForm):
    class Meta:
        model = Infrastructure
        fields = ['infra_type']

        widgets = {
            'infra_type': forms.Select(
                # choices = InfrastructureType.objects.all(), 
                attrs={
                'class': "form-control",
                'style': 'max-width: 150px;',
                'required': True,
                'placeholder': 'Infrastructure Type'
                }),
            }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['infra_type'] = forms.ModelChoiceField(
                queryset=InfrastructureType.objects.all(),
                widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
            )

# class PermitForm(forms.ModelForm):
#     class Meta:
#         model = Permit
#         fields = ['infra_type', 'amount', 'add_from', 'add_to', 'length', 'upload_application_letter',
#                   'upload_asBuilt_drawing', 'upload_payment_receipt']
        

#         widgets = {
#             'infra_type': forms.Select(
#                 # choices = InfrastructureType.objects.all(), 
#                 attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': True,
#                 'placeholder': 'Infrastructure Type'
#                 }),
#             'amount': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Amount',
#                 'value': 0,
#                 'type': "text"
#                 }),
#             'length': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'placeholder': 'Length',
#                 'required': False,
#                 'type': "text"
#                 }),
#             'add_from': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Address'
#                 }),
#             'upload_application_letter': forms.FileInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Upload application letter'
#                 }),
#             'upload_asBuilt_drawing': forms.FileInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Upload as-built drawing'
#                 })
#             # 'upload_payment_receipt': forms.FileInput(attrs={
#             #     'class': "form-control",
#             #     'style': 'max-width: 150px;',
#             #     'required': False,
#             #     'placeholder': 'Upload payment receipt'
#             #     })
#         }

#     def __init__(self, *args, **kwargs):
#         #  question_id = kwargs.pop('question_id')
#         # self.referenceid = referenceid
#         super().__init__(*args, **kwargs)
#         self.fields['infra_type'] = forms.ModelChoiceField(
#             queryset=InfrastructureType.objects.all(),
#             widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
#          )
#     # def __init__(self, *args, your_important_var=None, **kwargs):
#     #     self.your_important_var = your_important_var
#     #     super().__init__(*args, **kwargs)


# class PermitExForm(forms.ModelForm):
#     class Meta:
#         model = Permit
#         fields = ['infra_type', 'amount', 'length',  'add_from', 'upload_application_letter',
#                   'upload_asBuilt_drawing']

#         widgets = {
#             'infra_type': forms.Select(
#                 attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': True,
#                 'placeholder': 'Infrastructure Type'
#                 }),
#             'amount': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Amount',
#                 'value': 0,
#                 'type': "text"
#                 }),
#             'length': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'placeholder': 'Length',
#                 'required': False,
#                 'type': "text"
#                 }),
#             'add_from': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Address'
#                 }),
#             'upload_application_letter': forms.FileInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Upload application letter'
#                 }),
#             'upload_asBuilt_drawing': forms.FileInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Upload as-built drawing'
#                 })
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['infra_type'] = forms.ModelChoiceField(
#             queryset=InfrastructureType.objects.all(),
#             widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
#          )
#     # def __init__(self, *args, your_important_var=None, **kwargs):
#     #     self.your_important_var = your_important_var
#     #     super().__init__(*args, **kwargs)

# class PermitEditForm(forms.ModelForm):
#     class Meta:
#         model = Permit
#         fields = ['infra_type', 'referenceid', 'amount', 'add_from', 'length', 'upload_application_letter',
#                   'upload_asBuilt_drawing', 'upload_payment_receipt', 'is_disputed', 'is_revised', 'is_paid']

#         widgets = {
#             'infra_type': forms.Select(
#                 # choices = InfrastructureType.objects.all(), 
#                 attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': True,
#                 'placeholder': 'Infrastructure Type'
#                 }),
#             'amount': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Amount',
#                 'type': "text"
#                 }),
#             'referenceid': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': True,
#                 'placeholder': 'Amount',
#                 'type': "hidden"
#                 }),
#             'length': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'placeholder': 'Length',
#                 'required': False,
#                 'type': "text"
#                 }),
#             'add_from': forms.TextInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Address from'
#                 }),
#             'upload_application_letter': forms.FileInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Upload application letter'
#                 }),
#             'upload_asBuilt_drawing': forms.FileInput(attrs={
#                 'class': "form-control",
#                 'style': 'max-width: 150px;',
#                 'required': False,
#                 'placeholder': 'Upload as-built drawing'
#                 })
#         }

#     def __init__(self, *args, **kwargs):
#          super().__init__(*args, **kwargs)
#          self.fields['infra_type'] = forms.ModelChoiceField(
#              queryset=InfrastructureType.objects.all(),
#              widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder':'Infrastructure'})
#          )


class WaiverForm(forms.ModelForm):
    class Meta:
        model = Waiver
        fields = ['referenceid', 'company', 'wave_amount']

        widgets = {
            'referenceid': forms.TextInput(
                attrs={
                'class': "form-control",
                'style': 'max-width: 100%;',
                'required': False,
                'type': 'hidden'
                }),
            'company': forms.TextInput(
                attrs={
                'class': "form-control",
                'style': 'max-width: 100%;',
                'required': False,
                'type': 'hidden'
                }),
            'wave_amount': forms.TextInput(
                attrs={
                'class': "form-control",
                'style': 'max-width: 100%;',
                'required': True,
                'placeholder': 'Amount paid'
                })
        }


class RemittanceForm(forms.ModelForm):
    class Meta:
        model = Remittance
        fields = ['referenceid', 'remitted_amount', 'receipt']

        widgets = {
            'referenceid': forms.TextInput(
                attrs={
                'class': "form-control",
                'style': 'max-width: 100%;',
                'required': False,
                'type': 'hidden'
                }),
            'remitted_amount': forms.TextInput(
                attrs={
                'class': "form-control",
                'style': 'max-width: 100%;',
                'required': True,
                'placeholder': 'eg 5000000'
                }),
            'apply_for_waver': forms.BooleanField(required=False, initial=False, label='Apply for waver'),
            'receipt': forms.FileInput(
                attrs={
                'class': "form-control",
                'style': 'max-width: 300px; margin-right:10px',
                'required': True,
                'accept': '.pdf,.jpg,.png,.gif',
                'placeholder': 'Upload receipt'
                })
        }


class PermitUploadForm(forms.Form):
    class Meta:
        fields = ['upload_csv_xlxs']

        widgets = {
            'upload_csv_xlxs': forms.HiddenInput( # id="dropzone-file" name="upload_csv_xlxs" type="file" class="hidden"
                attrs={
                'id': "dropzone-file",
                'required': True
                })
        }

class BulkUploadForm(forms.Form):
    bulk_upload = forms.FileField()