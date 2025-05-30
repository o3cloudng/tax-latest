from django.db import models
from account.models import User
from datetime import datetime
# import timezone
# from simple_history.models import HistoricalRecords
from core.reference_id import generate_ref_id


class InfrastructureType(models.Model):
    infra_name = models.CharField(max_length=200, null=False)
    rate = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.infra_name

    

class Infrastructure(models.Model):
    infra_type = models.ForeignKey(InfrastructureType, related_name="infra_type", on_delete=models.CASCADE)
    company = models.ForeignKey(User, related_name="com", on_delete=models.CASCADE)
    length = models.IntegerField(null=True, default=0)
    address = models.CharField(max_length=200, blank=True)
    created_by = models.CharField(max_length=200, blank=True)
    year_installed = models.PositiveIntegerField(default=datetime.now().year)
    upload_application_letter = models.FileField(upload_to='uploads/applications/', blank=True, null=True)
    upload_asBuilt_drawing = models.FileField(upload_to='uploads/drawings/', blank=True, null=True)
    is_existing = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    referenceid=models.CharField(max_length=20, null=True)
    cost = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # history = HistoricalRecords()
    # penalty calculations
    def __str__(self):
        return f"{self.company} - ({self.infra_type})"



# class Reference(models.Model):
#     """Generate unique reference numbers for other models.

#     The only purpose of this model is to generate unique reference numbers.
#     """
#     # Django models need at least 1 field
#     created_date = models.DateTimeField(auto_now_add=True)

#     @classmethod
#     def generate(cls, prefix: str) -> str:
#         """Generate a unique reference number prefixed with the provided prefix.

#         For example, you could generate an invoice number as follows:

#         Reference.generate(prefix="INV") # INV-000001 etc.
#         """

#         instance = cls.objects.create()
#         suffix = f"{instance.pk}".zfill(6)
#         return f"{prefix}{suffix}"

class DemandNotice(models.Model):
    PAY_CHOICES = (
        ("DEMAND NOTICE", "Demand Notice"),
        ("UNDISPUTED UNPAID", "Undisputed Unpaid"),
        ("UNDISPUTED PAID", "Undisputed Paid"),
        ("REVISED", "Revised"),
        ("RESOLVED", "Resolved"),
    )
    referenceid = models.CharField(max_length=200, null=True, unique=True) 
    # referenceid = Reference.generate(prefix="LA")
    company = models.ForeignKey(User, related_name="company", on_delete=models.CASCADE, null=True)
    is_exisiting = models.BooleanField(default=False)
    infra = models.CharField(max_length=1000)
    amount_due = models.PositiveIntegerField(default=0)
    subtotal = models.PositiveIntegerField(default=0)
    penalty = models.PositiveIntegerField(default=0)
    application_fee = models.PositiveIntegerField(default=0)
    admin_fee = models.PositiveIntegerField(default=0)
    site_assessment = models.PositiveIntegerField(default=0)
    annual_fee = models.PositiveIntegerField(default=0)
    remittance = models.PositiveIntegerField(default=0)
    waiver_applied = models.PositiveIntegerField(default=0)
    amount_paid = models.PositiveIntegerField(default=0)
    total_due = models.IntegerField(default=0)

    status = models.CharField(max_length=30, choices=PAY_CHOICES, default="UNPAID")
    created_by = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # history = HistoricalRecords()

def save(self, *args, **kwargs):
    self.updated_at = datetime.now()
    if self.pk:
        original = DemandNotice.objects.get(pk=self.pk)
        if original.remittance != self.remittance or original.waiver_applied != self.waiver_applied:
            self.total_due = self.calculated_total_due()
    else:
        self.total_due = self.calculated_total_due()
    self.amount_due = self.total_due
    super(DemandNotice, self).save(*args, **kwargs)

    def calculated_total_due(self):
        self.total_due = self.subtotal + self.penalty + self.application_fee + self.admin_fee + \
            self.site_assessment - self.remittance - self.waiver_applied + self.annual_fee
        return self.total_due
    
    def cal_referenceid(self):
        self.referenceid = generate_ref_id()
        return self.referenceid

    # def update(self, *args, **kwargs):
    #     self.total_due = self.subtotal + self.penalty + self.application_fee + self.admin_fee + self.site_assessment - self.remittance - self.waiver
    #     super(DemandNotice, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.id}"



class Waiver(models.Model):
    referenceid = models.CharField(max_length=20)
    company = models.ForeignKey(User, related_name="companyid", on_delete=models.CASCADE)
    wave_amount = models.IntegerField(default=0)
    receipt = models.FileField(upload_to='uploads/receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.wave_amount}"


class Remittance(models.Model):
    referenceid = models.CharField(max_length=20)
    company = models.ForeignKey(User, related_name="remit_comp", on_delete=models.CASCADE)
    remitted_amount = models.IntegerField(blank=True)
    receipt = models.FileField(upload_to='uploads/receipts/', blank=True, null=True)
    approved = models.BooleanField(default=False)
    apply_for_waver = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.referenceid} - {self.remitted_amount}"
