from django.urls import include
from django.urls import path
from authentication.apps import AuthenticationConfig

app_name = AuthenticationConfig.name


urlpatterns = [
    path('api/', include('authentication.api.urls'), name='authentication-api'),
]
