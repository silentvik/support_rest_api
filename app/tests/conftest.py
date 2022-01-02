import pytest
from _pytest.runner import runtestprotocol
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def pytest_runtest_protocol(item, nextitem):
    """
        Makes reports more readable.
    """

    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        if report.when == 'call':
            print('\n%s --- %s' % (item.name, report.outcome))
    return True


@pytest.fixture(scope='session')
def django_db_setup():
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_db',
        'USER': 'django_user',
        'PASSWORD': 'django_password',
        'HOST': 'db',
        'PORT': '5432'
    }


@pytest.fixture
def create_user():
    """
        Creates User instance with given kwargs.
    """

    def make_user(**kwargs):
        username = kwargs.get('username', None)
        if not username:
            kwargs['username'] = 'test1000'
        kwargs['password'] = 'testtest'
        kwargs['email'] = f"{kwargs['username']}@aa.aa"
        return User.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def api_client():
    return APIClient()
