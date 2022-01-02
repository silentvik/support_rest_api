from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from app_support import serializers_fields
from app_support.models import Message, Ticket
from app_support.models_const import TICKET_THEMES
from app_support.serializers_mixins import SerializerAdditionalMethodsMixin
from app_support.services.generalized_funcs import find_a_match, merged

User = get_user_model()


class BasicMessageSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    written_by = serializers.CharField(source='linked_user.get_screen_name', read_only=True)
    creation_date = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='creation_date',
    )
    message = serializers.CharField(source='body', required=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'written_by',
            'creation_date',
            'message'
        ]

    def create(self, validated_data):
        """
            Сreates a new instance of the MESSAGE, adds the necessary field values.
        """

        user_obj = self.context.get('request', None).user
        ticket_number = self.context.get('ticket_id', None)
        ticket_obj = Ticket.objects.get(id=ticket_number)
        validated_data['linked_ticket'] = ticket_obj
        validated_data['linked_user'] = user_obj
        return super().create(validated_data)


class BasicTicketSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    """
        Contains the most necessary fields and methods for processing the Ticket instance.
    """

    message = serializers.CharField(write_only=True, default='')
    ticket_theme = serializers_fields.AppChoiceField(choices=TICKET_THEMES)
    is_closed = serializers.BooleanField(default=False)
    no_response_time = serializers_fields.SerializerMethodKwargsField(
        method_name='readable_time_seconds',
        field_name='not_answered_time',
    )

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_theme',
            'is_closed',
            'no_response_time',
            'message',
        ]

    def create(self, validated_data):
        """
            Creates a new Ticket and related Message instances
        """

        user = self.context.get('request', None).user
        validated_data['opened_by'] = user
        if validated_data.get('is_closed', None):
            validated_data['closed_by_id'] = user.id
        instance = super().create(validated_data)
        Message.objects.create(linked_ticket=instance, linked_user=user, body=validated_data['message'])
        return instance

    def update(self, instance, validated_data):
        """
            Custom updating with message field involved and closed_by_id field processing
        """

        self.process_closed_by_id_data(instance, validated_data)
        self.process_message_field(instance, validated_data)
        return super().update(instance, validated_data)

    def process_closed_by_id_data(self, instance, validated_data):
        """
            Adds a person who closed a ticket (if the ticket was closed)
        """

        user = self.context.get('request', None).user
        new_is_closed = validated_data.get('is_closed', None)
        old_is_closed = instance.is_closed
        if new_is_closed != old_is_closed:
            if new_is_closed is True:
                validated_data['closed_by_id'] = user.id
            else:
                validated_data['closed_by_id'] = None

    def process_message_field(self, instance, validated_data):
        """
            Creates a message, if one has been entered.
        """

        message_data = validated_data.get('message', '')
        if message_data != '':
            Message.objects.create(
                linked_ticket=instance,
                linked_user=self.context.get('request', None).user,
                body=validated_data['message']
            )

    def validate_ticket_theme(self, data):
        """
            The selection can be entered manually with errors,
            calls a function that makes a suitable choice depending on the request
        """

        new_data = find_a_match(
            subject=data,
            collection=TICKET_THEMES,
            default=TICKET_THEMES[-1][0],
        )
        return new_data

    def validate_message(self, message_data):
        """
            Message validator. Checks the message body only if there was an attempt to create a ticket
        """

        request_method = self.context.get('request', None).META['REQUEST_METHOD']

        # The message must be entered when creating a new ticket.
        if request_method == 'POST':
            if message_data == '':
                raise ValidationError('<message> field can not be blank when create new ticket.')
        return message_data


