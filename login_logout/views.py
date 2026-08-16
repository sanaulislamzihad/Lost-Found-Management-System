"""Views of the login_logout app.

Feature 2 of the SRS lives here: a member signs in with the email and
the password they registered with, and signs out when they are done.
"""

from django.contrib import auth, messages
from django.shortcuts import redirect, render

from core.models import LOCK_MINUTES, Profile


def login(request):
    """This method is used to show the login page and to let a member
    in when the form is submitted.

    The email works as the username because registration saves it in
    both fields, so Django's own authenticate call is enough here.

    Django's login function has the same name as this view, so the
    module is imported as ``auth`` and used as ``auth.login``.

    :param request: it's a HttpRequest from the user.
    :type request: HttpRequest.
    :return: the login page, or the home page once the member is in.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return render(request, 'login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    # The email is also the username, so the profile can be found even
    # before the password is checked.
    profile = Profile.objects.filter(user__username=email).first()

    # The lock is read before authenticate, so a correct password does
    # not open a shut account either. The SRS asks for that.
    if profile is not None and profile.is_locked():
        messages.error(
            request,
            'Too many wrong tries. Please try again after %s minutes.'
            % LOCK_MINUTES,
        )
        return render(request, 'login.html')

    user = auth.authenticate(request, username=email, password=password)
    if user is None:
        if profile is not None:
            profile.note_failed_login()
        # One message for both cases on purpose. Saying which half was
        # wrong would tell a stranger that the email exists.
        messages.error(request, 'Wrong email or password.')
        return render(request, 'login.html')

    profile.note_successful_login()
    auth.login(request, user)
    return redirect('index')


def logout(request):
    """This method is used to end the session and send the member back
    to the home page.

    Django's logout clears the session row and the session cookie, so
    pressing the back button does not bring the account back.

    :param request: it's a HttpRequest from the user.
    :type request: HttpRequest.
    :return: a redirect to the home page.
    :rtype: HttpResponse.
    """
    auth.logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')
