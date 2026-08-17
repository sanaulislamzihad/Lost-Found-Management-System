"""Views of the report_lost_item app.

Feature 3 of the SRS lives here: a member who has lost something posts
it so that whoever picks it up can find the owner. The same views let
them correct the post, take it down, and close it once the item is
back in their hands.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from core.models import Category, Item


def read_date(text):
    """Turn the text of a date box into a real date.

    The date box of the browser sends ``2026-07-12``, but a request can
    be sent without the form and carry anything at all, so a value that
    is not a date has to come back as nothing instead of crashing.

    :param text: whatever the date box sent.
    :type text: str.
    :return: the date, or None when the text is not a date.
    :rtype: datetime.date or None.
    """
    try:
        return parse_date(text)
    except ValueError:
        # parse_date raises this for something like 2026-02-31, which
        # is written the right way but is not a real day.
        return None


def clean_lost_form(request):
    """Check the five fields of the lost item form.

    The template marks every box required, but that only stops an
    honest browser, so the SRS rule "check that all the required fields
    are filled before saving" is applied again here. The create view
    and the edit view both call this one function.

    :param request: the HTTP request that carries the submitted form.
    :type request: HttpRequest.
    :return: the clean values ready for the Item table, or None when
        something was wrong. Every problem is added as a message before
        None is returned.
    :rtype: dict or None.
    """
    item_name = request.POST.get('item_name', '').strip()
    category_id = request.POST.get('category', '')
    description = request.POST.get('description', '').strip()
    location = request.POST.get('location', '').strip()
    date = read_date(request.POST.get('date', ''))

    if not item_name:
        messages.error(request, 'Please write what you lost.')
        return None

    # The category is picked from a dropdown, so anything that is not
    # a number means the box was left alone.
    category = None
    if category_id.isdigit():
        category = Category.objects.filter(pk=category_id).first()

    if category is None:
        messages.error(request, 'Please choose a category.')
        return None

    if not description:
        messages.error(request, 'Please describe the item.')
        return None

    if not location:
        messages.error(request, 'Please write where you last saw it.')
        return None

    if date is None:
        messages.error(request, 'Please choose the date you lost it.')
        return None

    if date > timezone.localdate():
        messages.error(request, 'The date lost cannot be in the future.')
        return None

    return {
        'item_name': item_name,
        'category': category,
        'description': description,
        'location': location,
        'date': date,
    }


def form_from_item(item):
    """Copy a saved post back into the shape the template reads.

    The edit page fills its boxes from the same ``form`` variable that
    the create page uses, so the one template works for both pages.

    :param item: the lost item post being edited.
    :type item: Item.
    :return: the values of the post, keyed by the name of each box.
    :rtype: dict.
    """
    return {
        'item_name': item.item_name,
        'category': item.category_id,
        'description': item.description,
        'location': item.location,
        # The date box of the browser only understands 2026-07-12.
        'date': item.date.isoformat(),
    }


def own_lost_item(request, pk):
    """Find one lost item post that belongs to the member.

    The SRS says a member can edit or delete only their own post, so
    every view that changes a post starts with this check.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :param pk: the id of the post in the Item table.
    :type pk: int.
    :return: the post when it is theirs, otherwise None.
    :rtype: Item or None.
    """
    item = get_object_or_404(Item, pk=pk, item_type='lost')

    if item.posted_by_id != request.user.id:
        return None

    return item


@login_required
def report_lost_item(request):
    """Show the lost item form and save a new post from it.

    The SRS asks for five fields and an optional photo, and it asks for
    the post to start with the status "Pending", because nothing has
    happened to the report yet.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :return: the form on GET, the page of the new post after it is
        saved.
    :rtype: HttpResponse.
    """
    context = {
        'categories': Category.objects.all(),
        'form': request.POST or {},
        'heading': 'Report a lost item',
        'button': 'Post it',
    }

    if request.method != 'POST':
        return render(request, 'report_lost_item.html', context)

    clean = clean_lost_form(request)
    if clean is None:
        return render(request, 'report_lost_item.html', context)

    item = Item.objects.create(
        item_type='lost',
        status='pending',
        posted_by=request.user,
        # The photo is not required, and .get() gives None when the
        # member left the file box empty.
        image=request.FILES.get('image'),
        **clean,
    )

    messages.info(
        request,
        'Your lost item post is live now. You will be told if something '
        'like it is handed in.',
    )
    return redirect('item_detail', pk=item.pk)


@login_required
def edit_lost_item(request, pk):
    """Let the owner correct their own lost item post.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :param pk: the id of the post being edited.
    :type pk: int.
    :return: the filled form on GET, the page of the post after it is
        saved.
    :rtype: HttpResponse.
    """
    item = own_lost_item(request, pk)
    if item is None:
        messages.error(request, 'You can edit only your own post.')
        return redirect('item_detail', pk=pk)

    context = {
        'categories': Category.objects.all(),
        'form': request.POST or form_from_item(item),
        'heading': 'Edit your lost item post',
        'button': 'Save changes',
        'item': item,
    }

    if request.method != 'POST':
        return render(request, 'report_lost_item.html', context)

    clean = clean_lost_form(request)
    if clean is None:
        return render(request, 'report_lost_item.html', context)

    for field, value in clean.items():
        setattr(item, field, value)

    # A new photo replaces the old one, and sending the form without
    # choosing a file keeps the photo that is already there.
    new_image = request.FILES.get('image')
    if new_image is not None:
        item.image = new_image

    item.save()

    messages.info(request, 'Your post has been updated.')
    return redirect('item_detail', pk=item.pk)


@login_required
def delete_lost_item(request, pk):
    """Ask before taking a lost item post down, then take it down.

    The SRS asks for a confirmation before deleting, so opening the
    page only shows the question and the post is removed only when the
    member presses the button on that page.

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :param pk: the id of the post being deleted.
    :type pk: int.
    :return: the question page on GET, the item list once the post is
        gone.
    :rtype: HttpResponse.
    """
    item = own_lost_item(request, pk)
    if item is None:
        messages.error(request, 'You can delete only your own post.')
        return redirect('item_detail', pk=pk)

    if request.method != 'POST':
        return render(request, 'delete_lost_item.html', {'item': item})

    item.delete()

    messages.info(request, 'The post has been deleted.')
    return redirect('item_list')


@login_required
def resolve_lost_item(request, pk):
    """Close the post because the member has the item back.

    The SRS keeps a recovered report in the history instead of
    deleting it, so this only moves the status to "Resolved".

    :param request: the HTTP request sent by the member.
    :type request: HttpRequest.
    :param pk: the id of the post being closed.
    :type pk: int.
    :return: a redirect back to the page of the post.
    :rtype: HttpResponse.
    """
    item = own_lost_item(request, pk)
    if item is None:
        messages.error(request, 'You can close only your own post.')
        return redirect('item_detail', pk=pk)

    # Closing is a change, so it only happens on POST. A link that
    # somebody follows by accident must not close their report.
    if request.method != 'POST':
        return redirect('item_detail', pk=item.pk)

    if not item.is_open():
        messages.error(request, 'This post is already closed.')
        return redirect('item_detail', pk=item.pk)

    item.mark_as_resolved()

    messages.info(request, 'Good news. The post is marked as resolved.')
    return redirect('item_detail', pk=item.pk)
