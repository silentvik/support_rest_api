from django.contrib import admin

from .models import AppUser, Message, Ticket

# Register your models here.


class TicketsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        # 'opened_by',
        # 'ticket_theme',
        # 'is_closed',
        # 'creation_date',
        # 'last_support_answer',
        # 'not_answered_time',
        # 'all_messages'
    )
    # list_display_links = ('id', 'ticket_theme')
    # search_fields = ('id', 'ticket_theme', 'opened_by')
    # list_editable = ('is_closed',)
    # list_filter = ('is_closed', 'creation_date')


class MessageAdmin(admin.ModelAdmin):
    pass


admin.site.register(AppUser)
admin.site.register(Ticket, TicketsAdmin)
admin.site.register(Message)
