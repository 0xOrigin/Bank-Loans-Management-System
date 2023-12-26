from django_filters.rest_framework import FilterSet, filters
from loans.models import LoanPayment


class LoanPaymentFilter(FilterSet):

    class Meta:
        model = LoanPayment
        fields = {
            'installment_number': ['exact', 'gte', 'lte'],
            'is_paid': ['exact',],
            'paid_at': ['exact', 'gte', 'lte'],
        }
