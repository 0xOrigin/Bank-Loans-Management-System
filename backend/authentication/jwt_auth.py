from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import status
from rest_framework import exceptions, serializers
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings


access_cookie_name = settings.JWT_AUTH_ACCESS_COOKIE_NAME
access_cookie_path = settings.JWT_AUTH_ACCESS_COOKIE_PATH
refresh_cookie_name = settings.JWT_AUTH_REFRESH_COOKIE_NAME
refresh_cookie_path = settings.JWT_AUTH_REFRESH_COOKIE_PATH
cookie_httponly = settings.JWT_AUTH_COOKIE_HTTPONLY
cookie_secure = settings.JWT_AUTH_COOKIE_SECURE
cookie_samesite = settings.JWT_AUTH_COOKIE_SAMESITE


def set_jwt_access_cookie(response, access_token):
    access_token_expiration = (timezone.now() + api_settings.ACCESS_TOKEN_LIFETIME)

    if access_cookie_name:
        response.set_cookie(
            access_cookie_name,
            access_token,
            path=access_cookie_path,
            expires=access_token_expiration,
            secure=cookie_secure,
            httponly=cookie_httponly,
            samesite=cookie_samesite,
        )


def set_jwt_refresh_cookie(response, refresh_token):
    refresh_token_expiration = (timezone.now() + api_settings.REFRESH_TOKEN_LIFETIME)

    if refresh_cookie_name:
        response.set_cookie(
            refresh_cookie_name,
            refresh_token,
            expires=refresh_token_expiration,
            path=refresh_cookie_path,
            httponly=cookie_httponly,
            secure=cookie_secure,
            samesite=cookie_samesite,
        )


def set_jwt_cookies(response, access_token, refresh_token):
    set_jwt_access_cookie(response, access_token)
    set_jwt_refresh_cookie(response, refresh_token)


def unset_jwt_cookies(response):
    if access_cookie_name:
        response.delete_cookie(access_cookie_name, path=access_cookie_path, samesite=cookie_samesite)
    if refresh_cookie_name:
        response.delete_cookie(refresh_cookie_name, path=refresh_cookie_path, samesite=cookie_samesite)


class JWTCookieAuthentication(JWTAuthentication):

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            if access_cookie_name:
                raw_token = request.COOKIES.get(access_cookie_name, None)
            else:
                return None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
