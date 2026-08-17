"""URL patterns of the admin_panel app.

Everything sits under /manage/ so that it never runs into /admin/,
which belongs to Django's own site.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('manage', views.dashboard, name='manage_dashboard'),
    path('manage/report.csv', views.export_report, name='manage_report'),

    path('manage/users', views.user_list, name='manage_users'),
    path(
        'manage/users/<int:pk>/role',
        views.set_user_role,
        name='manage_user_role',
    ),
    path(
        'manage/users/<int:pk>/active',
        views.set_user_active,
        name='manage_user_active',
    ),
    path(
        'manage/users/<int:pk>/delete',
        views.delete_user,
        name='manage_user_delete',
    ),

    path('manage/posts', views.post_list, name='manage_posts'),
    path(
        'manage/posts/<int:pk>/edit',
        views.edit_post,
        name='manage_post_edit',
    ),
    path(
        'manage/posts/<int:pk>/delete',
        views.delete_post,
        name='manage_post_delete',
    ),

    path(
        'manage/categories',
        views.category_list,
        name='manage_categories',
    ),
    path(
        'manage/categories/<int:pk>/rename',
        views.rename_category,
        name='manage_category_rename',
    ),
    path(
        'manage/categories/<int:pk>/delete',
        views.delete_category,
        name='manage_category_delete',
    ),
]
