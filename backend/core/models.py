import uuid
from django.utils import timezone
from django.db import models


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
    created_at = models.DateTimeField(verbose_name='Created at')
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name='Updated at')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Deleted at')
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='Created by')
    updated_by = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Updated by')
    deleted_by = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Deleted by')

    objects = BankManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class BaseBankModel(BaseAuditModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
