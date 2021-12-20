import pytest
from django.contrib.auth import get_user_model
from SUPPORT_API.settings import DATABASES

# from django.test import TestCase
# from rest_framework import status
# from rest_framework.test import APITestCase
from .services import TestMixin

User = get_user_model()


@pytest.mark.django_db
class TestPrepareDB(TestMixin):
    manipulated_items = 3

    def test_db_engine(self):
        assert DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'

    def test_db_write_delete(self):
        starting_users_count = User.objects.count()
        self.create_tmp_users(self.manipulated_items)
        assert User.objects.count() == starting_users_count + self.manipulated_items
        assert len(self.users) == self.manipulated_items
        self.delete_tmp_users()
        assert User.objects.count() == starting_users_count
