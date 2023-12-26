from django_filters.rest_framework import FilterSet, filters
from loans.models import Loan, LoanPayment



class LoanFilter(FilterSet):

    class Meta:
        model = Loan
        fields = {
            'purpose': ['exact', 'icontains'],
            'amount': ['exact', 'gte', 'lte'],
            'plan': ['exact',],
            'status': ['exact',],
            'is_active': ['exact',],
            'is_amortized': ['exact',],
            'approved_at': ['exact', 'gte', 'lte'],
            'disbursed_at': ['exact', 'gte', 'lte'],
        }


class LoanPaymentFilter(FilterSet):

    class Meta:
        model = LoanPayment
        fields = {
            'installment_number': ['exact', 'gte', 'lte'],
            'is_paid': ['exact',],
            'paid_at': ['exact', 'gte', 'lte'],
        }
