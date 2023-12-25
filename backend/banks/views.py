from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from core.views import BaseBankViewSet, NonCreatableViewSet, NonUpdatableViewSet, NonDeletableViewSet
from authentication.models import ApplicantStatus, LoanProvider, LoanCustomer
from authentication.serializers import LoanProviderSerializer, LoanCustomerSerializer
from banks.permissions import ApproveApplicantPermissions, RejectApplicantPermissions


class ApplicationViewSet(NonCreatableViewSet, NonUpdatableViewSet, NonDeletableViewSet, BaseBankViewSet):
    model = None

    def get_queryset(self):
        if self.model is None:
            raise NotImplementedError(_('ApplicationViewSet must be subclassed with a model'))
        return (
            super().get_queryset()
            .filter(
                bank_id=self.request.user.role_object.bank_id, status=ApplicantStatus.PENDING.value
            )
            .select_related('user')
        )
    
    @action(detail=True, methods=['get',], url_path='approve', url_name='approve', permission_classes=[ApproveApplicantPermissions])
    def approve(self, request, pk=None):
        instance = self.get_object()
        instance.status = ApplicantStatus.APPROVED.value
        instance.save(update_fields=['status'])
        return Response({'message': _('Application approved')}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get',], url_path='reject', url_name='reject', permission_classes=[RejectApplicantPermissions])
    def reject(self, request, pk=None):
        instance = self.get_object()
        instance.status = ApplicantStatus.REJECTED.value
        instance.save(update_fields=['status'])
        return Response({'message': _('Application rejected')}, status=status.HTTP_200_OK)


class LoanProviderApplicationViewSet(ApplicationViewSet):
    model = LoanProvider
    queryset = model.objects.all()
    serializer_class = LoanProviderSerializer


class LoanCustomerApplicationViewSet(ApplicationViewSet):
    model = LoanCustomer
    queryset = model.objects.all()
    serializer_class = LoanCustomerSerializer
