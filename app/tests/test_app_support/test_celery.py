
from time import sleep

import pytest
from app_support.celery_test_tasks import create_user_test, delete_user_test
from django.contrib.auth import get_user_model

from .services import TestMixin

User = get_user_model()


@pytest.mark.django_db
class TestCelery(TestMixin):
    manipulated_items_count = 3
    wait_for_celery_sec = 0.5

    def test_celery_is_working(self):
        starting_users_count = User.objects.count()
        self.create_tmp_users(self.manipulated_items_count, celery_task=create_user_test)
        sleep(self.wait_for_celery_sec)
        assert User.objects.count() == starting_users_count + self.manipulated_items_count
        assert len(self.users) == self.manipulated_items_count
        self.delete_tmp_users(celery_task=delete_user_test)
        sleep(self.wait_for_celery_sec)
        assert User.objects.count() == starting_users_count
