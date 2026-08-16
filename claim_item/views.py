"""Views of the claim_item app.

Feature 6 of the SRS lives here: a member who recognises their own
belonging in a found item post sends a claim with the proof that it is
theirs, and then watches on one page what happened to every claim they
have made.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Claim, Item
from notifications.services import notify_finder_of_new_claim


def blocked_reason(item, user):
    """Say why this member is not allowed to claim this item.

    The SRS puts three doors in front of a claim. The detail page hides
    the button when any of them is shut, but the address can also be
    typed by hand, so the same three are read here before the form is
    shown and again before anything is saved.

    :param item: the found item post being claimed.
    :type item: Item.
    :param user: the member who wants to claim it.
    :type user: User.
    :return: the sentence to show, or None when the claim is allowed.
    :rtype: str or None.
    """
    if item.posted_by_id == user.id:
        return 'This is your own post, so there is nothing to claim here.'

    if not item.is_open():
        return 'This item is already closed, so it cannot be claimed.'

    if Claim.objects.filter(item=item, claimed_by=user).exists():
        return 'You have already sent a claim on this item.'

    return None


@login_required
def claim_item(request, pk):
    """Show the claim form for one found item and save the claim.

    The claim is saved with the status "Pending", which is what puts it
    on the list the Security Officer works through in Feature 7.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :param pk: the id of the found item post being claimed.
    :type pk: int.
    :return: the claim form on GET, the list of the member's claims
        once the claim is saved.
    :rtype: HttpResponse.
    """
    item = get_object_or_404(
        Item.objects.select_related('category', 'posted_by'),
        pk=pk,
        item_type='found',
    )

    reason = blocked_reason(item, request.user)
    if reason is not None:
        messages.error(request, reason)
        return redirect('item_detail', pk=item.pk)

    if request.method != 'POST':
        return render(request, 'claim_item.html', {'item': item, 'proof': ''})

    proof = request.POST.get('proof', '').strip()

    # The SRS makes the proof of ownership the whole point of a claim,
    # so an empty box is not a claim at all.
    if not proof:
        messages.error(
            request,
            'Please write your proof of ownership before sending the claim.',
        )
        return render(
            request,
            'claim_item.html',
            {'item': item, 'proof': proof},
        )

    claim = Claim.objects.create(
        item=item,
        claimed_by=request.user,
        proof=proof,
    )

    # Feature 8: the person who handed the item in hears about it.
    notify_finder_of_new_claim(claim)

    messages.info(
        request,
        'Your claim has been sent. A Security Officer will check it and '
        'you will be told the decision.',
    )
    return redirect('my_claims')


@login_required
def my_claims(request):
    """Show every claim this member has made and where each one stands.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :return: the rendered list of the member's own claims.
    :rtype: HttpResponse.
    """
    # Newest first, because the claim somebody just sent is the one
    # they came to the page to look at. select_related fetches the item
    # and its category in the same query as the claims.
    claims = Claim.objects.filter(
        claimed_by=request.user,
    ).select_related('item', 'item__category').order_by('-created_at')

    return render(request, 'my_claims.html', {'claims': claims})
