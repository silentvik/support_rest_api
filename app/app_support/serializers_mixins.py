# from rest_framework import status
# from rest_framework.mixins import CreateModelMixin
# from rest_framework.response import Response
from django.utils import timezone

from app_support.models import Ticket
from app_support.services.generalized_funcs import (accurate_string_datetime,
                                                    accurate_string_seconds)


class SerializerAdditionalMethodsMixin:

    def get_readable_date(self, object, field_name=None, **kwargs):
        if field_name:
            date = getattr(object, field_name)
            return accurate_string_datetime(date)
        return accurate_string_datetime(object.creation_date)

    def opened_by_who(self, object):
        return f'{object.opened_by}'

    def get_user_no_response_time(self, object, field_name=None):
        delta = timezone.now()-getattr(object, field_name)
        return accurate_string_seconds(int(delta.total_seconds()))

    def get_no_response_time(self, object, field_name=None):
        delta = timezone.now()-getattr(object, field_name)
        return accurate_string_seconds(int(delta.total_seconds()))

    def get_actual_tickets_count(self, object):
        res = Ticket.objects.filter(opened_by=object, answered=False, is_closed=False).count()
        return res

    def get_count_of_related_objects(self, object, related_class=None):
        """
            Returns a number of related instances
            If class was not given, we have count=0
        """

        if related_class:
            return related_class.objects.filter(linked_ticket=object).count()
        return 0

    def hide_private_fields(self, representation, list_of_fields):
        for field in list_of_fields:
            representation.popitem(field)
