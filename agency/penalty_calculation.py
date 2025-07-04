from account.models import AdminSetting
# from tax.models import Permit
from django.db.models import (F, ExpressionWrapper,
                                IntegerField, Value, Case, When)
from django.db.models.functions import Now


# def penalty_calculation():
#     penalty_sum = Permit.objects.annotate(
#         age_in_days = ExpressionWrapper(
#             (Now() - F('year_installed')) / 86400000000,
#             # ExtractDay(Now() - F('year_installed')),
#             output_field=IntegerField()
#         ),

#         penalty_rate = Value(AdminSetting.objects.get(slug="penalty").rate),

#         infra_count =  Case(
#                 When(length=0, then=F('amount')),
#                 default=Value(1),
#                 output_field=IntegerField(),
#         ),
#         # Calculate penalty based on age in days and the daily penalty fee
#         penalty = ExpressionWrapper(
#             F('age_in_days') * F('penalty_rate') * F('infra_count'),
#             output_field=IntegerField()
#         )
#     )
#     return penalty_sum

# def agency_penalty_calculation():
#     penalty_sum = Permit.objects.annotate(
#         age_in_days = ExpressionWrapper(
#             (Now() - F('year_installed')) / 86400000000,
#             # ExtractDay(Now() - F('year_installed')),
#             output_field=IntegerField()
#         ),

#         penalty_rate = Value(AdminSetting.objects.get(slug="penalty").rate),

#         infra_count =  Case(
#                 When(length=0, then=F('amount')),
#                 default=Value(1),
#                 output_field=IntegerField(),
#         ),
#         # Calculate penalty based on age in days and the daily penalty fee
#         penalty = ExpressionWrapper(
#             F('age_in_days') * F('penalty_rate') * F('infra_count'),
#             output_field=IntegerField()
#         )
#     )
#     return penalty_sum


# def cal_infrastructure():
#     total_infra_count = Permit.objects.annotate(
#         mast_roof_count = ExpressionWrapper(
#             (F('amount')),
#             output_field=IntegerField()
#         ),

#         penalty_rate = Value(AdminSetting.objects.get(slug="penalty").rate),

#         infra_count =  Case(
#                 When(F(infra_type__infra_name__icontains='mast'), then=F('amount')),
#                 default=Value(1),
#                 output_field=IntegerField(),
#         ),
#         # Calculate penalty based on age in days and the daily penalty fee
#         penalty = ExpressionWrapper(
#             F('age_in_days') * F('penalty_rate') * F('infra_count'),
#             output_field=IntegerField()
#         )
#     )
#     return total_infra_count
