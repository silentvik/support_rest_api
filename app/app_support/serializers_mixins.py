from app_support.services.generalized_funcs import (accurate_string_datetime,
                                                    accurate_string_seconds)


class SerializerAdditionalMethodsMixin:
    """
        Contain a few general methods which can be used in any serializer
    """

    def get_readable_date(self, object, field_name):
        date = getattr(object, field_name)
        if date:
            return accurate_string_datetime(date)
        return None

    def readable_time_seconds(self, object, field_name):
        seconds = getattr(object, field_name)
        return accurate_string_seconds(seconds)

    def hide_private_fields(self, representation, list_of_fields):
        for field in list_of_fields:
            representation.popitem(field)