class DefaultTicketSerializer(BasicTicketSerializer):
    """
        Contains more fields than BasicTicketSerializer
    """

    opened_by_id = serializers.IntegerField(source='opened_by.id', read_only=True)
    screen_name = serializers.CharField(source='opened_by.get_screen_name', read_only=True)
    last_changes = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='last_changes',
    )
    creation_date = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='creation_date',
    )
    is_answered = serializers.BooleanField(read_only=True)

    class Meta(BasicTicketSerializer.Meta):
        fields = merged(BasicTicketSerializer.Meta.fields, [
            'opened_by_id',
            'screen_name',
            'creation_date',
            'last_changes',
            'messages_count',
            'is_answered',
        ])


class ExpandedTicketSerializer(DefaultTicketSerializer):
    """
        Contains more fields than DefaultTicketSerializer. Designed for use by support.
    """

    messages = BasicMessageSerializer(many=True, read_only=True)
    user_question_date = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='user_question_date',
    )

    class Meta(DefaultTicketSerializer.Meta):
        fields = merged(DefaultTicketSerializer.Meta.fields, [
            'user_question_date',
            'is_frozen',
            'answerer_id',
            'staff_note',
            'messages',
        ])


class FullTicketSerializer(ExpandedTicketSerializer):
    """
        Contains all Ticket fields (mandatory and optional).
    """

    class Meta:
        model = Ticket
        # repeated for ordering (messages at the end)
        fields = merged(ExpandedTicketSerializer.Meta.fields, [
            'closed_by_id',
            'messages'
            ]
        )


class BaseUserSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    """
        Basic user serializer with the most nessessary fields only.
    """

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=8, max_length=250, write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'email',
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
        # need I process unhashed _password in model here?
        return make_password(password_data)


class BasicUserListSerializer(BaseUserSerializer):
    """
        Serializes the User model. Designed to view the list of Users.
    """

    screen_name = serializers.CharField(source='get_screen_name', read_only=True)
    max_no_response_time = serializers_fields.SerializerMethodKwargsField(
        method_name='readable_time_seconds',
        field_name='max_not_answered_seconds',
    )
    opened_tickets_count = serializers.CharField(read_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = merged(
            BaseUserSerializer.Meta.fields, [
                'screen_name',
                'max_no_response_time',
                'opened_tickets_count',
            ]
        )


class ExpandedUserListSerializer(BasicUserListSerializer):
    """
        Serializes the User model.
        Designed to view the list of Users with their tickets (for the convenience of support workers).
    """

    tickets = BasicTicketSerializer(many=True, read_only=True)

    class Meta(BasicUserListSerializer.Meta):
        fields = merged(
            BasicUserListSerializer.Meta.fields, [
                'tickets',
            ]
        )


class DefaultUserProfileSerializer(serializers.ModelSerializer, SerializerAdditionalMethodsMixin):
    password = serializers.CharField(min_length=8, max_length=250, write_only=True)
    creation_date = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='date_joined',
    )
    updated_at = serializers_fields.SerializerMethodKwargsField(
        method_name='get_readable_date',
        field_name='last_changes',
    )
    # opened_tickets_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
            'creation_date',
            'updated_at',
            'screen_name',
            'first_name',
            'last_name',
            'personal_information',
            'opened_tickets_count',
            'hide_private_info',
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


class ExpandedUserProfileSerializer(DefaultUserProfileSerializer):
    """
        Expanded serializer for view (or change) user's profiles by staff.
    """

    tickets = BasicTicketSerializer(many=True, read_only=True)
    max_no_response_time = serializers_fields.SerializerMethodKwargsField(
        method_name='readable_time_seconds',
        field_name='max_not_answered_seconds',
    )

    class Meta(DefaultUserProfileSerializer.Meta):
        fields = merged(DefaultUserProfileSerializer.Meta.fields, [
            'is_support',
            'is_staff',
            'max_no_response_time',
            'tickets'
        ])


class FullUserProfileSerializer(ExpandedUserProfileSerializer):
    """
        Wider than ExpandedUserProfileSerializer.
    """
    class Meta(ExpandedUserProfileSerializer.Meta):
        fields = merged(ExpandedUserProfileSerializer.Meta.fields, [
            'tickets'
        ])
