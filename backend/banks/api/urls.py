from django.urls import include
from django.urls import path


urlpatterns = [
    path('v1/', include('banks.api.v1.urls'), name='banks-api-v1'),
]
