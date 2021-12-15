from copy import deepcopy

from django.contrib.auth import get_user_model
from django.urls import get_resolver
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from app_support.models import Message, Ticket
from app_support.serializers import (  # UserTicketsSerializer,; UserMessageSerializer,
    BasicMessageSerializer, BasicTicketsSerializer, BasicUserListSerializer,
    DefaultUserProfileSerializer, ExpandedUserListSerializer,
    ExpandedUserProfileSerializer, FullTicketSerializer,
    FullUserProfileSerializer)
from app_support.services import views_info
from app_support.views_mixins import AdditionalViewMethodsMixin
from app_support.views_permissions import (  # IsIdOwnerOrSuperUser,
    IsIdOwnerOrSupportPlus, IsItemOwnerOrSupportPlus, MethodsPermissions)

# from django.shortcuts import redirect
# from django.urls import path
# from rest_framework import \
#     status  # status,; views,; viewsets,; mixins,; filters,
# from app_support.tasks import create_user
# from rest_framework.views import APIView
# from rest_framework.request import Request
# from rest_framework.exceptions import NotFound
# from django.contrib.auth.models import AnonymousUser
# from django.http import JsonResponse
# from django.http.response import HttpResponseRedirect  # Http404,; HttpResponse


User = get_user_model()


class UsersListView(generics.ListCreateAPIView, AdditionalViewMethodsMixin):
    queryset = User.objects.all()
    permission_classes = (
        AllowAny,
    )
    serializer_modes = {
        'concise': BasicUserListSerializer,
        'expanded': ExpandedUserListSerializer,
        'default': DefaultUserProfileSerializer,  # for create
        'full': FullUserProfileSerializer,  # for staff+ only
    }
    serializer_mode = 'concise'
    list_ordering = ['id', 'date_joined']  # not filled yet
    list_limit = 10**6

    def get_serializer_class(self):
        self.serializer_class = self.serializer_modes[self.serializer_mode]
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.order_by(*self.list_ordering)[:self.list_limit]

    def list(self, request, *args, **kwargs):
        if self.get_current_user_type() not in ['Superuser', 'Staff', 'Support']:
            return Response(views_info.USERS_VIEW_INFO)
        self.set_valid_kwargs()
        return super().list(request, *args, **kwargs)

    def set_valid_kwargs(self):
        """
            Restrict list-view for support. Run validate/set attributes functions
        """
        self.set_list_limit()
        self.set_list_ordering()
        if self.get_current_user_type() not in ['Superuser', 'Staff']:
            serializer_modes_copy = deepcopy(self.serializer_modes)
            [serializer_modes_copy.pop(key) for key in ['default', 'full']]
            self.serializer_modes = serializer_modes_copy
        self.set_serializer_mode()

    def create(self, request, *args, **kwargs):
        self.serializer_mode = 'default'
        return super().create(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateDestroyAPIView, AdditionalViewMethodsMixin):
    queryset = User.objects.all()
    serializer_class = DefaultUserProfileSerializer
    permission_classes = (
        IsAuthenticated,
        # IsIdOwnerOrSuperUser,
        IsIdOwnerOrSupportPlus,
    )

    # defaults:
    # among these viewing modes, only the administrator can choose
    serializer_modes = {
        'concise': DefaultUserProfileSerializer,  # for user
        'expanded': ExpandedUserProfileSerializer,  # for support
        'full': FullUserProfileSerializer,  # for staff+
    }
    serializer_mode = 'concise'

    def set_mode(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            self.set_serializer_mode()
        elif user.is_support:
            self.serializer_mode = 'expanded'

    def get_object(self):
        self.set_mode()
        self.set_as_pk_in_kwargs(self.request.user.id)
        return super().get_object()

    def get_serializer(self, *args, **kwargs):
        """
            Get serializer depending on credentials and chosen mode.
        """
        serializer_class = self.serializer_modes[self.serializer_mode]
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class TicketsListView(generics.ListCreateAPIView, AdditionalViewMethodsMixin):

    # serializer_class = TicketDetailUserSerializer
    serializer_class = FullTicketSerializer
    permission_classes = (
        IsAuthenticated,
        IsIdOwnerOrSupportPlus,
    )
    queryset = Ticket.objects.all()

    # defaults:
    list_ordering = ['id', 'answered', 'ticket_theme']
    list_limit = 10**6
    serializer_modes = {
        'concise': BasicTicketsSerializer,
        'full': FullTicketSerializer,
    }
    serializer_mode = 'concise'
    asked_user_id = None

    def set_valid_kwargs(self):
        # AdditionalViewMethodsMixin helps here
        self.set_asked_user_id()
        self.set_list_limit()
        self.set_list_ordering()
        self.set_serializer_mode()

    def filter_queryset(self, queryset):
        self.set_valid_kwargs()
        queryset = super().filter_queryset(queryset)
        if self.asked_user_id:
            queryset = queryset.filter(
                opened_by=User.objects.get(
                    id=self.asked_user_id)
            )
        queryset = queryset.order_by(*self.list_ordering)[:self.list_limit]
        return queryset

    def get_serializer_class(self):
        print('***TicketsListView.get_serializer_class')
        self.serializer_class = self.serializer_modes[self.serializer_mode]
        return super().get_serializer_class()

    # def setup(self, request, *args, **kwargs):
        # perhaps this is the best place to process kwargs?


class TicketView(generics.RetrieveUpdateDestroyAPIView, AdditionalViewMethodsMixin):
    serializer_class = FullTicketSerializer
    queryset = Ticket.objects.all()
    restricted_class = Ticket
    permission_classes = (
        IsAuthenticated,
        MethodsPermissions,
        IsItemOwnerOrSupportPlus,
    )
    lookup_url_kwarg = 'ticket_id'


class MessagesView(generics.ListCreateAPIView, AdditionalViewMethodsMixin):
    serializer_class = BasicMessageSerializer
    restricted_class = Ticket
    permission_classes = (
        IsAuthenticated,
        MethodsPermissions,
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


class MessageView(generics.RetrieveUpdateDestroyAPIView, AdditionalViewMethodsMixin):
    serializer_class = BasicMessageSerializer
    permission_classes = (
        IsAdminUser,
        IsAuthenticated,
    )
    lookup_url_kwarg = 'message_id'
    queryset = Message.objects.all()


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
def error404_view(request, some_path=''):
    requested_path = request.path
    data = f'path {requested_path} does not exists.'
    if some_path[-1] != '/':
        # unfinished (the input parameters have not been processed yet)
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
    print('***BasicPageInfoView')
    resp = {
        'This is a root page. Your next steps': {
            'token/': 'token operations if have an account',
            'users/': 'view users (if have credentials for) or create new',
            'tickets/': 'to view tickets (if have credentials for) or create new',
        }
    }
    return Response(resp, status=200)
