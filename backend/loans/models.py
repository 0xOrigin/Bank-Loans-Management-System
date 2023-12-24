from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseBankModel


class LoanPlan(BaseBankModel):
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_months = models.PositiveIntegerField(verbose_name='Duration in months')

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
        ]

    def __str__(self) -> str:
        return f'{self.interest_rate}% ({self.minimum_amount} - {self.maximum_amount}) for {self.duration_in_months} month(s)'


class LoanStatus(models.TextChoices):
    PENDING = ('pending', _('Pending'))
    APPROVED = ('approved', _('Approved'))
    RELEASED = ('released', _('Released'))
    REJECTED = ('rejected', _('Rejected'))


class Loan(BaseBankModel):
    purpose = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan = models.ForeignKey('loans.LoanPlan', on_delete=models.CASCADE, related_name='loans')
    providers = models.ManyToManyField('authentication.LoanProvider', related_name='loans')
    customer = models.ForeignKey('authentication.LoanCustomer', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=LoanStatus.choices, default=LoanStatus.PENDING.value)
    is_active = models.BooleanField(default=True)
    is_amortized = models.BooleanField(default=False)
    total_payable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_payable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['plan']),
            models.Index(fields=['customer']),
        ]

    def set_monthly_payable_amount(self): # TODO: Move this to a serializer
        # Monthly Payment = Principal * Monthly Interest Rate * ((1 + Monthly Interest Rate) ^ Loan Duration in Months) 
        #                   / 
        #                   (((1 + Monthly Interest Rate) ^ Loan Duration in Months) - 1)
        monthly_interest_rate = self.plan.annual_interest_rate / 12
        first_part_of_equation = self.amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** self.plan.duration_in_months)
        second_part_of_equation = (((1 + monthly_interest_rate) ** self.plan.duration_in_months) - 1)
        self.monthly_payable_amount = first_part_of_equation / second_part_of_equation

    def set_total_payable_amount(self): # TODO: Move this to a serializer
        self.total_payable_amount = self.monthly_payable_amount * self.plan.duration_in_months

    def __str__(self) -> str:
        return f'{self.purpose} ({self.amount})'


class LoanPayment(BaseBankModel): # AKA Installment, or Amortization
    installment_number = models.PositiveIntegerField()
    loan = models.ForeignKey('loans.Loan', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    interest_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    principal_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_principal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['installment_number']),
            models.Index(fields=['loan']),
        ]

    def __str__(self) -> str:
        return f'{self.loan} ({self.amount})'
