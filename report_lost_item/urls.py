"""URL patterns of the report_lost_item app."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        'items/lost',
        views.report_lost_item,
        name='report_lost_item',
    ),
    path(
        'items/lost/<int:pk>/edit',
        views.edit_lost_item,
        name='edit_lost_item',
    ),
    path(
        'items/lost/<int:pk>/delete',
        views.delete_lost_item,
        name='delete_lost_item',
    ),
    path(
        'items/lost/<int:pk>/resolve',
        views.resolve_lost_item,
        name='resolve_lost_item',
    ),
]
