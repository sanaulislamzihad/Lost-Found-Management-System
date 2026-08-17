"""Views of the admin_panel app.

Feature 10 of the SRS lives here: the Admin looks after the members,
the posts and the categories, reads the statistics of the whole system
and takes the activity report away as a CSV file.

Django's own site at /admin/ is still there for emergencies. These
pages are the ones the SRS describes: they speak the language of the
system instead of the language of the database, and they enforce the
rules of the SRS, which the database admin does not.
"""

import csv

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from core.models import (
    ITEM_STATUS_CHOICES,
    ITEM_TYPE_CHOICES,
    ROLE_CHOICES,
    Category,
    Claim,
    Item,
)

from .decorators import admin_required


def read_date(text):
    """Turn the text of a date box into a real date.

    :param text: whatever the date box sent.
    :type text: str.
    :return: the date, or None when the text is not a date.
    :rtype: datetime.date or None.
    """
    try:
        return parse_date(text)
    except ValueError:
        # Raised for something like 2026-02-31, which is written the
        # right way but is not a real day.
        return None


@admin_required
def dashboard(request):
    """Show the statistics of the whole system on one page.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :return: the rendered dashboard.
    :rtype: HttpResponse.
    """
    context = {
        # The three numbers the SRS names, and then the few that say
        # how much work is waiting.
        'total_lost': Item.objects.filter(item_type='lost').count(),
        'total_found': Item.objects.filter(item_type='found').count(),
        'successful_claims': Claim.objects.filter(status='approved').count(),
        'pending_claims': Claim.objects.filter(status='pending').count(),
        'total_users': User.objects.count(),
        'total_categories': Category.objects.count(),
        'recent_items': Item.objects.select_related(
            'category', 'posted_by',
        )[:5],
    }
    return render(request, 'manage_dashboard.html', context)


@admin_required
def user_list(request):
    """List every member with their role and whether the account is on.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :return: the rendered list of members.
    :rtype: HttpResponse.
    """
    users = User.objects.select_related('profile').order_by('first_name')

    query = request.GET.get('query', '').strip()
    if query:
        # The username is the email address, so one box searches both
        # the name and the email.
        users = users.filter(
            Q(first_name__icontains=query) | Q(username__icontains=query)
        )

    role = request.GET.get('role', '')
    if role in dict(ROLE_CHOICES):
        users = users.filter(profile__role=role)

    context = {
        'users': users,
        'roles': ROLE_CHOICES,
        'query': query,
        'role': role,
    }
    return render(request, 'manage_users.html', context)


@admin_required
def set_user_role(request, pk):
    """Move one member to another role.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :param pk: the id of the member being changed.
    :type pk: int.
    :return: a redirect back to the list of members.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return redirect('manage_users')

    member = get_object_or_404(User, pk=pk)
    role = request.POST.get('role', '')

    if role not in dict(ROLE_CHOICES):
        messages.error(request, 'That is not one of the roles.')
        return redirect('manage_users')

    # An Admin who takes their own Admin role away locks themselves
    # out of these pages, and nobody else can put them back.
    if member == request.user and role != 'admin':
        messages.error(
            request,
            'You cannot take your own Admin role away. Ask another '
            'Admin to do it.',
        )
        return redirect('manage_users')

    member.profile.role = role
    member.profile.save()

    messages.info(
        request,
        '%s is now a %s.'
        % (member.first_name or member.username,
           member.profile.get_role_display()),
    )
    return redirect('manage_users')


@admin_required
def set_user_active(request, pk):
    """Switch one member's account on or off.

    Django refuses the login of a user whose ``is_active`` is off, so
    this one flag is the whole of "activate and deactivate".

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :param pk: the id of the member being changed.
    :type pk: int.
    :return: a redirect back to the list of members.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return redirect('manage_users')

    member = get_object_or_404(User, pk=pk)

    if member == request.user:
        messages.error(request, 'You cannot switch off your own account.')
        return redirect('manage_users')

    member.is_active = not member.is_active
    member.save()

    messages.info(
        request,
        'The account of %s is now %s.'
        % (member.first_name or member.username,
           'active' if member.is_active else 'switched off'),
    )
    return redirect('manage_users')


