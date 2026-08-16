"""Views of the notifications app.

Feature 8 of the SRS lives here: the panel that lists everything the
system has told this member, with a read and unread mark, and the
switch that asks for an email copy of the same messages.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Notification


@login_required
def notification_list(request):
    """Show the notification panel of the member who is logged in.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :return: the rendered panel.
    :rtype: HttpResponse.
    """
    # Notification.Meta already orders these newest first.
    notifications = request.user.notifications.all()

    context = {
        'notifications': notifications,
        'email_copy_on': request.user.profile.email_notifications,
    }
    return render(request, 'notifications.html', context)


@login_required
def open_notification(request, pk):
    """Mark one message as read and go to the page it points at.

    Opening a message is what marks it read, the way a mailbox works,
    so there is no separate button to press for every single line.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :param pk: the id of the message being opened.
    :type pk: int.
    :return: a redirect to the page the message points at, or back to
        the panel when it points at nothing.
    :rtype: HttpResponse.
    """
    # Filtering on the user as well as the id is what stops somebody
    # reading, or marking read, a message that is not theirs.
    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    notification.mark_as_read()

    # Every link is written by our own code and always starts with a
    # slash. Checking that anyway means a full address typed into the
    # admin site cannot turn this page into a way of sending members
    # off to another website.
    if notification.link.startswith('/'):
        return redirect(notification.link)

    return redirect('notification_list')


@login_required
def mark_all_read(request):
    """Mark every message of this member as read.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :return: a redirect back to the panel.
    :rtype: HttpResponse.
    """
    if request.method == 'POST':
        # One UPDATE for the whole lot, because nothing else has to
        # happen per message here.
        request.user.notifications.filter(is_read=False).update(is_read=True)

    return redirect('notification_list')


@login_required
def set_email_copy(request):
    """Turn the email copy of the notifications on or off.

    An unticked checkbox is not sent by the browser at all, so the box
    being absent from the form is what means "off".

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :return: a redirect back to the panel.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return redirect('notification_list')

    profile = request.user.profile
    profile.email_notifications = 'email_copy' in request.POST
    profile.save()

    if profile.email_notifications:
        messages.info(
            request,
            'Email copies are on. Every notification will also be sent '
            'to %s.' % request.user.email,
        )
    else:
        messages.info(request, 'Email copies are off.')

    return redirect('notification_list')
