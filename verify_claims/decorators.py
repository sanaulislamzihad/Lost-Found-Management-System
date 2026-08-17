"""The door on every claim verification page.

Feature 7 belongs to the Security Officer, so each view of this app is
written with ``@officer_required`` above it and none of them has to
repeat the check.
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def is_officer(user):
    """Tell whether this user may decide on claims.

    An Admin is let in as well, because Feature 10 puts the whole
    platform in their hands and the queue would otherwise be shut to
    the one person who has to keep it moving.

    :param user: the visitor being checked.
    :type user: User or AnonymousUser.
    :return: True for a Security Officer, an Admin or a superuser.
    :rtype: bool.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    profile = getattr(user, 'profile', None)
    if profile is None:
        return False

    return profile.is_officer() or profile.is_admin()


def officer_required(view_function):
    """Let only a Security Officer or an Admin through to the view.

    A visitor who is not logged in is sent to the login page and
    brought back afterwards. Somebody who is logged in but is neither
    gets 403 Forbidden, because sending them to a login page they have
    already passed would only be confusing.

    :param view_function: the view being protected.
    :type view_function: callable.
    :return: the wrapped view.
    :rtype: callable.
    """
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if not is_officer(request.user):
            raise PermissionDenied

        return view_function(request, *args, **kwargs)

    return wrapper
