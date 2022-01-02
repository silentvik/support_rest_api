from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ChoiceField, SerializerMethodField


class SerializerMethodKwargsField(SerializerMethodField):
    """
        SerializerMethodField with kwargs possibility.
    """

    def __init__(self, method_name=None, **kwargs):
        """
            Saves the passed arguments as self.kwargs
        """

        super().__init__(method_name)
        self.kwargs = kwargs

    def to_representation(self, value):
        """
            Selects a method by name.
            Uses arguments defined during initialization.
        """

        method = getattr(self.parent, self.method_name)
        return method(value, **self.kwargs)


class AppChoiceField(ChoiceField):
    """
        Custom ChoiceField.
        Added error message (with choices list output),
        more soft choice with friendly error message.
    """

    default_error_messages = {
        'invalid_choice': _(
            '"{input}" is not a valid choice.'
            ' Choices are: "{choices_list}"'
        )
    }

    def to_internal_value(self, data):
        """
            Selects a key from the available options.
            Can fail with friendly message.
        """

        if data == '' and self.allow_blank:
            return ''
        for key, val in self._choices.items():
            if val == data or key == data:
                return key

        self.fail('invalid_choice', input=data, choices_list=self.get_choices_list())

    def get_choices_list(self):
        """
            Returns a list of choices. It doesn't have to be an instance method.
        """

        return [val for _, val in self._choices.items()]
