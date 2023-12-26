from django.dispatch import receiver
from django.db.models.signals import post_migrate, pre_save
from django.contrib.auth import get_user_model
from authentication.apps import AuthenticationConfig
from authentication.utils import (
    create_superuser, create_permission_groups, add_permissions_to_admin_group,
    add_permissions_to_bank_personnel_group, add_permissions_to_loan_provider_group,
    add_permissions_to_loan_customer_group,
)

User = get_user_model()


@receiver(post_migrate)
def perform_post_migrate_actions(sender, **kwargs):
    if sender.name == AuthenticationConfig.name:
        create_permission_groups() # First create permission groups
        create_superuser() # Then create superuser with admin group
        add_permissions_to_admin_group()
        add_permissions_to_bank_personnel_group()
        add_permissions_to_loan_provider_group()
        add_permissions_to_loan_customer_group()


@receiver(pre_save, sender=User)
def delete_old_user_picture_on_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            user = User.objects.get(pk=instance.pk)
        except User.DoesNotExist:
            return

        if user.picture != instance.picture:
            user.picture.delete(save=False)
