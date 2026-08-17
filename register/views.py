"""
This module is used to hold the views of the register app.
"""

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render

from core.models import Profile


def register(request):
    """
    This method is used to show the registration form and to create the
    account when the form is submitted. The email is saved as the
    username as well, so the member can log in with it later.

    :param request: it's a HttpRequest from the user.
    :type request: HttpRequest.
    :return: the registration page, or the login page once the account
     is created.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return render(request, 'register.html')

    full_name = request.POST.get('full_name', '').strip()
    university_id = request.POST.get('university_id', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    # The template marks every box required, but the fields are checked
    # here again because a request can be sent without the form.
    if not full_name:
        messages.error(request, 'Please write your full name.')
        return render(request, 'register.html')

    if not university_id:
        messages.error(request, 'Please write your university or employee ID.')
        return render(request, 'register.html')

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, 'Please enter a valid email address.')
        return render(request, 'register.html')

    try:
        validate_password(password)
    except ValidationError as error:
        for text in error.messages:
            messages.error(request, text)
        return render(request, 'register.html')

    if User.objects.filter(email=email).exists():
        messages.error(request, 'This email is already registered.')
        return render(request, 'register.html')

    if Profile.objects.filter(university_id=university_id).exists():
        messages.error(request, 'This ID is already registered.')
        return render(request, 'register.html')

    # create_user hashes the password, so the plain text is never saved.
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=full_name,
    )

    # The profile row is already there because of the post_save signal
    # in the core app.
    user.profile.university_id = university_id
    user.profile.save()

    messages.info(request, 'Registration successful. You can log in now.')
    return redirect('login')
