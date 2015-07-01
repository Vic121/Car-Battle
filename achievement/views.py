# -*- coding: utf-8 -*-
from annoying.decorators import render_to
# from django.core.urlresolvers import reverse
from django.http import Http404

from achievement.models import Achievement


@render_to('achievement/index.html')
def list(request):
    items = {}
    for item in Achievement.objects.get_all():
        if not items.has_key(item.type): items[item.type] = []
        items[item.type].append(item)

    return {
        'achievements': items,
    }


@render_to('achievement/details.html')
def details(request, type):
    t, k = type.split(',')
    a = Achievement.objects.get_details(t, k)
    if len(a) == 0:
        return Http404

    return {
        'achievements': a,
        'achievement_desc': request.engine.achieve.achievement_desc[type],
        't': t,
        'k': k,
    }
