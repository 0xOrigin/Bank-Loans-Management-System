import os
import uuid
from enum import Enum
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from core.models import BankManager, BaseBankModel


class UserManager(BaseUserManager, BankManager):

    def create_user(self, email, username, password=None, created_at=timezone.now()):
        if not email:
            raise ValueError(_('User must have an email address'))
        if not username:
            raise ValueError(_('User must have a username'))

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            created_at=created_at,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserRole(models.TextChoices):
    ADMIN = ('admin', _('Admin'))
    BANK_PERSONNEL = ('bank_personnel', _('Bank Personnel'))
    LOAN_PROVIDER = ('loan_provider', _('Loan Provider'))
    LOAN_CUSTOMER = ('loan_customer', _('Loan Customer'))


class User(AbstractBaseUser, BaseBankModel, PermissionsMixin):

    def get_user_picture_upload_path(instance, filename):
        path = 'profile-pictures/'
        (filename, ext) = os.path.splitext(filename)
        return f'{path}{uuid.uuid4()}{ext}'

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    picture = models.ImageField(upload_to=get_user_picture_upload_path, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(max_length=30, choices=UserRole.choices)

    @property
    def role_object(self):
        return getattr(self, self.role, None)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']
    objects = UserManager()

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self) -> str:
        return self.username


class ApplicantStatus(models.TextChoices):
    PENDING = ('pending', _('Pending'))
    APPROVED = ('approved', _('Approved'))
    REJECTED = ('rejected', _('Rejected'))


class BaseApplicant(BaseBankModel):
    status = models.CharField(max_length=20, choices=ApplicantStatus.choices, default=ApplicantStatus.PENDING.value)
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='%(class)s_applicants')

    class Meta:
        abstract = True


class LoanProvider(BaseApplicant):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name=UserRole.LOAN_PROVIDER.value)
    name_en = models.CharField(max_length=150)
    name_ar = models.CharField(max_length=150)
    total_funds = models.DecimalField(max_digits=14, decimal_places=2)
    registration_number = models.CharField(max_length=20)
    vat_number = models.CharField(max_length=20)

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self) -> str:
        return f'{self.user} ({self.total_funds})'


class LoanCustomer(BaseApplicant):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name=UserRole.LOAN_CUSTOMER.value)
    ssn = models.CharField(max_length=20, unique=True) # Social Security Number or National ID
    credit_score = models.PositiveIntegerField()
    monthly_income = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self) -> str:
        return f'{self.user} ({self.ssn})'


class BankPersonnel(BaseBankModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name=UserRole.BANK_PERSONNEL.value)
    branch = models.ForeignKey('banks.Branch', on_delete=models.CASCADE, related_name='personnels')

    @property
    def bank(self):
        return self.branch.bank

    class Meta:
        managed = True
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['user']),
            models.Index(fields=['branch']),
        ]
    
    def __str__(self) -> str:
        return f'{self.user} ({self.branch})'