@admin_required
def delete_user(request, pk):
    """Ask before removing a member, then remove them.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :param pk: the id of the member being removed.
    :type pk: int.
    :return: the question page on GET, the list of members afterwards.
    :rtype: HttpResponse.
    """
    member = get_object_or_404(User, pk=pk)

    if member == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('manage_users')

    if request.method != 'POST':
        context = {
            'member': member,
            # Both of these are cascaded away with the member, so the
            # Admin is told the size of what they are about to do.
            'item_count': Item.objects.filter(posted_by=member).count(),
            'claim_count': Claim.objects.filter(claimed_by=member).count(),
        }
        return render(request, 'manage_delete_user.html', context)

    name = member.first_name or member.username
    member.delete()

    messages.info(request, '%s has been deleted.' % name)
    return redirect('manage_users')


@admin_required
def post_list(request):
    """List every post of the system, whichever member wrote it.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :return: the rendered list of posts.
    :rtype: HttpResponse.
    """
    items = Item.objects.select_related('category', 'posted_by').annotate(
        claim_count=Count('claims'),
    )

    query = request.GET.get('query', '').strip()
    if query:
        items = items.filter(item_name__icontains=query)

    item_type = request.GET.get('type', '')
    if item_type in dict(ITEM_TYPE_CHOICES):
        items = items.filter(item_type=item_type)

    status = request.GET.get('status', '')
    if status in dict(ITEM_STATUS_CHOICES):
        items = items.filter(status=status)

    context = {
        'items': items,
        'item_types': ITEM_TYPE_CHOICES,
        'statuses': ITEM_STATUS_CHOICES,
        'query': query,
        'type': item_type,
        'status': status,
    }
    return render(request, 'manage_posts.html', context)


def clean_post_form(request):
    """Check the fields of the Admin's post form.

    This is the form of Feature 4 with two more boxes on it, because
    an Admin may also move a post between lost and found and set its
    status by hand.

    :param request: the HTTP request that carries the submitted form.
    :type request: HttpRequest.
    :return: the clean values, or None when something was wrong.
    :rtype: dict or None.
    """
    item_name = request.POST.get('item_name', '').strip()
    category_id = request.POST.get('category', '')
    description = request.POST.get('description', '').strip()
    location = request.POST.get('location', '').strip()
    date = read_date(request.POST.get('date', ''))
    item_type = request.POST.get('item_type', '')
    status = request.POST.get('status', '')

    if not item_name:
        messages.error(request, 'Please write the name of the item.')
        return None

    category = None
    if category_id.isdigit():
        category = Category.objects.filter(pk=category_id).first()

    if category is None:
        messages.error(request, 'Please choose a category.')
        return None

    if not description:
        messages.error(request, 'Please write the description.')
        return None

    if not location:
        messages.error(request, 'Please write the place.')
        return None

    if date is None:
        messages.error(request, 'Please choose the date.')
        return None

    if date > timezone.localdate():
        messages.error(request, 'The date cannot be in the future.')
        return None

    if item_type not in dict(ITEM_TYPE_CHOICES):
        messages.error(request, 'Please choose lost or found.')
        return None

    if status not in dict(ITEM_STATUS_CHOICES):
        messages.error(request, 'Please choose a status.')
        return None

    return {
        'item_name': item_name,
        'category': category,
        'description': description,
        'location': location,
        'date': date,
        'item_type': item_type,
        'status': status,
    }


@admin_required
def edit_post(request, pk):
    """Let the Admin correct any post of the system.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :param pk: the id of the post being edited.
    :type pk: int.
    :return: the filled form on GET, the list of posts after saving.
    :rtype: HttpResponse.
    """
    item = get_object_or_404(Item, pk=pk)

    context = {
        'item': item,
        'categories': Category.objects.all(),
        'item_types': ITEM_TYPE_CHOICES,
        'statuses': ITEM_STATUS_CHOICES,
        'form': request.POST or {
            'item_name': item.item_name,
            'category': item.category_id,
            'description': item.description,
            'location': item.location,
            'date': item.date.isoformat(),
            'item_type': item.item_type,
            'status': item.status,
        },
    }

    if request.method != 'POST':
        return render(request, 'manage_post_form.html', context)

    clean = clean_post_form(request)
    if clean is None:
        return render(request, 'manage_post_form.html', context)

    for field, value in clean.items():
        setattr(item, field, value)
    item.save()

    messages.info(request, 'The post has been updated.')
    return redirect('manage_posts')


