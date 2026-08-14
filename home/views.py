"""Views of the home app.

This app holds the landing page of the site and, later on, the
registration and login pages.
"""

from django.shortcuts import render

from .models import Item

RECENT_ITEM_LIMIT = 4


def index(request):
    """Show the landing page with the counts and the newest found items.

    The view only asks the models for data and hands it to the template,
    which keeps the MVT layers separate the way our Architectural
    Pattern page describes.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :return: the rendered landing page.
    :rtype: HttpResponse.
    """
    recent_found = Item.objects.filter(
        item_type='found',
        status='available',
    )[:RECENT_ITEM_LIMIT]

    context = {
        'total_posted': Item.objects.count(),
        'total_returned': Item.objects.filter(status='claimed').count(),
        'recent_found': recent_found,
    }
    return render(request, 'index.html', context)


def register(request):
    """Show the registration form.

    The SRS asks for four fields: full name, university or employee ID,
    email and password. Saving the account is added in the next step.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :return: the rendered registration page.
    :rtype: HttpResponse.
    """
    return render(request, 'register.html')
