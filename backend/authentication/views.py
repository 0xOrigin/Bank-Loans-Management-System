from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from core.renderers import BankJSONRenderer
from core.views import BaseBankViewSet, NonCreatableViewSet, NonUpdatableViewSet, NonDeletableViewSet
from authentication.jwt_auth import set_jwt_cookies, unset_jwt_cookies
from authentication.serializers import UserSerializer, BankPersonnelSerializer, LoanProviderSerializer, LoanCustomerSerializer
from authentication.permissions import AuthenticationPermissions
from authentication.filters import UserFilter
from authentication.models import User, BankPersonnel, LoanProvider, LoanCustomer


class UserViewSet(BaseBankViewSet):
    model = User
    queryset = model.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AuthenticationPermissions]
    filterset_class = UserFilter

    def get_queryset(self):
        return (
            super().get_queryset().prefetch_related('groups', 'user_permissions')
        )


class LoginView(TokenObtainPairView):
    renderer_classes = [BankJSONRenderer, BrowsableAPIRenderer]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        set_jwt_cookies(response, response.data['access_token'], response.data.pop('refresh'))
        return response


class LogoutView(generics.GenericAPIView):
    renderer_classes = [BankJSONRenderer, BrowsableAPIRenderer]

    def get(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        unset_jwt_cookies(response)
        return response


class BaseAccountRegistrationViewSet(NonCreatableViewSet, BaseBankViewSet):
    model = None
    serializer_class = None

    def perform_create(self, serializer):
        serializer.save(created_by=None, created_at=timezone.now())
    
    @action(detail=False, methods=['post',], url_path='register', url_name='register', permission_classes=[])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BankPersonnelViewSet(BaseAccountRegistrationViewSet):
    model = BankPersonnel
    queryset = model.objects.all()
    serializer_class = BankPersonnelSerializer

    def get_queryset(self):
        return (
            super().get_queryset().select_related('user', 'branch')
        )


class LoanProviderViewSet(BaseAccountRegistrationViewSet):
    model = LoanProvider
    queryset = model.objects.all()
    serializer_class = LoanProviderSerializer

    def get_queryset(self):
        return (
            super().get_queryset().select_related('user')
        )


class LoanCustomerViewSet(BaseAccountRegistrationViewSet):
    model = LoanCustomer
    queryset = model.objects.all()
    serializer_class = LoanCustomerSerializer

    def get_queryset(self):
        return (
            super().get_queryset().select_related('user')
        )
