"""
This module is used to hold the views of the login_logout app.
"""

from django.contrib import auth, messages
from django.shortcuts import redirect, render

from core.models import LOCK_MINUTES, Profile


def login(request):
    """
    This method is used to show the login page and to let a member in
    when the form is submitted. Django's own login function has the
    same name as this view, so the module is imported as ``auth``.

    :param request: it's a HttpRequest from the user.
    :type request: HttpRequest.
    :return: the login page, or the home page once the member is in.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return render(request, 'login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    # The email is also the username, so the profile is found before
    # the password is checked.
    profile = Profile.objects.filter(user__username=email).first()

    # The lock is read first, so a correct password does not open a
    # shut account either.
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
        # One message for both cases, so a stranger cannot find out
        # which emails are registered.
        messages.error(request, 'Wrong email or password.')
        return render(request, 'login.html')

    profile.note_successful_login()
    auth.login(request, user)
    return redirect('index')


def logout(request):
    """
    This method is used to end the session and send the member back to
    the home page.

    :param request: it's a HttpRequest from the user.
    :type request: HttpRequest.
    :return: a redirect to the home page.
    :rtype: HttpResponse.
    """
    auth.logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')
