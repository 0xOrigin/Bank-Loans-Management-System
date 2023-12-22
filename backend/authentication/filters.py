from django_filters.rest_framework import filters, FilterSet
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(FilterSet):
    name = filters.CharFilter(method='filter_name', label='Name')

    class Meta:
        model = User
        fields = {
            'first_name': ['icontains'],
            'last_name': ['icontains'],
            'email': ['icontains'],
            'is_active': ['exact'],
            'is_staff': ['exact'],
            'is_superuser': ['exact'],
            'role': ['exact'],
        }

    def filter_name(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )
