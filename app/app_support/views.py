from django.contrib.auth import get_user_model
from django.urls import get_resolver
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from app_support.models import Message, Ticket
from app_support.serializers import (BasicMessageSerializer,
                                     BasicTicketSerializer,
                                     BasicUserListSerializer,
                                     DefaultTicketSerializer,
                                     DefaultUserProfileSerializer,
                                     ExpandedTicketSerializer,
                                     ExpandedUserListSerializer,
                                     ExpandedUserProfileSerializer,
                                     FullTicketSerializer,
                                     FullUserProfileSerializer)
from app_support.services import views_info
from app_support.services.generalized_funcs import popped_dict
from app_support.views_mixins import ViewArgsMixin, ViewModesMixin
from app_support.views_permissions import (IsIdOwnerOrSupportPlus,
                                           IsItemOwnerOrSupportPlus,
                                           MethodsPermissions)

User = get_user_model()


class UsersListView(generics.ListCreateAPIView, ViewArgsMixin, ViewModesMixin):
    queryset = User.objects.prefetch_related("tickets").all()
    permission_classes = (
        AllowAny,
    )
    serializer_modes = {
        'basic': BasicUserListSerializer,
        'expanded': ExpandedUserListSerializer,
        'default': DefaultUserProfileSerializer,  # for create
        'full': FullUserProfileSerializer,  # for staff+ only
    }
    serializer_mode = 'default'
    list_ordering = ('unanswered_since', 'id', 'date_joined')  # not filled yet
    list_limit = 10**6

    def filter_queryset(self, queryset):
        print('***UsersListView.filter_queryset')
        queryset = super().filter_queryset(queryset)
        return queryset.order_by(*list(self.list_ordering))[:self.list_limit]

    def list(self, request, *args, **kwargs):
        if self.get_current_user_type() not in ['Superuser', 'Staff', 'Support']:
            return Response(views_info.USERS_PAGE_INFO)
        self.set_valid_kwargs()
        return super().list(request, *args, **kwargs)

    def set_valid_kwargs(self):
        """
            Prepare (validation and set) self.kwarg for further processing
        """
        self.set_list_limit()
        self.set_list_ordering()

    def set_available_modes(self):
        usertype = self.get_current_user_type()
        if usertype in ['Support']:
            self.serializer_modes = popped_dict(self.serializer_modes, ['full'])
        elif usertype in ['User']:
            self.serializer_modes = popped_dict(self.serializer_modes, [''])

    def set_default_mode(self):
        if self.request.method == 'POST':
            self.serializer_mode = 'default'
        else:
            self.serializer_mode = 'basic'

    def get_serializer_class(self):
        self.set_serializer_class()
        return super().get_serializer_class()


class UserProfileView(generics.RetrieveUpdateDestroyAPIView, ViewArgsMixin, ViewModesMixin):
    queryset = User.objects.all()
    # serializer_class = DefaultUserProfileSerializer
    permission_classes = (
        IsAuthenticated,
        # IsIdOwnerOrSuperUser,
        IsIdOwnerOrSupportPlus,
    )

    # defaults:
    # among these viewing modes, only the administrator can choose
    serializer_modes = {
        'basic': BasicUserListSerializer,  # for support+
        'default': DefaultUserProfileSerializer,  # for user
        'expanded': ExpandedUserProfileSerializer,  # for support+
        'full': FullUserProfileSerializer,  # for staff+
    }
    serializer_mode = 'default'

    def get_object(self):
        self.set_as_pk_in_kwargs(self.request.user.id)
        return super().get_object()

    def set_available_modes(self):
        usertype = self.get_current_user_type()
        if usertype in ['Superuser', 'Staff', 'Support']:
            self.serializer_modes = popped_dict(self.serializer_modes, [''])
        else:
            self.serializer_modes = popped_dict(self.serializer_modes, ['full', 'expanded', 'basic'])

    def set_default_mode(self):
        usertype = self.get_current_user_type()
        if usertype in ['Superuser', 'Staff', 'Support']:
            self.serializer_mode = 'expanded'

    def get_serializer_class(self):
        self.set_serializer_class()
        return super().get_serializer_class()


