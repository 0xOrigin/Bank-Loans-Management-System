from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from authentication.models import UserRole

User = get_user_model()


def create_superuser():
    if User.objects.filter(username='admin').exists():
        return
    
    user = User.objects.create_superuser(
        'egyahmed.ezzat120@gmail.com',
        'admin',
        'admin',
    )
    admin_group = Group.objects.get_or_create(name=UserRole.ADMIN.value)
    user.groups.add(admin_group)
    print('[+] Superuser created successfully.')


def create_permission_groups():
    for role in UserRole:
        Group.objects.get_or_create(name=role.value)
