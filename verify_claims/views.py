"""Views of the verify_claims app.

Feature 7 of the SRS lives here: a Security Officer works through the
claims that are waiting, reads the proof of ownership beside the item
it is about, and either hands the item over or turns the claim down
with a reason.

The two decisions themselves are ``Claim.approve`` and ``Claim.reject``
in the ``core`` app. Everything that follows a decision, closing the
item, closing the other claims on it and telling the people involved,
is written there, so it happens whichever page the decision is taken
from.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.models import CLAIM_STATUS_CHOICES, Claim

from .decorators import officer_required


@officer_required
def claim_queue(request):
    """Show the claims waiting for a decision, oldest first.

    The SRS asks for the pending claims sorted by date, so the person
    who has been waiting longest is dealt with first. The claims that
    are already decided are one tab away, so an officer can look back
    at what was done.

    :param request: the HTTP request sent by the officer.
    :type request: HttpRequest.
    :return: the rendered queue.
    :rtype: HttpResponse.
    """
    claims = Claim.objects.select_related(
        'item', 'item__category', 'claimed_by', 'reviewed_by',
    )

    # Claim.Meta already orders these oldest first, which is the order
    # the SRS asks for.
    status = request.GET.get('status', 'pending')
    if status not in dict(CLAIM_STATUS_CHOICES):
        status = 'pending'

    context = {
        'claims': claims.filter(status=status),
        'statuses': CLAIM_STATUS_CHOICES,
        'status': status,
        'pending_count': claims.filter(status='pending').count(),
    }
    return render(request, 'verify_queue.html', context)


@officer_required
def review_claim(request, pk):
    """Show one claim beside its item, and take the decision.

    :param request: the HTTP request sent by the officer.
    :type request: HttpRequest.
    :param pk: the id of the claim being read.
    :type pk: int.
    :return: the review page on GET, the queue once a decision is
        taken.
    :rtype: HttpResponse.
    """
    claim = get_object_or_404(
        Claim.objects.select_related(
            'item', 'item__category', 'item__posted_by', 'claimed_by',
            'reviewed_by',
        ),
        pk=pk,
    )

    context = {
        'claim': claim,
        # The officer reads the other claims on the same item before
        # deciding, because approving this one closes all of them.
        'other_claims': Claim.objects.filter(
            item=claim.item,
        ).exclude(pk=claim.pk).select_related('claimed_by'),
        'remark': request.POST.get('remark', ''),
    }

    if request.method != 'POST':
        return render(request, 'verify_claim.html', context)

    # A claim is decided once. Deciding it twice would close the item
    # a second time and send a second message to the claimant.
    if claim.status != 'pending':
        messages.error(
            request,
            'This claim was already %s.' % claim.get_status_display().lower(),
        )
        return redirect('claim_queue')

    decision = request.POST.get('decision', '')

    if decision == 'approve':
        claim.approve(request.user)
        messages.info(
            request,
            'Approved. "%s" is now marked as claimed, and everybody who '
            'claimed it has been told.' % claim.item.item_name,
        )
        return redirect('claim_queue')

    if decision == 'reject':
        remark = request.POST.get('remark', '').strip()

        # The SRS makes the remark mandatory when rejecting, so the
        # claimant is never left without a reason.
        if not remark:
            messages.error(
                request,
                'Please write why the claim is being rejected.',
            )
            return render(request, 'verify_claim.html', context)

        claim.reject(request.user, remark)
        messages.info(
            request,
            'Rejected. %s has been told why.'
            % (claim.claimed_by.first_name or claim.claimed_by.username),
        )
        return redirect('claim_queue')

    messages.error(request, 'Please choose approve or reject.')
    return render(request, 'verify_claim.html', context)
