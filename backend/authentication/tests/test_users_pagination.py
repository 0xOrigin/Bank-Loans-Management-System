import pytest
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from model_bakery import baker
from faker import Faker
from django.conf import settings
from authentication.models import UserRole
from authentication.tests.conftest import ReverseViewName


@pytest.mark.django_db
@pytest.mark.usefixtures('api_client_factory_injector', 'user_factory_injector')
class TestPagiantion(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.company, self.user = TestPagiantion.user_factory(UserRole.SUPERVISOR)
        self.user.is_superuser = True
        self.user.save()
        self.api_client = TestPagiantion.api_client
        self.authenticated_api_client = TestPagiantion.api_client_with_credentials(self.user)

    def test_user_list_pagination(self):
        for i in range(settings.PAGINATION_PAGE_SIZE): # create PAGINATION_PAGE_SIZE users after the first user.
            baker.make(settings.AUTH_USER_MODEL, company=self.company).save()
        data = {'page': 2} # get the second page.

        response = self.authenticated_api_client.get(reverse(ReverseViewName.USER_LIST), data=data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1) # 1 user in the second page.
