from django.urls import include
from django.urls import path
from django.conf import settings
from rest_framework_nested import routers
from banks.views import LoanProviderApplicationViewSet, LoanCustomerApplicationViewSet

router = routers.DefaultRouter(trailing_slash=settings.APPEND_SLASH)
router.register(r'providers/applications', LoanProviderApplicationViewSet)
router.register(r'customers/applications', LoanCustomerApplicationViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
