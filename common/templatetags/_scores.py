# -*- coding: utf-8 -*-
import datetime
from time import strptime
# import simplejson as json
# from django.core.cache import cache
from django.template import Library
from match.models import League, Team, Match

register = Library()


@register.filter
def EALIER_THAN(value, arg):
    try:
        if arg == 'NOW': arg = str(datetime.date.today())
        r = datetime.datetime(*strptime(value, "%Y-%m-%d")[0:5]) - datetime.datetime(*strptime(arg, "%Y-%m-%d")[0:5])
    except TypeError:
        return False
    if ((r.days * 3600) + r.seconds) > 0:
        return True
    else:
        return False


@register.filter
def LATER_THAN(value, arg):
    try:
        if arg == 'NOW': arg = str(datetime.date.today())
        r = datetime.datetime(*strptime(value, "%Y-%m-%d")[0:5]) - datetime.datetime(*strptime(arg, "%Y-%m-%d")[0:5])
    except TypeError:
        return False
    if ((r.days * 3600) + r.seconds) < 0:
        return True
    else:
        return False


@register.filter
def EQUALS_TODAY(value):
    try:
        r = datetime.datetime(*strptime(value, "%Y-%m-%d")[0:5]) - datetime.datetime(
            *strptime(str(datetime.date.today()), "%Y-%m-%d")[0:5])
    except TypeError:
        return True
    if r.days == 0:
        return True
    else:
        return False


@register.inclusion_tag('partials/user_box.html')
def user_box(request):
    return {'request': request}


@register.filter
def get_league(id):
    if id == 0: return League()
    return League.objects.get_by_id(id)


@register.filter
def get_team(id):
    if id == 0: return Team()
    return Team.objects.get_by_id(id)


@register.filter
def get_match(id):
    if id == 0: return Match()
    return Match.objects.get_by_id(id)


@register.filter
def match_time(time):
    if time == -1:
        return 'Extra Time'
    elif time == -2:
        return '2nd Half'
    elif time == -3:
        return 'Half Time'
    elif time == -4:
        return '1st Half'
    else:
        return '%d\'\'' % time


LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 10
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 8
NUM_PAGES_OUTSIDE_RANGE = 2
ADJACENT_PAGES = 4
PER_PAGE = 20


def digg_paginator(context):
    if context["pages"] > 1:
        context["is_paginated"] = True
    else:
        context["is_paginated"] = False

    if context["is_paginated"]:

        path = context['request'].META['PATH_INFO']
        if path.find('strona-') > -1:
            base_url = path[0:path.find('strona-')]
        elif path.find('page-') > -1:
            base_url = path[0:path.find('page-')]
        else:
            base_url = path

        " Initialize variables "
        in_leading_range = in_trailing_range = False
        pages_outside_leading_range = pages_outside_trailing_range = range(0)

        if (context["pages"] <= LEADING_PAGE_RANGE_DISPLAYED):
            in_leading_range = in_trailing_range = True
            page_numbers = [n for n in range(1, context["pages"] + 1) if n > 0 and n <= context["pages"]]

        elif (context["page_no"] <= LEADING_PAGE_RANGE):
            in_leading_range = True
            page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= context["pages"]]
            pages_outside_leading_range = [n + context["pages"] for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        elif (context["page_no"] > context["pages"] - TRAILING_PAGE_RANGE):
            in_trailing_range = True
            page_numbers = [n for n in range(context["pages"] - TRAILING_PAGE_RANGE_DISPLAYED + 1, context["pages"] + 1)
                            if n > 0 and n <= context["pages"]]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        else:
            page_numbers = [n for n in
                            range(context["page_no"] - ADJACENT_PAGES, context["page_no"] + ADJACENT_PAGES + 1) if
                            n > 0 and n <= context["pages"]]
            pages_outside_leading_range = [n + context["pages"] for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]

        if context["pages"] == 1:
            has_previous, previous = False, False
            has_next = True
            next = context["page_no"] + 1
        elif context["page_no"] > 1 and context["page_no"] < context["pages"]:
            has_previous = True
            previous = context["page_no"] - 1
            has_next = True
            next = context["page_no"] + 1
        elif context["pages"] == context["page_no"]:
            has_next, next = False, False
            has_previous = True
            previous = context["page_no"] - 1
        else:
            has_next = True
            next = context["page_no"] + 1
            has_previous, previous = False, False

        return {
            "base_url": base_url,
            "is_paginated": context["is_paginated"],
            "previous": previous,
            "has_previous": has_previous,
            "next": next,
            "has_next": has_next,
            "results_per_page": PER_PAGE,
            "page": context["page_no"],
            "pages": context["pages"],
            "page_numbers": page_numbers,
            "in_leading_range": in_leading_range,
            "in_trailing_range": in_trailing_range,
            "pages_outside_leading_range": pages_outside_leading_range,
            "pages_outside_trailing_range": pages_outside_trailing_range
        }


register.inclusion_tag("partials/paginator.html", takes_context=True)(digg_paginator)
