# -*- coding: utf-8 -*-
from django.template import Library

register = Library()


@register.simple_tag
def find_achievement(engine, type, name, value, field=None):
    if not engine.achieve.achievements.has_key(type):
        return None

    for item in engine.achieve.achievements[type]:
        if item.name.lower() == name and (str(item.level) == str(value.get('level')) or item.level == 0):
            if field is None:
                return item
            if field == 'img':
                return item.__dict__.get('img') or 'images/achievements/%s.png' % str(item.level)
            return item.__dict__[field]
    return None


@register.inclusion_tag('partials/home/achievement_item.html')
def render_achievement(engine, key, name, value):
    item = find_achievement(engine, key, name, value)
    item.type = key

    return {
        'item': item,
        'item_desc': engine.achieve.achievement_desc[key],
        'current_value': value['value'],
    }


@register.inclusion_tag('partials/home/achievement_item_done.html')
def render_done_achievement(engine, key, name, value):
    item = find_achievement(engine, key, name, value)
    item.type = key

    return {
        'item': item,
        'item_desc': engine.achieve.achievement_desc[key],
    }
