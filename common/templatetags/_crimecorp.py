# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.template import Library
from django.conf import settings

from common.helpers.core import reverse
from crimecorp.common.helpers._crimecorp import get_chance

register = Library()


@register.filter
def CHANCE(job_obj, user_obj):
    return get_chance(user_obj.total_attack, \
                      user_obj.total_respect, \
                      job_obj.req_attack, \
                      job_obj.req_respect, \
                      0, \
                      user_obj.heat, \
                      user_obj.max_heat, \
                      job_obj.heat)


@register.filter
def CHANCE_TRIBUTE(job_obj, user_obj):
    return get_chance(user_obj.team_attack, \
                      user_obj.team_respect, \
                      job_obj.req_attack, \
                      job_obj.req_respect, \
                      0, \
                      user_obj.heat, \
                      user_obj.max_heat, \
                      job_obj.heat)


@register.inclusion_tag('render.html')
def moving_units_list(engine):
    from crimecorp.city.models import City, MapMove

    current_queue = MapMove.objects.get_by_user(user=engine.user.user).units

    current_cities = {}
    if len(current_queue) > 0:
        for cu in current_queue:
            current_cities[int(cu[0])] = None
            current_cities[int(cu[1])] = None

        cm = City.objects.get_names_list(current_cities.keys())
        for cc in current_cities.keys():
            current_cities[int(cc)] = cm[long(cc)].name

    return {
        'render': render_to_string('modules/moving_units_list.html', {
            'engine': engine,
            'current_queue': current_queue,
            'current_cities': current_cities,
        })
    }


@register.inclusion_tag('render.html')
def other_cities(engine):
    return {
        'render': render_to_string('modules/other_cities.html', {
            'engine': engine,
            'cities': engine.city.get_other_cities(),
        })
    }


@register.simple_tag
def robbery_tabs(page, tab, lang='en'):
    ret = ''

    if page > 0:
        ret += '<li><a href="%s"">&laquo;</a></li>' % reverse('robbery', args=[page - 1])

    i = 0
    for tabs in settings.ROBBERY_TABS[page]:
        ret += '<li><a href="%s">' % reverse('robbery', args=[page, i])

        if int(tab) == i:
            ret += '<b>%s</b>' % tabs
        else:
            ret += '%s' % tabs
        ret += '</a></li>'
        i += 1

    if len(settings.ROBBERY_TABS) > page + 1:
        ret += '<li><a href="%s"">&raquo;</a></li>' % reverse('robbery', args=[page + 1])

    return ret


@register.simple_tag
def job_loot_items(loot, lang):
    from item.models import Item

    ret = ''

    for item_id, chance in loot.iteritems():
        item = Item.objects.get_by_id(item_id)
        if settings.ALL_ITEM.has_key(int(item.id)):
            try:
                item.name = unicode(settings.ALL_ITEM[int(item.id)][lang])
            except KeyError:
                item.name = unicode(settings.ALL_ITEM[int(item.id)]['en'])

        # ret += '<li>%d%s <a href="%s%s" class="preview">%s</a></li>' % (chance, '%', settings.MEDIA_URL, item.image_filename, item_name)
        ret += '<li>%s (%d%s)</li>' % (item.name, chance, '%')

    return ret
