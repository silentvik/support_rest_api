from rest_framework import exceptions


class ViewModesMixin:
    def set_serializer_mode(self):
        # set mode works only w GET request yet
        mode = self.request.GET.get('mode', None)
        if mode:
            if mode in self.serializer_modes.keys():
                self.serializer_mode = mode
            else:
                # we need a serializer to render exception ^)
                self.serializer_class = self.serializer_modes[self.__class__.serializer_mode]
                raise exceptions.ValidationError(
                    f'Mode value <{mode}> is not in available choices for this type of user:'
                    f' {list(self.serializer_modes.keys())}'
                )

    def set_serializer_class(self):
        if not self.serializer_class:
            self.set_default_mode()
            self.set_available_modes()
            self.set_serializer_mode()
            self.serializer_class = self.serializer_modes[self.serializer_mode]

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


class ViewArgsMixin:
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
        if order_kwarg:
            self.list_ordering = self.choice_arg_validator(order_kwarg, self.list_ordering)
            # print(f'self.list_ordering = {self.list_ordering}')

    def choice_arg_validator(self, kwarg_value, valid_choices):
        positive_kwarg_value = kwarg_value
        if str(kwarg_value)[0] == '-':
            positive_kwarg_value = kwarg_value[1:]
        new_choices = list(valid_choices)
        if positive_kwarg_value in new_choices:
            idx = new_choices.index(positive_kwarg_value)
            new_choices[idx] = new_choices[0]
            new_choices[0] = kwarg_value
            return tuple(new_choices)
        raise exceptions.ValidationError(
            f'kwarg value <{kwarg_value}> is not in available choices: {valid_choices}'
        )

    def set_valid_kwargs(self):
        self.set_asked_user_id()
        self.set_list_limit()
        self.set_list_ordering()
