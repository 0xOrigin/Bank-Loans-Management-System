import pytest
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from model_bakery import baker
from faker import Faker
from authentication.models import UserRole
from authentication.tests.conftest import ReverseViewName


@pytest.mark.django_db
@pytest.mark.usefixtures('api_client_factory_injector', 'authentication_injector', 'member_factory_injector')
class TestAuthentication(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.api_client = TestAuthentication.api_client

    def test_leader_can_login(self):
        company, user, team = TestAuthentication.team_factory(UserRole.SUPERVISOR)

        response = TestAuthentication.authenticate(user)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_can_login(self):
        company, user, team, member = TestAuthentication.member_factory(UserRole.MEMBER)

        response = TestAuthentication.authenticate(user)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_leader_or_member_cannot_login(self):
        company, user = TestAuthentication.user_factory()

        response = TestAuthentication.authenticate(user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_cannot_login(self):
        response = TestAuthentication.authenticate()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
@pytest.mark.usefixtures('api_client_factory_injector', 'user_factory_injector')
class TestPasswordReset(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.api_client = TestPasswordReset.api_client

    def test_password_reset(self):
        company, user = TestPasswordReset.user_factory(UserRole.MEMBER)
        data = {'email': user.email}

        response = self.api_client.post(reverse(ReverseViewName.PASSWORD_RESET), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_with_invalid_email(self):
        data = {'email': 'invalid_email'}

        response = self.api_client.post(reverse(ReverseViewName.PASSWORD_RESET), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_with_non_existent_email(self):
        data = {'email': self.faker.email()}
        
        response = self.api_client.post(reverse(ReverseViewName.PASSWORD_RESET), data=data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
@pytest.mark.usefixtures('api_client_factory_injector', 'user_factory_injector')
class TestUserEndpoints(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.company, self.user = TestUserEndpoints.user_factory(UserRole.SUPERVISOR)
        self.user.is_superuser = True
        self.user.save()
        self.api_client = TestUserEndpoints.api_client
        self.authenticated_api_client = TestUserEndpoints.api_client_with_credentials(self.user)

    def test_list_users(self):
        response = self.authenticated_api_client.get(reverse(ReverseViewName.USER_LIST))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_user(self):
        response = self.authenticated_api_client.get(reverse(ReverseViewName.USER_DETAIL, kwargs={'pk': self.user.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        data = {
            'email': self.faker.email(),
            'name_en': self.faker.first_name(),
            'name_ar': self.faker.last_name(),
            'password': self.faker.password(),
            'username': self.faker.user_name(),
            'company': self.company.pk
        }
        response = self.authenticated_api_client.post(reverse(ReverseViewName.USER_LIST), data=data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], data['email'])

    def test_update_user(self):
        data = {
            'email': self.faker.email(),
            'name_en': self.faker.first_name(),
            'name_ar': self.faker.last_name(),
            'password': self.faker.password(),
            'company': self.company.pk,
            'username': self.faker.user_name()
        }
        response = self.authenticated_api_client.put(reverse(ReverseViewName.USER_DETAIL, kwargs={'pk': self.user.pk}), data=data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], data['email'])

    def test_partial_update_user(self):
        data = {
            'name_en': self.faker.first_name(),
            'name_ar': self.faker.last_name(),
        }
        response = self.authenticated_api_client.patch(reverse(ReverseViewName.USER_DETAIL, kwargs={'pk': self.user.pk}), data=data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name_en'], data['name_en'])

    def test_delete_user(self):
        response = self.authenticated_api_client.delete(reverse(ReverseViewName.USER_DETAIL, kwargs={'pk': self.user.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
