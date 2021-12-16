from copy import deepcopy

from rest_framework import exceptions


class AdditionalViewMethodsMixin:
    default_queryset_filter_limit = 100*3

    def set_as_pk_in_kwargs(self, obj_to_set):
        if not self.kwargs.get('pk', None):
            self.kwargs['pk'] = obj_to_set

    def limit_arg_validator(self, limit_arg):
        try:
            return int(limit_arg)
        except ValueError:
            raise exceptions.ValidationError('invalid <limit> kwarg')

    def set_list_limit(self):
        limit_kwarg = self.request.GET.get('limit', self.default_queryset_filter_limit)
        self.list_limit = self.limit_arg_validator(limit_kwarg)

    def set_asked_user_id(self):
        asked_user_id = self.request.GET.get('user_id', None)
        if asked_user_id is None:
            asked_user_id = self.request.parser_context["kwargs"].get('pk', None)
        if asked_user_id is not None:
            asked_user_id = int(asked_user_id)
            if asked_user_id == 0:
                asked_user_id = self.request.user.id
        self.asked_user_id = asked_user_id

    def set_list_ordering(self):
        order_kwarg = self.request.GET.get('order', None)
        # print(f'TYPE ORDER = {type(order_kwarg)}')
        # not really nessesary but I used deepcopy
        if order_kwarg:
            self.list_ordering = self.choice_arg_validator(order_kwarg, deepcopy(self.list_ordering))

    def choice_arg_validator(self, kwarg, valid_choices):
        if kwarg in valid_choices:
            idx = valid_choices.index(kwarg)
            valid_choices[0], valid_choices[idx] = valid_choices[idx], valid_choices[0]
            return valid_choices
        raise exceptions.ValidationError(
            f'kwarg <{kwarg}> not in available choices: {valid_choices}'
        )

    def set_serializer_mode(self):
        # set mode works only w GET request yet
        mode = self.request.GET.get('mode', None)
        if mode:
            if mode in self.serializer_modes.keys():
                self.serializer_mode = mode
            else:
                raise exceptions.ValidationError(
                    f'kwarg <{mode}> not in available choices: {list(self.serializer_modes.keys())}'
                )

    def get_current_user_type(self):
        user = self.request.user
        if user.id is None:
            return 'Anonimous'
        if user.is_superuser:
            return 'Superuser'
        if user.is_staff:
            return 'Staff'
        if user.is_support:
            return 'Support'
        return 'User'

    def chose_and_set_mode(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            self.set_serializer_mode()
        elif user.is_support:
            self.serializer_mode = 'expanded'
