
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from app_support import views

urlpatterns = [
    path('', views.BasicPageInfoView, name='home_page'),
    path('tokens/obtain/', TokenObtainPairView.as_view(), name='obtain_token'),  # simpleJWT
    path('tokens/refresh/', TokenRefreshView.as_view(), name='refresh_token'),  # simpleJWT
    path('users/', views.UsersListView.as_view(), name='users_list'),
    path('users/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),
    path('users/me/', views.UserProfileView.as_view(), {'pk': 0}, name='user_profile2'),
    path('tickets/', views.TicketsListView.as_view(), name='tickets_list'),
    path('tickets/my/', views.TicketsListView.as_view(), {'user_id': 0}, name='tickets_list_owner'),
    path('tickets/<int:ticket_id>/', views.TicketView.as_view(), name='specific_ticket'),
    path('tickets/<int:ticket_id>/messages/', views.MessagesView.as_view(), name='specific_ticket_messages'),

    # unnecessary, but perhaps convenient urls:
    path('users/<int:pk>/tickets/', views.TicketsListView.as_view()),
    path('users/<int:pk>/tickets/<int:ticket_id>/', views.TicketView.as_view()),
    path('tickets/<int:ticket_id>/messages/<int:message_id>/', views.MessageView.as_view(), name='specific_message'),

    path('<path:some_path>', views.error404_view, name='unknown_page'),
]
# handler404 = views.error404_view
urlpatterns = format_suffix_patterns(urlpatterns)
