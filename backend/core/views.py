from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter
from rest_framework.renderers import BrowsableAPIRenderer
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.paginations import BankPagination
from core.renderers import BankJSONRenderer


class BaseBankViewSet(viewsets.ModelViewSet):
    model = None
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = BankPagination
    renderer_classes = [BankJSONRenderer, BrowsableAPIRenderer]

    def get_queryset(self):
        if self.model is None:
            raise NotImplementedError(_('BaseBankViewSet must be subclassed with a model'))
        return self.model.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.pk, created_at=timezone.now())
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.pk, updated_at=timezone.now())
    
    def perform_destroy(self, instance):
        instance.deleted_by = self.request.user.pk
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_by', 'deleted_at'])


class NonUpdatableViewSet(viewsets.ModelViewSet):

    def update(self, request, *args, **kwargs):
        return Response({'detail': _('Method Not Allowed')}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': _('Method Not Allowed')}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class NonDeletableViewSet(viewsets.ModelViewSet):

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': _('Method Not Allowed')}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
