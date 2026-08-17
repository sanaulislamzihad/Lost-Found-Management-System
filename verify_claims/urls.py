"""URL patterns of the verify_claims app."""

from django.urls import path

from . import views

urlpatterns = [
    path('verify', views.claim_queue, name='claim_queue'),
    path('verify/<int:pk>', views.review_claim, name='review_claim'),
]
