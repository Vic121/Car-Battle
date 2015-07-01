# -*- coding: utf-8 -*-
import logging

from django.http import Http404
from django.conf import settings

from annoying.decorators import render_to
from common.models import Car
from common.paginator import DiggPaginator as Paginator
from album.models import Album


@render_to('encyclopedia/index.html')
def index(request):
    return {
        'manufs': Car.objects.get_manuf_list(),
    }


@render_to('encyclopedia/car_list.html')
def car_list(request, manuf_url, page_no):
    try:
        manuf = Car.objects.get_manuf_dict()[manuf_url]
    except KeyError:
        logging.debug('Manuf %s key error' % (manuf_url))
        raise Http404

    cars = Car.objects.get_by_manuf(manuf=manuf)
    selected = cars[
               (int(page_no) - 1) * settings.DEFAULT_CARS_PER_ENCYCLOPEDIA_PAGE:int(
                   page_no) * settings.DEFAULT_CARS_PER_ENCYCLOPEDIA_PAGE
               ]
    paginator = Paginator(cars, settings.DEFAULT_CARS_PER_ENCYCLOPEDIA_PAGE, body=8, padding=2)

    try:
        current_page = paginator.page(page_no)
    except:
        logging.debug('Page %s error for %s' % (page_no, manuf))
        raise Http404

    return {
        'manuf': manuf,
        'short_manuf': manuf_url,
        'cars': selected,
        'page_no': int(page_no),
        'page': current_page,
        'total': len(cars),
    }


@render_to('encyclopedia/car_details.html')
def car_details(request, manuf_url, model_url, car_id):
    car = Car.objects.get_by_id(car_id)
    if car is None: raise Http404

    try:
        manuf = Car.objects.get_manuf_dict()[manuf_url]
    except KeyError:
        logging.debug('Manuf %s key error' % (manuf_url))
        raise Http404

    return {
        'car': car,
        'manuf': manuf,
    }


@render_to('encyclopedia/album_list.html')
def album_list(request, page_no):
    albums = Album.objects.filter(is_active=True, is_locked=True, is_hidden=False).order_by('name')
    selected = albums[
               (int(page_no) - 1) * settings.DEFAULT_CARS_PER_ENCYCLOPEDIA_PAGE:int(
                   page_no) * settings.DEFAULT_CARS_PER_ENCYCLOPEDIA_PAGE
               ]
    paginator = Paginator(albums, settings.DEFAULT_CARS_PER_ENCYCLOPEDIA_PAGE, body=8, padding=2)

    try:
        current_page = paginator.page(page_no)
    except:
        logging.debug('Page %s error for %s' % (page_no, manuf))
        raise Http404

    return {
        'albums': selected,
        'page_no': int(page_no),
        'page': current_page,
        'total': len(albums),
    }


@render_to('encyclopedia/album_details.html')
def album_details(request, album_url, album_id):
    album = Album.objects.get_by_id(album_id)
    if album is None:
        raise Http404

    return {
        'album': album,
        'cars': Car.objects.get_list(album.cars),
    }


@render_to('encyclopedia/achievement_list.html')
def achievement_list(request):
    return {
        'achievements': request.engine.achieve.achievements,
    }


@render_to('encyclopedia/achievement_details.html')
def achievement_details(request, achievement_url, achievement_id):
    return {
        'achievements': request.engine.achieve.achievements,
    }
