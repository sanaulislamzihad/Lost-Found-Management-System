"""Views of the home app.

This app holds the landing page of the site and, later on, the
registration and login pages.
"""

from django.shortcuts import render


def index(request):
    """Show the landing page of the website.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :return: the rendered landing page.
    :rtype: HttpResponse.
    """
    return render(request, 'index.html')
