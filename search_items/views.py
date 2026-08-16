"""Views of the search_items app.

Feature 5 of the SRS lives here: anybody can search every lost and
found post by a keyword and then narrow the list down by category,
place and a date range, and open one post to read the whole report.
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from core.models import ITEM_TYPE_CHOICES, Category, Item


def read_date(text):
    """Turn the text of a date box into a real date.

    A search link can be typed by hand, so a value that is not a date
    has to come back as nothing and simply be ignored by the filter
    instead of crashing the page.

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


def item_list(request):
    """Show the posts that match the keyword and the chosen filters.

    Every filter is optional and they all narrow the same queryset one
    after another, which is how the SRS asks for search and filter to
    work together at the same time. Nothing touches the database until
    the template walks over the list, so an unused filter costs
    nothing.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :return: the rendered list of matching posts.
    :rtype: HttpResponse.
    """
    # select_related fetches the category and the poster in the same
    # query, so a page of fifty posts is still one trip to the database
    # instead of a hundred and one.
    items = Item.objects.select_related('category', 'posted_by')

    query = request.GET.get('query', '').strip()
    if query:
        # Q objects joined with | mean "any one of these three", so one
        # word is enough to find a post by its name, by its category or
        # by a word from the description.
        items = items.filter(
            Q(item_name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    category_id = request.GET.get('category', '')
    # A category is chosen from a dropdown, so anything that is not a
    # number came from a hand written link and is ignored.
    if category_id.isdigit():
        items = items.filter(category_id=category_id)

    item_type = request.GET.get('type', '')
    if item_type in dict(ITEM_TYPE_CHOICES):
        items = items.filter(item_type=item_type)

    location = request.GET.get('location', '').strip()
    if location:
        items = items.filter(location__icontains=location)

    date_from = read_date(request.GET.get('date_from', ''))
    if date_from is not None:
        items = items.filter(date__gte=date_from)

    date_to = read_date(request.GET.get('date_to', ''))
    if date_to is not None:
        items = items.filter(date__lte=date_to)

    # The boxes are filled again from these values, so the visitor can
    # see what is switched on and change one thing without typing the
    # rest a second time.
    filters = {
        'query': query,
        'category': category_id,
        'type': item_type,
        'location': location,
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
    }

    context = {
        'items': items,
        'categories': Category.objects.all(),
        'item_types': ITEM_TYPE_CHOICES,
        'filters': filters,
        # The template shows "Clear all filters" only when there is
        # something to clear.
        'is_filtered': any(filters.values()),
    }
    return render(request, 'item_list.html', context)


def item_detail(request, pk):
    """Show one post with its photo, its status and its whole report.

    :param request: the HTTP request sent by the visitor.
    :type request: HttpRequest.
    :param pk: the id of the post in the Item table.
    :type pk: int.
    :return: the rendered detail page, or a 404 page when there is no
        post with that id.
    :rtype: HttpResponse.
    """
    item = get_object_or_404(
        Item.objects.select_related('category', 'posted_by'),
        pk=pk,
    )
    return render(request, 'item_detail.html', {'item': item})
