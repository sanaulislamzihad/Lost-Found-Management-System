"""URL configuration for the lost_and_found project.

Every feature of the system has its own app, and each app keeps its own
urls.py file. This file only collects them together and gives each app a
prefix, so two members can add their URLs without touching the same lines.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('home.urls')),
    path('', include('register.urls')),
    path('', include('login_logout.urls')),
    path('', include('report_found_item.urls')),
    path('', include('search_items.urls')),
    path('admin/', admin.site.urls),
]

# During development Django serves the uploaded item photos itself.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