class TicketsListView(generics.ListCreateAPIView, ViewArgsMixin, ViewModesMixin):

    permission_classes = (
        IsAuthenticated,
        IsIdOwnerOrSupportPlus,
    )
    queryset = Ticket.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['id', 'opened_by', 'is_closed', 'is_frozen', 'is_answered', 'answerer_id']
    # defaults:
    list_ordering = ('user_question_date', 'id', 'ticket_theme')
    list_limit = 10**6
    serializer_modes = {
        'basic': BasicTicketSerializer,  # view list
        'default': DefaultTicketSerializer,  # view list/create
        'expanded': ExpandedTicketSerializer,  # view list/create
        'full': FullTicketSerializer,  # view list/create
    }
    serializer_mode = 'basic'
    asked_user_id = None

    def set_available_modes(self):
        usertype = self.get_current_user_type()
        if usertype in ['Support', 'Staff', 'Superuser']:
            self.serializer_modes = popped_dict(self.serializer_modes, [''])
        else:
            self.serializer_modes = popped_dict(self.serializer_modes, ['full', 'expanded'])

    def set_default_mode(self):
        if self.request.method == 'POST':
            self.serializer_mode = 'default'
        else:
            self.serializer_mode = 'basic'

    def filter_queryset(self, queryset):
        print('***TicketsListView.filter_queryset')
        self.set_valid_kwargs()
        queryset = super().filter_queryset(queryset)
        print(f'    self.filter_backends = {self.filter_backends}')
        # for backend in list(self.filter_backends):
        #     print(f'    backend = {backend}')
        #     queryset2 = backend().filter_queryset(self.request, queryset, self)

        if self.asked_user_id:
            queryset = queryset.filter(
                opened_by=User.objects.get(
                    id=self.asked_user_id)
            )
        queryset = queryset.order_by(*list(self.list_ordering))[:self.list_limit]
        return queryset

    def get_serializer_class(self):
        self.set_serializer_class()
        return super().get_serializer_class()

    # def setup(self, request, *args, **kwargs):
        # perhaps this is the best place to process kwargs?


class TicketView(generics.RetrieveUpdateDestroyAPIView, ViewArgsMixin, ViewModesMixin):
    # serializer_class = DefaultTicketSerializer
    queryset = Ticket.objects.all()
    restricted_class = Ticket
    permission_classes = (
        IsAuthenticated,
        MethodsPermissions,
        IsItemOwnerOrSupportPlus,
    )
    lookup_url_kwarg = 'ticket_id'

    serializer_modes = {
        'basic': BasicTicketSerializer,
        'default': DefaultTicketSerializer,
        'expanded': ExpandedTicketSerializer,
        'full': FullTicketSerializer,
    }
    serializer_mode = 'default'

    def set_available_modes(self):
        usertype = self.get_current_user_type()
        if usertype in ['Superuser', 'Staff', 'Support']:
            self.serializer_modes = popped_dict(self.serializer_modes, [''])
        else:
            self.serializer_modes = popped_dict(self.serializer_modes, ['full', 'expanded'])

    def set_default_mode(self):
        usertype = self.get_current_user_type()
        if usertype in ['Superuser', 'Staff', 'Support']:
            self.serializer_mode = 'full'

    def get_serializer_class(self):
        self.set_serializer_class()
        return super().get_serializer_class()


class MessagesView(generics.ListCreateAPIView):
    serializer_class = BasicMessageSerializer
    restricted_class = Ticket
    permission_classes = (
        IsAuthenticated,
        # MethodsPermissions,
        IsItemOwnerOrSupportPlus,
    )

    def get_queryset(self):
        asked_ticket_id = int(self.kwargs.get('ticket_id'))
        queryset = Message.objects.filter(linked_ticket__id=asked_ticket_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['ticket_id'] = self.kwargs['ticket_id']
        return context


class MessageView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BasicMessageSerializer
    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )
    lookup_url_kwarg = 'message_id'
    queryset = Message.objects.all()


@api_view(['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def error404_view(request, some_path=''):
    # unfinished (the input parameters have not been processed yet)
    requested_path = request.path
    data = f'path {requested_path} does not exists.'
    if some_path[-1] != '/':
        requested_path = f'{requested_path[1:]}/'
        urls_list = [value[0][0][0].split('%')[0] for value in get_resolver().reverse_dict.values()]
        if requested_path in urls_list:
            data += ' Could you have forgotten to add a slash?'
    resp = Response(
        data=str(data),
        status=404
    )
    return resp


@api_view(['GET'])
def BasicPageInfoView(request, **kwargs):
    resp = views_info.ROOT_PAGE_INFO
    return Response(resp, status=200)
