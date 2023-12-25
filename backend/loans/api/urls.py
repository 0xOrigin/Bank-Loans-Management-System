from django.urls import include
from django.urls import path


urlpatterns = [
    path('v1/', include('loans.api.v1.urls'), name='loans-api-v1'),
]
