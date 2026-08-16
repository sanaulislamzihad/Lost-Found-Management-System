"""URL patterns of the report_found_item app."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        'items/found',
        views.report_found_item,
        name='report_found_item',
    ),
    path(
        'items/found/<int:pk>/edit',
        views.edit_found_item,
        name='edit_found_item',
    ),
    path(
        'items/found/<int:pk>/delete',
        views.delete_found_item,
        name='delete_found_item',
    ),
]
