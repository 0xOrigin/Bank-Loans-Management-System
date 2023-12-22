from django.urls import include
from django.urls import path


urlpatterns = [
    path('v1/', include('authentication.api.v1.urls'), name='authentication-api-v1'),
]
