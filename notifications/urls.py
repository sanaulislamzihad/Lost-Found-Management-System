"""URL patterns of the notifications app."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        'notifications',
        views.notification_list,
        name='notification_list',
    ),
    path(
        'notifications/read-all',
        views.mark_all_read,
        name='mark_all_notifications_read',
    ),
    path(
        'notifications/email',
        views.set_email_copy,
        name='set_email_copy',
    ),
    path(
        'notifications/<int:pk>/open',
        views.open_notification,
        name='open_notification',
    ),
]
