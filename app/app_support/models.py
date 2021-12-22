from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Min
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app_support import models_const


class AppUserManager(BaseUserManager):
    """
        Custom user model manager where email is the unique identifiers
        for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
            Create and save a SuperUser with the given email and password.
            is_support = True by default to get all support-only credentials.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_support', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractUser):
    """
        Custom User.
    """
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    date_joined = models.DateTimeField(default=timezone.now)
    is_support = models.BooleanField(default=False)
    last_changes = models.DateTimeField(auto_now_add=True)
    hide_private_info = models.BooleanField(default=False)
    screen_name = models.CharField(max_length=250, blank=True)
    personal_information = models.TextField(max_length=2000, blank=True)
    current_opened_tickets_count = models.IntegerField(default=0, editable=False, name='opened_tickets_count')
    earliest_unanswered_ticket_question_date = models.DateTimeField(blank=True, null=True, name='unanswered_since')
    tickets_messages = models.IntegerField(default=0, editable=False)
    objects = AppUserManager()

    class Meta:
        ordering = ['unanswered_since', 'id']

    @property
    def max_not_answered_seconds(self):
        """
            Returns ([int]) seconds count left after user's question.
            Can be usefull for ordering (by support).
        """
        delta = 0
        if self.unanswered_since:
            delta = (timezone.now() - self.unanswered_since).total_seconds()
        return delta

    def save(self, *args, **kwargs):
        """
            Also updates last_changes field
        """
        self.last_changes = timezone.now()
        super().save(*args, **kwargs)  # call the actual save method

    def __str__(self):
        return self.get_screen_name()

    def update_user_fields(self):
        """
            This method will mostly called when some Ticket/Message fields values changed /new created.
            Recalculates some related AppUser fields as tickets_messages
        """
        self.tickets_messages = self.messages.count()
        self.current_opened_tickets_count = self.tickets.filter(is_closed=False).count()
        unanswered_since = (
            self.tickets.exclude(
                user_question_date=None
                ).filter(
                    is_answered=False
                ).aggregate(
                    Min('user_question_date')
                )['user_question_date__min']
        )
        if unanswered_since:
            self.unanswered_since = unanswered_since
        else:
            self.unanswered_since = None
        self.save()

    def get_screen_name(self):
        """
            Returns User's id if screen_name wasn't set.
            Add postfix to screen name according User's status.
        """
        tail = ''
        if self.is_staff:
            tail = ' (admin)'
        elif self.is_support:
            tail = ' (support)'
        if self.screen_name:
            screen_name = self.screen_name
        elif not self.hide_private_info:
            screen_name = self.username
        else:
            screen_name = f'user (id #{self.id})'
        return screen_name+tail


def get_current_tc_user_object():
    """
    returns an user-object,
    which collects all tickets for deleted users.
    """
    user_object = AppUser.objects.get_or_create(
        username=settings.APP_SUPPORT_DEFAULTS['TICKETS_COLLECTOR_NAME']
    )[0]
    return user_object


class Ticket(models.Model):
    """
        Ticket model will be used to collect messages from users.
    """
    ticket_theme = models.CharField(
        max_length=255,
        choices=models_const.TICKET_THEMES,
    )
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_current_tc_user_object),
        related_name="tickets",
        related_query_name="ticket",
    )
    answerer_id = models.PositiveIntegerField(blank=True, null=True, editable=False)
    creation_date = models.DateTimeField(default=timezone.now, editable=False)
    is_frozen = models.BooleanField(default=False)  # True = ticket is frozen
    is_closed = models.BooleanField(default=False)
    staff_note = models.TextField(max_length=10000, blank=True, default='')

    # the following fields will be monitored automatically by save() and other methods
    last_changes = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    user_question_date = models.DateTimeField(blank=True, null=True, editable=False)
    closed_by_id = models.PositiveIntegerField(blank=True, null=True, editable=False)
    messages_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ['id', 'ticket_theme', 'user_question_date', 'last_changes', 'is_answered']  # , 'is_opened'

    @property
    def not_answered_time(self):
        if self.is_answered is False and self.user_question_date:
            return int((timezone.now() - self.user_question_date).total_seconds())
        return 0

    def save(self, *args, **kwargs):
        self.last_changes = timezone.now()  # update 'last_update' field
        super().save(*args, **kwargs)  # call the actual save method
        self.opened_by.update_user_fields()

    def delete(self, *args, **kwargs):
        user = self.opened_by
        res = super().delete(*args, **kwargs)
        user.update_user_fields()  # dont forget to update_user_fields
        return res

    def update_related_ticket_fields(self, message_owner=None):
        """
            This method will mostly called when some Message objects created/deleted.
        """
        self.messages_count = self.messages.count()
        if message_owner:
            if message_owner.id == self.opened_by.id:
                self.user_question_date = timezone.now()
                self.is_answered = False
            else:
                self.is_answered = True
                self.answerer_id = message_owner.id
                self.user_question_date = None
        self.save()


class Message(models.Model):
    related_class = Ticket

    linked_ticket = models.ForeignKey(
        related_class,
        on_delete=models.CASCADE,
        related_name="messages",
        related_query_name="message",
    )
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_current_tc_user_object),
        related_name="messages",
        related_query_name="message",
    )
    body = models.TextField(max_length=1000, default='')
    creation_date = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)  # call the actual save method
        self.linked_ticket.update_related_ticket_fields(message_owner=self.linked_user)
        return res

    def delete(self, *args, **kwargs):
        ticket, user = self.linked_ticket, self.linked_user
        res = super().delete(*args, **kwargs)
        if ticket:  # If ticket was deleted?
            ticket.update_related_ticket_fields(message_owner=user)
        return res

    def __str__(self):
        return (
            f'Message (ticket={self.linked_ticket.id})'
            f' (written_by={self.linked_user.username})'
            f' body= {self.body[:40]}'
        )
