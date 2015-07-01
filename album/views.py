# -*- coding: utf-8 -*-
import logging

from django.http import Http404

from annoying.decorators import render_to
from common.helpers.core import reverse


@render_to('album/index.fbml')
def index(request):
    request.engine.register('album')
    request.engine.module = 'album'

    albums = request.engine.album.group(request.engine.album.list)

    order = ('Empty', 'Incomplete', 'Full')
    active_tab = 'Buy more'
    for i in order:
        if len(albums[i]) > 0:
            active_tab = i
            break

    return {
        'items': albums,
        'active_tab': active_tab,
    }


@render_to('album/details.fbml')
def details(request, album_id):
    request.engine.register('album')
    request.engine.module = 'album'
    request.engine.album.set_item(album_id)

    if request.engine.album.item is None:
        raise Http404

    return {
        'item': request.engine.album.item,
        'cars': request.engine.album.item.elements,
    }


def stick(request, album_id, car_id):
    request.engine.register('album')
    request.engine.album.set_item(album_id)
    request.engine.album.stick_item(car_id)

    logging.info('car (%d) sticked to %d by %s' % (int(car_id), int(album_id), request.engine.user.user))
    return request.engine.redirect(reverse('album', args=[album_id]))


def buy(request, album_id):
    request.engine.register('album')
    request.engine.album.buy(album_id)

    logging.info('album (%s) bought by %s' % (album_id, request.engine.user.user))
    return request.engine.redirect(reverse('albums'))
