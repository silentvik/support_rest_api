# CELERY tasks
from celery import shared_task
from django.contrib.auth import get_user_model

# from app_support.models import Message, Ticket

User = get_user_model()


@shared_task
def create_user_test(username, password, email):
    """
        for tests only
    """
    user = User.objects.create(
        username=username,
        password=password,
        email=email,
    )
    user.save()
    # print('##################   [CELERY] OBJECT CREATED     #######################!!!')


@shared_task
def delete_user_test(username):
    """
        for tests only
    """
    user = User.objects.get(
        username=username,
    )
    user.delete()
    # print('##################   [CELERY] OBJECT DELETED      #######################!!!')
