from django.urls import include
from django.urls import path
from loans.apps import LoansConfig

app_name = LoansConfig.name


urlpatterns = [
    path('api/', include('loans.api.urls'), name='loans-api'),
]
