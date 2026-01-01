from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation_list'),
    path('conversation/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('start-conversation/<int:farmer_id>/', views.start_conversation, name='start_conversation'),
    path('send-message/', views.send_message, name='send_message'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('mark-notification-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notification-count/', views.notification_count, name='notification_count'),
]
