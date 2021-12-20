from django.contrib import admin

from .models import AppUser, Message, Ticket

# Register your models here.


class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'is_staff',
        'is_support',
        'opened_tickets_count',
        'unanswered_since',
        'date_joined'
    )
    list_display_links = ('id', 'username')
    list_editable = ('is_staff', 'is_support',)
    search_fields = ('id', 'is_staff', 'is_support', 'opened_tickets_count', 'unanswered_since')
    list_filter = ('is_staff', 'is_support', 'opened_tickets_count', 'unanswered_since')


class TicketsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ticket_theme',
        'opened_by',
        'is_closed',
        'is_frozen',
        'creation_date',
        'user_question_date',
    )
    list_display_links = ('id',)
    search_fields = ('id', 'ticket_theme', 'is_closed', 'is_frozen',)
    list_editable = ('ticket_theme', 'is_closed', 'is_frozen', 'opened_by',)
    list_filter = ('ticket_theme', 'is_closed', 'is_frozen', 'creation_date', 'user_question_date')


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'linked_user',
        'linked_ticket',
    )
    list_display_links = ('id',)
    search_fields = ('id', 'linked_user', 'linked_ticket')
    list_filter = ('linked_user', 'linked_ticket')


admin.site.register(AppUser, UsersAdmin)
admin.site.register(Ticket, TicketsAdmin)
admin.site.register(Message, MessageAdmin)
