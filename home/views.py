"""Views of the home app.

This app holds the landing page of the site and, later on, the
registration and login pages.
"""

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render

from .models import Item, Profile

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
    """Show the registration form and create the account.

    The SRS asks for four fields: full name, university or employee ID,
    email and password. The email is also saved as the username, so a
    member can log in with the email later on.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :return: the registration page on GET, the home page after a
        successful registration.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return render(request, 'register.html')

    full_name = request.POST['full_name']
    university_id = request.POST['university_id']
    email = request.POST['email']
    password = request.POST['password']

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

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=full_name,
    )

    # The profile row already exists because of the post_save signal.
    user.profile.university_id = university_id
    user.profile.save()

    messages.info(request, 'Registration successful. You can log in now.')
    return redirect('index')
