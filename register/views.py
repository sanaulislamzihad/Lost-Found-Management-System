"""Views of the register app.

Feature 1 of the SRS lives here: a student or a staff member opens an
account with a full name, a university or employee ID, an email and a
password.
"""

from django.shortcuts import render


def register(request):
    """Show the registration form.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :return: the rendered registration page.
    :rtype: HttpResponse.
    """
    return render(request, 'register.html')
