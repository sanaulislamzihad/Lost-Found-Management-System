"""Views of the profile_history app.

Feature 9 of the SRS lives here: a member reads and corrects their own
details on one page, and on another page follows everything they have
posted and everything they have claimed.
"""

import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.images import get_image_dimensions
from django.shortcuts import redirect, render

from core.models import ITEM_STATUS_CHOICES, Claim, Item

# A phone number is written differently by everybody, so the check is
# on the shape and not on one country's format: digits, and the few
# marks people put between them.
PHONE_PATTERN = re.compile(r'^[0-9+][0-9+\-\s]{6,19}$')

# Photos are shown at about 200 pixels wide, so anything past a couple
# of megabytes is only filling up the disk.
MAX_PHOTO_BYTES = 2 * 1024 * 1024


def clean_photo(request, photo):
    """Check that the uploaded file really is a picture and not too big.

    A model ``ImageField`` does not check anything by itself, so this
    is what keeps a renamed .exe or a fifty megabyte photo out of the
    media folder.

    :param request: the request, used to write the error message on.
    :type request: HttpRequest.
    :param photo: the file the member chose.
    :type photo: UploadedFile.
    :return: True when the file may be saved.
    :rtype: bool.
    """
    if photo.size > MAX_PHOTO_BYTES:
        messages.error(request, 'Please choose a photo under 2 MB.')
        return False

    # get_image_dimensions gives back a pair of Nones for a file that
    # is not a picture at all.
    width, height = get_image_dimensions(photo)
    if width is None or height is None:
        messages.error(request, 'That file is not a picture.')
        return False

    return True


@login_required
def my_profile(request):
    """Show the details of the member and save the ones they may change.

    The SRS locks the email and the university ID after registration,
    because the whole system recognises a member by those two, so they
    are printed on the page but never read back from the form.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :return: the profile page, and the same page again after saving.
    :rtype: HttpResponse.
    """
    profile = request.user.profile

    if request.method != 'POST':
        return render(request, 'profile.html', {'profile': profile})

    full_name = request.POST.get('full_name', '').strip()
    phone_number = request.POST.get('phone_number', '').strip()
    photo = request.FILES.get('photo')

    if not full_name:
        messages.error(request, 'Please write your full name.')
        return render(request, 'profile.html', {'profile': profile})

    # An empty box means the member is clearing the number, which is
    # allowed. Anything else has to look like a phone number.
    if phone_number and not PHONE_PATTERN.match(phone_number):
        messages.error(
            request,
            'Please write a phone number using digits, for example '
            '01712345678.',
        )
        return render(request, 'profile.html', {'profile': profile})

    if photo is not None and not clean_photo(request, photo):
        return render(request, 'profile.html', {'profile': profile})

    request.user.first_name = full_name
    request.user.save()

    profile.phone_number = phone_number
    if photo is not None:
        profile.photo = photo
    profile.save()

    messages.info(request, 'Your profile has been updated.')
    return redirect('my_profile')


@login_required
def my_history(request):
    """Show everything this member has posted and everything they claimed.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :return: the rendered history page.
    :rtype: HttpResponse.
    """
    items = Item.objects.filter(
        posted_by=request.user,
    ).select_related('category')

    # The SRS asks for the list to be narrowed by status. Anything that
    # is not one of the four statuses is ignored, so a hand written
    # address cannot empty the page by accident.
    status = request.GET.get('status', '')
    if status in dict(ITEM_STATUS_CHOICES):
        items = items.filter(status=status)

    claims = Claim.objects.filter(
        claimed_by=request.user,
    ).select_related('item').order_by('-created_at')

    context = {
        'items': items,
        'claims': claims,
        'statuses': ITEM_STATUS_CHOICES,
        'status': status,
        # Counted before the filter, so the tabs keep showing how much
        # there is in total.
        'total_posted': Item.objects.filter(posted_by=request.user).count(),
    }
    return render(request, 'my_history.html', context)
