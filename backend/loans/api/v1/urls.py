from django.urls import include
from django.urls import path
from django.conf import settings
from rest_framework_nested import routers
from loans.views import LoanPlanViewSet, LoanViewSet, LoanApplicationViewSet, LoanPaymentViewSet

router = routers.DefaultRouter(trailing_slash=settings.APPEND_SLASH)
router.register(r'loan-plans', LoanPlanViewSet)
router.register(r'loans/applications', LoanApplicationViewSet, basename='loan-applications')
router.register(r'loans', LoanViewSet)

loan_router = routers.NestedSimpleRouter(router, r'loans', lookup='loan')
loan_router.register(r'payments', LoanPaymentViewSet, basename='loan-payments')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(loan_router.urls)),
]
