# Create your tasks here

# from support.models import Ticket, Message

from celery import shared_task
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def create_user(username, password, email):
    user = User.objects.create(
        username=username,
        password=password,
        email=email,
    )
    user.save()
    # print('##################   [CELERY] OBJECT CREATED     #######################!!!')


@shared_task
def delete_user(username):
    user = User.objects.get(
        username=username,
    )
    user.delete()
    # print('##################   [CELERY] OBJECT DELETED      #######################!!!')
