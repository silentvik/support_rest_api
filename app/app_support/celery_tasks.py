"""
    Regular CELERY tasks here
"""

from celery import shared_task
from django.contrib.auth import get_user_model

from app_support.models import Message, Ticket

User = get_user_model()

AVAILABLE_CLASSES = {
    'User': User,
    'Ticket': Ticket,
    'Message': Message,
}


@shared_task
def delete_object(class_name=None, id_to_delete=None):
    """
        delete obj from db by id
    """
    if class_name and id_to_delete:
        AVAILABLE_CLASSES[class_name].objects.filter(id=id_to_delete)[0].delete()
