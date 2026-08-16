"""Context processor of the notifications app.

Every page carries the bell in the navigation bar, so the number of
unread messages has to reach every template. A context processor adds
it to all of them at once, which is better than making each view of
the system remember to put it in its own context.
"""

from core.models import Notification


def unread_notifications(request):
    """Add the number of unread messages of the current member.

    :param request: the HTTP request being answered.
    :type request: HttpRequest.
    :return: the count under ``unread_notification_count``, or nothing
        at all for a visitor who is not logged in.
    :rtype: dict.
    """
    if not request.user.is_authenticated:
        return {}

    return {
        'unread_notification_count': Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count(),
    }
