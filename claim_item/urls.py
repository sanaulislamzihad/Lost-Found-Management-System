"""URL patterns of the claim_item app."""

from django.urls import path

from . import views

urlpatterns = [
    path('items/<int:pk>/claim', views.claim_item, name='claim_item'),
    path('my-claims', views.my_claims, name='my_claims'),
]
