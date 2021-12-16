# from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import (  # AbstractBaseUser,; BaseUserManager,; PermissionsMixin,
    AbstractUser, BaseUserManager, User)
from django.db import models
from django.db.models import Min  # Max,
from django.utils import timezone
# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _

from app_support.services.generalized_funcs import \
    accurate_string_seconds  # accurate_string_datetime,

# from django.contrib.auth.hashers import make_password

#
CONFIG = {
    'NAME_OF_TC': 'tickets_collector',
    'TICKET_THEMES': (
        (1, 'product'),
        (2, 'soft'),
        (3, 'security'),
        (4, 'any other'),
    ),
    'WRITTEN_BY': (
        (1, 'user'),
        (2, 'support'),
        (3, 'admin'),
    )
}
# TICKET_THEMES = CONFIG['TICKET_THEMES']


def get_current_tc_user_object():
    """
    returns an user-object,
    which collects all tickets for deleted users.
    """

    user_object = User.objects.get_or_create(
        username=CONFIG['NAME_OF_TC']
    )[0]
    return user_object


TICKET_THEMES = (
        ('1', 'product'),
        ('2', 'soft'),
        ('3', 'security'),
        ('4', 'other'),
)


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
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    date_joined = models.DateTimeField(default=timezone.now)
    is_support = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now_add=True)
    hide_private_info = models.BooleanField(default=False)
    screen_name = models.CharField(max_length=250, blank=True)
    personal_information = models.TextField(max_length=2000, blank=True)

    opened_tickets_count = models.IntegerField(default=0)
    last_answer_date = models.DateTimeField(default=timezone.now)
    objects = AppUserManager()

    @property
    def get_screen_name(self):
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
            screen_name = f'user#{self.id}'
        return screen_name+tail

    @property
    def max_unanswered_time(self):
        # r = Ticket.objects.filter(opened_by=self).order_by('last_support_answer')
        # print(f'r = {r}')
        res = Ticket.objects.filter(opened_by=self).aggregate(Min('last_answer_date'))['last_answer_date__min']
        if res:
            delta = (timezone.now()-res).total_seconds()
        else:
            delta = 0
        return delta

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # call the actual save method
        self.last_update = timezone.now()


class Ticket(models.Model):
    ticket_theme = models.CharField(
        max_length=255,
        choices=TICKET_THEMES,
    )
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_current_tc_user_object),
        related_name="tickets",
        related_query_name="ticket",
    )
    creation_date = models.DateTimeField(default=timezone.now, editable=False)
    last_update = models.DateTimeField(auto_now_add=True)

    is_answered = models.BooleanField(default=False)
    last_answer_date = models.DateTimeField(default=timezone.now)

    is_frozen = models.BooleanField(default=False)  # True = ticket is frozen
    is_closed = models.BooleanField(default=False)
    was_closed_by = models.CharField(
        max_length=250,
        blank=True
    )
    staff_note = models.TextField(max_length=10000, blank=True, default='')
    # messages_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ['id', 'ticket_theme', 'creation_date', 'last_update', 'is_answered', 'last_answer_date']  # , 'is_opened'

    # this field must be in serializer I think
    @property
    def not_answered_time(self):
        if self.is_answered is False:
            return accurate_string_seconds(int((timezone.now() - self.last_support_answer).total_seconds()))
        return accurate_string_seconds(0)

    def save(self, *args, **kwargs):
        self.last_update = timezone.now()  # update 'last_update' field
        super().save(*args, **kwargs)  # call the actual save method


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
        on_delete=models.SET(get_current_tc_user_object)
    )
    body = models.TextField(max_length=1000, default='')
    creation_date = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return (
            f'Message (ticket={self.linked_ticket.id})'
            f' (written_by={self.linked_user.username})'
            f' body= {self.body[:40]}'
        )

    def save(self, *args, **kwargs):
        if self.linked_user.is_support:
            self.linked_ticket.is_answered = True
            self.linked_ticket.last_answer = models.DateTimeField(default=timezone.now)
        else:
            self.linked_ticket.is_answered = False
        super().save(*args, **kwargs)  # call the actual save method
