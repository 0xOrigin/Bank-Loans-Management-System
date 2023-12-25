from rest_framework import serializers
from core.serializers import BaseBankSerializer
from loans.models import LoanPlan, Loan, LoanPayment


class LoanPlanSerializer(BaseBankSerializer):

    class Meta:
        model = LoanPlan
        exclude = BaseBankSerializer.Meta.exclude + ('bank',)


class LoanSerializer(BaseBankSerializer):

    class Meta:
        model = Loan
        exclude = BaseBankSerializer.Meta.exclude


class LoanPaymentSerializer(BaseBankSerializer):

    class Meta:
        model = LoanPayment
        exclude = BaseBankSerializer.Meta.exclude
