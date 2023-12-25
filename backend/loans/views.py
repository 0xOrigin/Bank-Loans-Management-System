from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from core.views import BaseBankViewSet
from loans.serializers import LoanPlanSerializer, LoanSerializer, LoanPaymentSerializer
from loans.models import LoanPlan, Loan, LoanPayment


class LoanPlanViewSet(BaseBankViewSet):
    model = LoanPlan
    queryset = model.objects.all()
    serializer_class = LoanPlanSerializer


class LoanViewSet(BaseBankViewSet):
    model = Loan
    queryset = model.objects.all()
    serializer_class = LoanSerializer


class LoanPaymentViewSet(BaseBankViewSet):
    model = LoanPayment
    queryset = model.objects.all()
    serializer_class = LoanPaymentSerializer
