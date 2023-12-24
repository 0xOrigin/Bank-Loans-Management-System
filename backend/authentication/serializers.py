from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login, Group
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.serializers import BaseBankSerializer
from authentication.models import UserRole, BankPersonnel, LoanProvider, LoanCustomer

User = get_user_model()

role_serializers_dict = lambda : {
    UserRole.BANK_PERSONNEL.value: BankPersonnelSerializer,
    UserRole.LOAN_PROVIDER.value: LoanProviderSerializer,
    UserRole.LOAN_CUSTOMER.value: LoanCustomerSerializer,
}


class UserSerializer(BaseBankSerializer):
    name = serializers.SerializerMethodField(source='get_name')

    class Meta:
        model = User
        exclude = BaseBankSerializer.Meta.exclude + ('groups', 'user_permissions',)
        extra_kwargs = {
            'last_login': {'read_only': True},
            'password': {'write_only': True},
            'role': {'default': UserRole.ADMIN.value},
        }
    
    def validate_password(self, value):
        try:
            validate_password(value)
        except Exception as exception:
            raise serializers.ValidationError(exception.messages)
        return value

    def create(self, validated_data):
        validated_data['email'] = BaseUserManager.normalize_email(validated_data['email'])
        validated_data['password'] = make_password(validated_data['password'])

        with transaction.atomic():
            instance = super().create(validated_data)
            instance.groups.add(Group.objects.get(name=instance.role))
        
        return instance

    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class BankTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'
    default_error_messages = {
        'no_active_account': _('Invalid username or password')
    }

    def validate(self, attrs):
        data = super().validate(attrs)

        data['access_token'] = data.pop('access')
        ROLE_SERIALIZERS = role_serializers_dict()
        if self.user.role in ROLE_SERIALIZERS:
            data[self.user.role] = ROLE_SERIALIZERS[self.user.role](self.user.role_object).data
        else:
            data['user'] = UserSerializer(self.user).data

        return data


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(required=False)

    def extract_refresh_token(self):
        request = self.context['request']
        if 'refresh' in request.data and request.data['refresh'] != '':
            return request.data['refresh']
        
        cookie_name = settings.JWT_AUTH_REFRESH_COOKIE_NAME
        if cookie_name and cookie_name in request.COOKIES:
            return request.COOKIES.get(cookie_name)
        else:
            raise InvalidToken(_('No valid refresh token found'))

    def validate(self, attrs):
        attrs['refresh'] = self.extract_refresh_token()
        data = super().validate(attrs)
        data['access_token'] = data.pop('access')
        return data


class BaseUserRoleSerializer(BaseBankSerializer):
    user = UserSerializer(required=True, allow_null=False)

    class Meta:
        model = None
        exclude = BaseBankSerializer.Meta.exclude

    def set_user_role(self, data):
        data['role'] = UserRole.ADMIN.value

    def create_user(self, data, validated_data):
        self.set_user_role(data)
        user = UserSerializer(data=data, context=self.context)
        user.is_valid(raise_exception=True)
        user = user.save(created_by=validated_data['created_by'], created_at=validated_data['created_at'])
        return user
    
    def update_user(self, data, instance, validated_data):
        data.pop('role', None) # remove role from data to prevent changing user role
        user = UserSerializer(instance, data=data, context=self.context)
        user.is_valid(raise_exception=True)
        user = user.save(updated_by=validated_data['updated_by'], updated_at=validated_data['updated_at'])
        return user

    def create(self, validated_data):
        user = validated_data.pop('user') # remove user data from validated_data to avoid error of nested serializer create method
        
        with transaction.atomic():
            validated_data['user'] = self.create_user(user, validated_data)
            instance = super().create(validated_data)

        return instance
    
    def update(self, instance, validated_data):
        user = validated_data.pop('user')

        with transaction.atomic():
            validated_data['user'] = self.update_user(user, instance.user, validated_data)
            instance = super().update(instance, validated_data)
        
        return instance


class BankPersonnelSerializer(BaseUserRoleSerializer):

    class Meta:
        model = BankPersonnel
        exclude = BaseBankSerializer.Meta.exclude

    def set_user_role(self, data):
        data['role'] = UserRole.BANK_PERSONNEL.value


class LoanProviderSerializer(BaseUserRoleSerializer):

    class Meta:
        model = LoanProvider
        exclude = BaseBankSerializer.Meta.exclude

    def set_user_role(self, data):
        data['role'] = UserRole.LOAN_PROVIDER.value


class LoanCustomerSerializer(BaseUserRoleSerializer):

    class Meta:
        model = LoanCustomer
        exclude = BaseBankSerializer.Meta.exclude

    def set_user_role(self, data):
        data['role'] = UserRole.LOAN_CUSTOMER.value
