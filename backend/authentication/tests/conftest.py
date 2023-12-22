import pytest
from enum import Enum
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from model_bakery import baker
from authentication.apps import AuthenticationConfig
from core.models import Company
from van_sales.models import SalesTeam, SalesTeamMember


User = get_user_model()


class ReverseViewName(str, Enum):
    AUTHENTICATION = AuthenticationConfig.name

    LOGIN = f'{AUTHENTICATION}:token_obtain_pair'
    PASSWORD_RESET = f'{AUTHENTICATION}:password_reset'

    USER_LIST = f'{AUTHENTICATION}:user-list'
    USER_DETAIL = f'{AUTHENTICATION}:user-detail'



''' 
# ---------------------------------------------------------------------------------------------
    |   # Creators 
# ---------------------------------------------------------------------------------------------
'''


@pytest.fixture(scope='class')
def api_client():
    return APIClient()


@pytest.fixture(scope='class')
def api_client_with_credentials():
    def make_api_client_with_credentials(user):
        api_client_with_credentials = APIClient()
        api_client_with_credentials.force_authenticate(user=user)
        return api_client_with_credentials
    return make_api_client_with_credentials


@pytest.fixture(scope='class')
def create_company():
    def make_company(**kwargs):
        company = baker.make(Company, **kwargs)
        company.save()
        return company
    return make_company


@pytest.fixture(scope='class')
def create_permission_group():
    def make_permission_group(name):
        permission_group, created = Group.objects.get_or_create(name=name)
        if created:
            permissions = Permission.objects.filter(content_type__app_label=AuthenticationConfig.name)
            permission_group.permissions.set(permissions)
        return permission_group
    return make_permission_group


@pytest.fixture(scope='class')
def create_user():
    def make_user(**kwargs):
        user = baker.make(User, **kwargs)
        user.set_password('password')
        user.save()
        return user
    return make_user


@pytest.fixture(scope='class')
def create_team():
    def make_team(**kwargs):
        team = baker.make(SalesTeam, **kwargs)
        team.save()
        return team
    return make_team


@pytest.fixture(scope='class')
def create_member():
    def make_member(**kwargs):
        member = baker.make(SalesTeamMember, **kwargs)
        member.save()
        return member
    return make_member



''' 
# ---------------------------------------------------------------------------------------------
    |   # Authenticator 
# ---------------------------------------------------------------------------------------------
'''


@pytest.fixture(scope='class')
def authenticate(api_client):
    def do_authenticate(make_user=None):
        url = reverse(ReverseViewName.LOGIN)

        data = {
            'email': make_user.email if make_user else '',
            'password': 'password'
        }
        return api_client.post(url, data)
    return do_authenticate



''' 
# ---------------------------------------------------------------------------------------------
    |   # Factories 
# ---------------------------------------------------------------------------------------------
'''


@pytest.fixture(scope='class')
def user_factory(create_company, create_permission_group, create_user):
    def make_user_factory(permission_group_name=None):
        company = create_company()
        if permission_group_name:
            permission_group = create_permission_group(permission_group_name)
            user = create_user(company=company, groups=[permission_group,])
        else:
            user = create_user(company=company)
        return company, user
    return make_user_factory


@pytest.fixture(scope='class')
def team_factory(user_factory, create_team):
    def make_team_factory(permission_group_name=None):
        company, user = user_factory(permission_group_name)
        team = create_team(company=company, leader=user)
        return company, user, team
    return make_team_factory


@pytest.fixture(scope='class')
def member_factory(team_factory, create_member):
    def make_member_factory(permission_group_name=None):
        company, user, team = team_factory(permission_group_name)
        member = create_member(company=company, user=user, team=team)
        return company, user, team, member
    return make_member_factory



''' 
# ---------------------------------------------------------------------------------------------
    |   # Injectors 
# ---------------------------------------------------------------------------------------------
'''


@pytest.fixture(scope='class')
def authentication_injector(request, authenticate):
    request.cls.authenticate = authenticate


@pytest.fixture(scope='class')
def api_client_factory_injector(request, api_client, api_client_with_credentials):
    request.cls.api_client = api_client
    request.cls.api_client_with_credentials = api_client_with_credentials


@pytest.fixture(scope='class')
def company_factory_injector(request, create_company):
    request.cls.create_company = create_company


@pytest.fixture(scope='class')
def user_factory_injector(request, company_factory_injector, create_permission_group, create_user, user_factory):
    request.cls.create_permission_group = create_permission_group
    request.cls.create_user = create_user
    request.cls.user_factory = user_factory


@pytest.fixture(scope='class')
def team_factory_injector(request, user_factory_injector, create_team, team_factory):
    request.cls.create_team = create_team
    request.cls.team_factory = team_factory


@pytest.fixture(scope='class')
def member_factory_injector(request, team_factory_injector, create_member, member_factory):
    request.cls.create_member = create_member
    request.cls.member_factory = member_factory
