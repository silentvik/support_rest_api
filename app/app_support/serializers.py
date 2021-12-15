from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from app_support import serializers_fields
from app_support.models import TICKET_THEMES, Message, Ticket  # AppUser,
from app_support.serializers_mixins import SerializerAdditionalMethodsMixin
from app_support.services.generalized_funcs import (accurate_string_seconds,
                                                    find_a_match, merged)

# from rest_framework.decorators import permission_classes
# from datetime import datetime, timedelta
# from django.utils import timezone
User = get_user_model()


# basic serializers:


class BasicTicketsSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    message = serializers.CharField(write_only=True)
    ticket_theme = serializers_fields.AppChoiceField(choices=TICKET_THEMES,)
    owner_id = serializers.CharField(source='opened_by.id', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_theme',
            'is_closed',
            'answered',
            'message',
            'owner_id',
        ]

    # def validate_ticket_theme(self, ticket_theme_data):
    #     valid_theme = try_found_in_collection(ticket_theme_data, TICKET_THEMES, '1')
    #     return valid_theme

    def create(self, validated_data):
        """
            Create new Ticket and related Message instance
        """
        print('***UserTicketsSerializer.create')
        print(f'    validated_data = {validated_data}')
        validated_data['ticket_theme'] = find_a_match(
            subject=validated_data,
            collection=TICKET_THEMES,
            default=TICKET_THEMES[-1][0],
        )
        user = self.context.get('request', None).user
        # if not user.is_support and not user.is_superuser:
        #     validated_data['ticket_theme'] = False
        print(f'    user = {user}')
        ticket = Ticket.objects.create(opened_by=user, **validated_data)
        Message.objects.create(linked_ticket=ticket, linked_user=user, body=validated_data['message'])
        return ticket


class BasicUserListSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    screen_name = serializers.CharField(source='get_screen_name', read_only=True)
    pretty_creation_date = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='date_joined',
        read_only=True,
    )

    actual_tickets_count = serializers.SerializerMethodField(
        method_name='get_actual_tickets_count',
        # read_only=True,
    )
    # tickets = fields.SerializerMethodKwargsField(
    #     method_name='get_readable_date',
    # )

    class Meta:
        model = User
        fields = [
            'screen_name',
            'pretty_creation_date',
            'actual_tickets_count',
            'max_unanswered_time'
        ]

    # def get_related_fields(self, inst, **kwargs):
    #     res = Ticket.objects.filter(opened_by=inst, )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['max_unanswered_time'] = accurate_string_seconds(representation['max_unanswered_time'])
        return representation


class BasicMessageSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    written_by = serializers.CharField(source='linked_user.get_screen_name', read_only=True)
    creation_date = serializers.SerializerMethodField('get_readable_date')
    message = serializers.CharField(source='body', required=True)

    class Meta:
        model = Message
        fields = [
            # 'id',
            'written_by',
            'creation_date',
            'message'
        ]

    # def update(self, instance, validated_data):
    #     print('***MessageSerializer.update')
    #     return instance

    def create(self, validated_data):
        print('***MessageSerializer.create')
        print(f'    self.context = {self.context}')
        user_obj = self.context.get('request', None).user
        ticket_number = self.context.get('ticket_id', None)
        ticket_obj = Ticket.objects.get(id=ticket_number)
        print(f'    ticket_obj = {ticket_obj}')
        print(f'    user_obj = {user_obj}')
        validated_data['linked_ticket'] = ticket_obj
        validated_data['linked_user'] = user_obj
        return super().create(validated_data)


class BasicUserProfileSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    # email = serializers.EmailField(max_length=250, write_only=True)
    password = serializers.CharField(min_length=8, max_length=250, write_only=True)
    # username = serializers.CharField(max_length=250, write_only=True)
    creation_date = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='date_joined',
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'screen_name',
            'hide_private_info',
            'creation_date',
        ]

    def validate_password(self, password_data):
        """
            password_str: password of a user [str]
            return: a hashed version of the password
        """
        username_data = self.initial_data.get('username', '')
        email_data = self.initial_data.get('email', '')
        if '' not in [password_data, username_data, email_data]:
            if password_data in username_data or username_data in password_data:
                raise serializers.ValidationError('Password is very close to username')
            if password_data in email_data or email_data in password_data:
                raise serializers.ValidationError('Password is very close to email')
        return make_password(password_data)


# expanded serializers:


class ExpandedUserListSerializer(BasicUserListSerializer):
    tickets = BasicTicketsSerializer(many=True, read_only=True)

    class Meta(BasicUserListSerializer.Meta):
        fields = merged(BasicUserListSerializer.Meta.fields, [
            'first_name',
            'last_name',
            'tickets',
        ])

    def get_related_fields(self, inst, **kwargs):
        queryset = Ticket.objects.filter(opened_by=inst)
        return BasicTicketsSerializer(queryset, many=True)


class DefaultUserProfileSerializer(BasicUserProfileSerializer):
    updated_at = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='last_update',
        read_only=True,
    )
    actual_tickets_count = serializers.SerializerMethodField(
        method_name='get_actual_tickets_count',
        # read_only=True,
    )

    class Meta(BasicUserProfileSerializer.Meta):
        fields = merged(BasicUserProfileSerializer.Meta.fields, [
            'username',
            'email',
            'first_name',
            'last_name',
            'personal_information',
            'updated_at',
            'actual_tickets_count',
        ])


class ExpandedUserProfileSerializer(DefaultUserProfileSerializer):
    no_response_time = serializers_fields.SerializerMethodKwargsField(
        method_name='get_no_response_time',
        field_name='last_update',
    )

    class Meta(DefaultUserProfileSerializer.Meta):
        model = User
        fields = merged(DefaultUserProfileSerializer.Meta.fields, [
            'is_support',
            'is_staff',
            'no_response_time'
        ])


class FullUserProfileSerializer(ExpandedUserProfileSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FullTicketSerializer(BasicTicketsSerializer):
    no_response_time = serializers_fields.SerializerMethodKwargsField(
        method_name='get_no_response_time',
        field_name='last_update',
    )
    messages = BasicMessageSerializer(many=True, read_only=True)
    message = serializers.CharField(write_only=True)
    opened_by = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'


class UserTicketsSerializer(BasicTicketsSerializer):
    last_update = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='last_update',
        read_only=True,
    )
    no_response_time = serializers_fields.SerializerMethodKwargsField(
        method_name='get_no_response_time',
        field_name='last_update',
    )

    class Meta(BasicTicketsSerializer.Meta):
        fields = merged(BasicTicketsSerializer.Meta.fields, [
            'no_response_time',
            'last_update'
        ])
