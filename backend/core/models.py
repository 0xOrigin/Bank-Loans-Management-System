import uuid
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class BankQuerySet(models.QuerySet):

    def not_deleted(self):
        return self.filter(deleted_at__isnull=True)

    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class BankManager(models.Manager):

    def get_queryset(self):
        return BankQuerySet(self.model, using=self._db).not_deleted()


class BaseAuditModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Created at'))
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Updated at'))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Deleted at'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_created_by', verbose_name=_('Created by'))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_updated_by', verbose_name=_('Updated by'))
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='%(class)s_deleted_by', verbose_name=_('Deleted by'))

    objects = BankManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class BaseBankModel(BaseAuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