@admin_required
def delete_post(request, pk):
    """Ask before removing any post, then remove it.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :param pk: the id of the post being removed.
    :type pk: int.
    :return: the question page on GET, the list of posts afterwards.
    :rtype: HttpResponse.
    """
    item = get_object_or_404(Item, pk=pk)

    if request.method != 'POST':
        context = {
            'item': item,
            'claim_count': item.claims.count(),
        }
        return render(request, 'manage_delete_post.html', context)

    name = item.item_name
    item.delete()

    messages.info(request, '"%s" has been removed.' % name)
    return redirect('manage_posts')


@admin_required
def category_list(request):
    """List the categories and add a new one.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :return: the rendered list, and the same list after adding.
    :rtype: HttpResponse.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Please write the name of the category.')
        elif Category.objects.filter(name__iexact=name).exists():
            messages.error(request, 'There is already a category called that.')
        else:
            Category.objects.create(name=name)
            messages.info(request, '"%s" has been added.' % name)

        return redirect('manage_categories')

    # The count tells the Admin which categories are safe to remove.
    categories = Category.objects.annotate(item_count=Count('items'))

    return render(request, 'manage_categories.html', {
        'categories': categories,
    })


@admin_required
def rename_category(request, pk):
    """Give one category a new name.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :param pk: the id of the category being renamed.
    :type pk: int.
    :return: a redirect back to the list of categories.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return redirect('manage_categories')

    category = get_object_or_404(Category, pk=pk)
    name = request.POST.get('name', '').strip()

    if not name:
        messages.error(request, 'Please write the name of the category.')
    elif Category.objects.filter(name__iexact=name).exclude(pk=pk).exists():
        messages.error(request, 'There is already a category called that.')
    else:
        category.name = name
        category.save()
        messages.info(request, 'The category is now called "%s".' % name)

    return redirect('manage_categories')


@admin_required
def delete_category(request, pk):
    """Remove one category, unless posts are still using it.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :param pk: the id of the category being removed.
    :type pk: int.
    :return: a redirect back to the list of categories.
    :rtype: HttpResponse.
    """
    if request.method != 'POST':
        return redirect('manage_categories')

    category = get_object_or_404(Category, pk=pk)

    try:
        category.delete()
    except ProtectedError:
        # The Category foreign key of Item is PROTECT, so the database
        # itself refuses to leave a post without a category.
        messages.error(
            request,
            'Posts are still using "%s", so it cannot be removed. Move '
            'those posts to another category first.' % category.name,
        )
    else:
        messages.info(request, '"%s" has been removed.' % category.name)

    return redirect('manage_categories')


@admin_required
def export_report(request):
    """Hand the activity report over as a CSV file.

    One line per post, with the number of claims made on it, which is
    the report the SRS asks the Admin to be able to take away.

    :param request: the HTTP request sent by the Admin.
    :type request: HttpRequest.
    :return: the CSV file as a download.
    :rtype: HttpResponse.
    """
    response = HttpResponse(content_type='text/csv')
    # This header is what makes the browser save the file instead of
    # printing it on the screen.
    response['Content-Disposition'] = (
        'attachment; filename="lost-and-found-report-%s.csv"'
        % timezone.localdate().isoformat()
    )

    writer = csv.writer(response)
    writer.writerow([
        'Id', 'Type', 'Item', 'Category', 'Status', 'Place', 'Date',
        'Posted by', 'Posted on', 'Claims',
    ])

    items = Item.objects.select_related('category', 'posted_by').annotate(
        claim_count=Count('claims'),
    )

    for item in items:
        writer.writerow([
            item.pk,
            item.get_item_type_display(),
            item.item_name,
            item.category.name,
            item.get_status_display(),
            item.location,
            item.date.isoformat(),
            item.posted_by.first_name or item.posted_by.username,
            item.created_at.date().isoformat(),
            item.claim_count,
        ])

    return response
