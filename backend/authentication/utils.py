from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
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
    admin_group = Group.objects.get(name=UserRole.ADMIN.value)
    user.groups.add(admin_group)
    print('[+] Superuser created successfully.')


def create_permission_groups():
    for role in UserRole:
        Group.objects.get_or_create(name=role.value)
    print('[+] Permission groups created/updated successfully.')


def add_permissions_to_admin_group():
    admin_group = Group.objects.get(name=UserRole.ADMIN.value)
    codenames = [
        'add_user', 'change_user', 'delete_user', 'view_user',
        'add_bankpersonnel', 'change_bankpersonnel', 'delete_bankpersonnel', 'view_bankpersonnel',
        'add_loanprovider', 'change_loanprovider', 'delete_loanprovider', 'view_loanprovider',
        'add_loancustomer', 'change_loancustomer', 'delete_loancustomer', 'view_loancustomer',
        'add_bank', 'change_bank', 'delete_bank', 'view_bank',
        'add_branch', 'change_branch', 'delete_branch', 'view_branch',
    ]
    permissions = Permission.objects.filter(codename__in=codenames)
    admin_group.permissions.add(*permissions)


def add_permissions_to_bank_personnel_group():
    bank_personnel_group = Group.objects.get(name=UserRole.BANK_PERSONNEL.value)
    codenames = [
        'change_user', 'view_user', 'view_bankpersonnel', 'view_bank',
        'view_branch', 'view_loanprovider', 'view_loancustomer',
        'view_loanplan', 'view_loan', 'view_loanpayment', 'can_view_amortization_schedule',
        'add_loanplan', 'can_approve_applicant', 'can_reject_applicant', 'can_approve_loan',
        'can_reject_loan', 'can_disburse_loan',
    ]
    permissions = Permission.objects.filter(codename__in=codenames)
    bank_personnel_group.permissions.add(*permissions)


def add_permissions_to_loan_provider_group():
    loan_provider_group = Group.objects.get(name=UserRole.LOAN_PROVIDER.value)
    codenames = [
        'change_user', 'view_user', 'view_loanprovider', 'view_bank', 'view_branch',
        'view_loancustomer', 'view_loanplan', 'view_loan', 'can_view_amortization_schedule',
        'add_loan', 'can_release_loan',
    ]
    permissions = Permission.objects.filter(codename__in=codenames)
    loan_provider_group.permissions.add(*permissions)


def add_permissions_to_loan_customer_group():
    loan_customer_group = Group.objects.get(name=UserRole.LOAN_CUSTOMER.value)
    codenames = [
        'change_user', 'view_user', 'view_bank', 'view_branch', 'view_loanprovider',
        'view_loancustomer', 'view_loanplan', 'view_loan', 'view_loanpayment',
        'add_loan', 'can_pay_loan',
    ]
    permissions = Permission.objects.filter(codename__in=codenames)
    loan_customer_group.permissions.add(*permissions)
