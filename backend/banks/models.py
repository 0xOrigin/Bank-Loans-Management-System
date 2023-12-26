from django.db import models
from core.models import BaseBankModel


class Bank(BaseBankModel):
    name_en = models.CharField(max_length=150)
    name_ar = models.CharField(max_length=150)
    total_funds = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    available_funds = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
        ]

    def __str__(self) -> str:
        return f'{self.name_en} ({self.name_ar})'


class Branch(BaseBankModel):
    name_en = models.CharField(max_length=150)
    name_ar = models.CharField(max_length=150)
    code = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='branches')

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['bank']),
        ]

    def __str__(self) -> str:
        return f'{self.name_en} ({self.name_ar}) - {self.bank}'
