from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(source='get_name')

    class Meta:
        model = User
        exclude = ['groups', 'user_permissions',]
        extra_kwargs = {
            'last_login': {'read_only': True},
            'password': {'write_only': True},
        }
    
    def validate(self, attrs):
        data = super().validate(attrs)
        if 'password' in data:
            data['password'] = make_password(data['password'])
        return data

    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class BankTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'
    default_error_messages = {
        'no_active_account': _('Invalid email or password')
    }

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['access_token'] = str(refresh.access_token)
        data['user'] = UserSerializer(self.user).data

        if settings.SIMPLE_JWT.get('UPDATE_LAST_LOGIN', False):
            update_last_login(None, self.user)

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
        data['access_token'] = str(data['access'])
        del data['access']
        return data
