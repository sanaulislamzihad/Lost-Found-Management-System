"""Context processor of the verify_claims app.

An officer should see from any page that claims are waiting, so the
number reaches every template at once instead of every view of the
system having to remember to put it in its own context.
"""

from core.models import Claim

from .decorators import is_officer


def pending_claims(request):
    """Add the number of claims waiting, and who may see the queue.

    The flag is given as well as the count, because an officer with an
    empty queue still has to be shown the way to it, and a count of
    zero on its own cannot be told apart from having no count at all.

    :param request: the HTTP request being answered.
    :type request: HttpRequest.
    :return: ``can_verify_claims`` and ``pending_claim_count``, or
        nothing at all for anybody who may not decide on claims.
    :rtype: dict.
    """
    if not is_officer(request.user):
        return {}

    return {
        'can_verify_claims': True,
        'pending_claim_count': Claim.objects.filter(status='pending').count(),
    }
