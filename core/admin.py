"""Admin site setup for the core app.

Registering a model here is what makes it appear at /admin/. Feature 10
(Admin Management) is built mostly on top of these pages.
"""

from django.contrib import admin

from .models import Category, Claim, Item, Notification, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'item_type', 'status',
                    'location', 'date', 'posted_by']
    list_filter = ['item_type', 'status', 'category']
    search_fields = ['item_name', 'description', 'location']


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['item', 'claimed_by', 'status', 'reviewed_by',
                    'created_at']
    list_filter = ['status']
    search_fields = ['item__item_name', 'claimed_by__username']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'university_id', 'phone_number', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'university_id']
