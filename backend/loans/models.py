from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseBankModel


class LoanPlan(BaseBankModel):
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_months = models.PositiveIntegerField(verbose_name='Duration in months')
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='loan_plans')

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['bank']),
        ]

    def __str__(self) -> str:
        return f'{self.annual_interest_rate}% ({self.minimum_amount} - {self.maximum_amount}) for {self.duration_in_months} month(s)'


class LoanStatus(models.TextChoices):
    PENDING = ('pending', _('Pending'))
    APPROVED = ('approved', _('Approved'))
    RELEASED = ('released', _('Released'))
    DISBURSED = ('disbursed', _('Disbursed'))
    REJECTED = ('rejected', _('Rejected'))


class Loan(BaseBankModel):
    purpose = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    plan = models.ForeignKey('loans.LoanPlan', on_delete=models.CASCADE, related_name='loans')
    provider = models.ForeignKey('authentication.LoanProvider', on_delete=models.CASCADE, related_name='loans')
    customer = models.ForeignKey('authentication.LoanCustomer', on_delete=models.CASCADE, related_name='loans')
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='loans')
    status = models.CharField(max_length=20, choices=LoanStatus.choices, default=LoanStatus.PENDING.value)
    is_active = models.BooleanField(default=True)
    is_amortized = models.BooleanField(default=False)
    total_payable_amount = models.DecimalField(max_digits=16, decimal_places=2)
    monthly_payable_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['plan']),
            models.Index(fields=['customer']),
            models.Index(fields=['provider']),
            models.Index(fields=['bank']),
        ]
        permissions = [
            ('can_approve_loan', 'Can approve loan'),
            ('can_reject_loan', 'Can reject loan'),
            ('can_disburse_loan', 'Can disburse loan'),
        ]

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
        permissions = [
            ('can_pay_loan', 'Can pay loan'),
            ('can_view_amortization_schedule', 'Can view amortization schedule'),
        ]

    def __str__(self) -> str:
        return f'{self.loan} ({self.amount})'
