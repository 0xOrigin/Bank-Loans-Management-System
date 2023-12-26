from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.views import BaseBankViewSet, NonCreatableViewSet, NonUpdatableViewSet, NonDeletableViewSet
from authentication.models import UserRole
from loans.serializers import LoanPlanSerializer, LoanSerializer, LoanPaymentSerializer, AmortizationScheduleSerializer
from loans.models import LoanPlan, Loan, LoanPayment, LoanStatus
from loans.filters import LoanPaymentFilter
from loans.permissions import (
    ApproveLoanPermissions, RejectLoanPermissions, DisburseLoanPermissions,
    PayLoanPermissions, AmortizationSchedulePermissions
)


class LoanPlanViewSet(NonUpdatableViewSet, NonDeletableViewSet, BaseBankViewSet):
    model = LoanPlan
    queryset = model.objects.all()
    serializer_class = LoanPlanSerializer

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(bank_id=self.request.user.role_object.bank_id)
        )


class LoanViewSet(NonUpdatableViewSet, NonDeletableViewSet, BaseBankViewSet):
    model = Loan
    queryset = model.objects.all()
    serializer_class = LoanSerializer

    def get_queryset(self):
        queryset = (
            super().get_queryset()
            .filter(bank_id=self.request.user.role_object.bank_id)
            .select_related('plan', 'customer', 'provider')
        )
        if self.request.user.role == UserRole.LOAN_PROVIDER.value: # Loan provider can only see loans that they provided
            queryset = queryset.filter(provider=self.request.user.role_object)
        elif self.request.user.role == UserRole.LOAN_CUSTOMER.value: # Loan customer can only see loans that they applied for
            queryset = queryset.filter(customer=self.request.user.role_object)
        return queryset


class LoanApplicationViewSet(NonCreatableViewSet, LoanViewSet):

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == UserRole.BANK_PERSONNEL.value: # Bank personnel can only see loans that are pending approval
            queryset = queryset.filter(status=LoanStatus.PENDING.value)
        elif self.request.user.role == UserRole.LOAN_PROVIDER.value: # Loan provider can only see loans that are approved
            queryset = queryset.filter(status=LoanStatus.APPROVED.value)
        return queryset

    @action(detail=True, methods=['get',], url_path='approve', url_name='approve', permission_classes=[ApproveLoanPermissions])
    def approve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            updated_by=self.request.user, updated_at=timezone.now(),
            approved_at=timezone.now(), status=LoanStatus.APPROVED.value
        )
        return Response({'message': _('Loan approved')}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get',], url_path='reject', url_name='reject', permission_classes=[RejectLoanPermissions])
    def reject(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            updated_by=self.request.user, updated_at=timezone.now(),
            status=LoanStatus.REJECTED.value
        )
        return Response({'message': _('Loan rejected')}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get',], url_path='disburse', url_name='disburse', permission_classes=[DisburseLoanPermissions])
    def disburse(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            updated_by=self.request.user, updated_at=timezone.now(),
            disbursed_at=timezone.now(), status=LoanStatus.DISBURSED.value
        )
        return Response({'message': _('Loan disbursed')}, status=status.HTTP_200_OK)


class AmortizationScheduleViewSet(NonCreatableViewSet, NonUpdatableViewSet, NonDeletableViewSet, BaseBankViewSet):
    model = LoanPayment
    queryset = model.objects.all()
    permission_classes = [AmortizationSchedulePermissions]
    serializer_class = AmortizationScheduleSerializer
    filterset_class = LoanPaymentFilter

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(loan_id=self.kwargs['loan_pk'])
        )


class LoanPaymentViewSet(NonCreatableViewSet, NonUpdatableViewSet, NonDeletableViewSet, BaseBankViewSet):
    model = LoanPayment
    queryset = model.objects.all()
    permission_classes = [PayLoanPermissions]
    serializer_class = LoanPaymentSerializer

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(loan_id=self.kwargs['loan_pk'])
        )

    @action(detail=False, methods=['get',], url_path='next-payment', url_name='next-payment')
    def next_payment(self, request, loan_pk=None):
        instance = (
            self.get_queryset()
            .filter(is_paid=False, paid_at__isnull=True)
            .order_by('installment_number')
            .first()
        )
        serializer = self.get_serializer(instance)
        if instance is None:
            return Response({'message': _('No more payments to be made')}, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get',], url_path='pay', url_name='pay')
    def pay(self, request, loan_pk=None, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            updated_by=self.request.user, updated_at=timezone.now(),
            is_paid=True, paid_at=timezone.now()
        )
        return Response({'message': _('Loan payment successful')}, status=status.HTTP_200_OK)
