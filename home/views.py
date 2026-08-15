"""Views of the home app.

This app holds only the landing page of the site. Every feature of the
system lives in an app of its own, so that two members never have to
write in the same file.
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
