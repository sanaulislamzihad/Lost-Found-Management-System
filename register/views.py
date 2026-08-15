"""Views of the register app.

Feature 1 of the SRS lives here: a student or a staff member opens an
account with a full name, a university or employee ID, an email and a
password.
"""

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render


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

    if User.objects.filter(email=email).exists():
        messages.error(request, 'This email is already registered.')
        return render(request, 'register.html')

    # create_user hashes the password before it is written, so the
    # plain text never reaches the database.
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=full_name,
    )

    # The profile row already exists because of the post_save signal
    # that the core app connects to the User model.
    user.profile.university_id = university_id
    user.profile.save()

    messages.info(request, 'Registration successful. You can log in now.')
    return redirect('index')
