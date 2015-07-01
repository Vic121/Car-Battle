# -*- coding: utf-8 -*-
# from django.core.urlresolvers import reverse
from annoying.decorators import render_to
from msg.models import Msg


@render_to()
def list(request, type, page=0):
    if type == 'outbox':
        arr = outbox(request, page)
    else:
        request.engine.msg.mark_unread_as_read()
        arr = inbox(request, page)

    if request.GET.has_key('ajax') and request.GET['ajax'] == '1':
        arr['TEMPLATE'] = 'msg/list_ajax.html'

    return arr


def inbox(request, page):
    return {
        'TEMPLATE': 'msg/list.html',
        'msgs': request.engine.msg.get_inbox(page),
        'selected_tab': 'inbox',
    }


def outbox(request, page):
    return {
        'TEMPLATE': 'msg/list.html',
        'msgs': request.engine.msg.get_outbox(page),
        'selected_tab': 'outbox',
    }


@render_to()
def form(request):
    usernames = []
    for string in request.POST['text'].split(' '):
        if string.startswith('@'): usernames.append(string)

    if len(usernames) > 0:
        for user in set(usernames):
            Msg.send.send_to(request.engine.user.user, user[1:], request.POST['text'])

        return {
            'TEMPLATE': 'msg/send_success.html'
        }

    return {
        'TEMPLATE': 'msg/send_failure.html'
    }
