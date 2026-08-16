"""Views of the login_logout app.

Feature 2 of the SRS lives here: a member signs in with the email and
the password they registered with, and signs out when they are done.
"""

from django.contrib import auth, messages
from django.shortcuts import redirect, render


def login(request):
    """Show the login form and start the session.

    The email works as the username because registration saves it in
    both fields, so Django's own authenticate call is enough here.

    Django's login function has the same name as this view, so the
    module is imported as ``auth`` and used as ``auth.login``.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :return: the login page, or the home page once the member is in.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return render(request, 'login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    user = auth.authenticate(request, username=email, password=password)
    if user is None:
        # One message for both cases on purpose. Saying which half was
        # wrong would tell a stranger that the email exists.
        messages.error(request, 'Wrong email or password.')
        return render(request, 'login.html')

    auth.login(request, user)
    return redirect('index')
