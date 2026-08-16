"""The rules that decide who hears about what.

Feature 8 of the SRS names three moments when the system has to tell
somebody something:

* a claim was approved or rejected,
* a new found item of the same category as somebody's lost post
  turned up,
* somebody sent a claim on a found item post.

The first one happens inside ``core.models.Claim.approve`` and
``core.models.Claim.reject``, because it belongs to the decision
itself. The other two happen on a page, so they are written here and
the view of that page calls one line. Keeping them out of the views
means the message can be reworded in one place instead of five.
"""

from django.urls import reverse

from core.models import Item, Notification

# A lost post is still worth telling somebody about while it is in one
# of these two states. A claimed or resolved post is finished with.
OPEN_STATUSES = ('pending', 'available')


def display_name(user):
    """Return the name to show for a member inside a message.

    :param user: the member being named.
    :type user: User.
    :return: the full name if there is one, otherwise the username.
    :rtype: str.
    """
    return user.first_name or user.username


def notify_finder_of_new_claim(claim):
    """Tell the finder that somebody has claimed their found item.

    :param claim: the claim that was just sent.
    :type claim: Claim.
    :return: the notification that was saved.
    :rtype: Notification.
    """
    return Notification.send(
        claim.item.posted_by,
        '%s has sent a claim on your found item "%s".'
        % (display_name(claim.claimed_by), claim.item.item_name),
        link=claim.get_absolute_url(),
    )


def notify_matching_lost_posters(found_item):
    """Tell everybody who lost this kind of thing that one turned up.

    The SRS matches on the category, which is the one field a finder
    and an owner are likely to agree on. The finder is left out, and a
    member with several open lost posts in the same category is told
    once and not once per post.

    :param found_item: the found item post that was just saved.
    :type found_item: Item.
    :return: the notifications that were saved.
    :rtype: list.
    """
    lost_posts = Item.objects.filter(
        item_type='lost',
        category_id=found_item.category_id,
        status__in=OPEN_STATUSES,
    ).exclude(
        posted_by_id=found_item.posted_by_id,
    ).select_related('posted_by')

    link = reverse('item_detail', kwargs={'pk': found_item.pk})

    told = set()
    sent = []

    for lost_post in lost_posts:
        if lost_post.posted_by_id in told:
            continue
        told.add(lost_post.posted_by_id)

        sent.append(Notification.send(
            lost_post.posted_by,
            'A new found item was posted in %s: "%s", at %s. It may be '
            'the one you lost.'
            % (found_item.category.name, found_item.item_name,
               found_item.location),
            link=link,
        ))

    return sent
