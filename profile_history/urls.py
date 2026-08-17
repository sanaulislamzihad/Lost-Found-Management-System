"""URL patterns of the profile_history app."""

from django.urls import path

from . import views

urlpatterns = [
    path('profile', views.my_profile, name='my_profile'),
    path('my-history', views.my_history, name='my_history'),
]
