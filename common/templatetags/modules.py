# -*- coding: utf-8 -*-
from django.template import Library
from django.conf import settings

register = Library()


@register.simple_tag
def hint_show(tag):
    if not settings.HINTS.has_key(tag): return ''
    title = settings.HINTS[tag].get('title') or 'HOW TO PLAY'

    body = """<div class="menu"><span style="float: right"><a href="#">close</a></span><h3>%s</h3><ul>""" % title
    if isinstance(settings.HINTS[tag].get('content'), list):
        for b in settings.HINTS[tag]['content']:
            body += """<li>%s<div class="descrip">%s</div></li>""" % (b[0], b[1])
    body += """</ul></div>"""
    return body
