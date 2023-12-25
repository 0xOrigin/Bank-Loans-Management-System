from django.urls import include
from django.urls import path
from banks.apps import BanksConfig

app_name = BanksConfig.name


urlpatterns = [
    path('api/', include('banks.api.urls'), name='banks-api'),
]
