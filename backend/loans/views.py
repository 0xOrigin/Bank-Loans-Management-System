from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.views import BaseBankViewSet, NonCreatableViewSet, NonUpdatableViewSet, NonDeletableViewSet
from authentication.models import UserRole
from loans.serializers import LoanPlanSerializer, LoanSerializer, LoanPaymentSerializer
from loans.models import LoanPlan, Loan, LoanPayment, LoanStatus
from loans.permissions import ApproveLoanPermissions, RejectLoanPermissions, DisburseLoanPermissions


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


class LoanPaymentViewSet(NonUpdatableViewSet, NonDeletableViewSet, BaseBankViewSet):
    model = LoanPayment
    queryset = model.objects.all()
    serializer_class = LoanPaymentSerializer
