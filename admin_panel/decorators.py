"""The door on every management page.

Feature 10 belongs to the Admin alone, so each view of this app is
written with ``@admin_required`` above it and none of them has to
repeat the check.
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def is_admin(user):
    """Tell whether this user may open the management pages.

    A Django superuser is let in as well, because that is the account
    the very first Admin of the system is made from.

    :param user: the visitor being checked.
    :type user: User or AnonymousUser.
    :return: True for an Admin or a superuser.
    :rtype: bool.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    profile = getattr(user, 'profile', None)
    return profile is not None and profile.is_admin()


def admin_required(view_function):
    """Let only an Admin through to the view.

    A visitor who is not logged in is sent to the login page and
    brought back afterwards. Somebody who is logged in but is not an
    Admin gets 403 Forbidden, because sending them to a login page
    they have already passed would only be confusing.

    :param view_function: the view being protected.
    :type view_function: callable.
    :return: the wrapped view.
    :rtype: callable.
    """
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if not is_admin(request.user):
            raise PermissionDenied

        return view_function(request, *args, **kwargs)

    return wrapper
