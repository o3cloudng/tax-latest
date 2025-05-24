from import_export import resources
from tax.models import Infrastructure


class InfrastructureResource(resources.ModelResource):

    def after_init_instance(self, instance, new, row, **kwargs):
        instance.created_by = kwargs.get('created_by')
        instance.company = kwargs.get('company')

    class Meta:
        model = Infrastructure
        # fields = (
        #     'infra_type', 'company', 'length','address','year_installed','created_by','upload_application_letter',
        #           'upload_asBuilt_drawing'
        #           )
        # import_id_fields = (
        #     'infra_type','company','length','address','year_installed','created_by','upload_application_letter',
        #           'upload_asBuilt_drawing'
        #           )
        
