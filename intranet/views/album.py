# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from common.helpers.core import reverse


# import urllib, urlparse, os, shutil
# from PIL import Image
from decimal import Decimal
from common.models import Car
# from album.models import Album, UserAlbum

@staff_member_required
def index(request):
    if request.method == 'POST':
        item = Album()
        item.name = request.POST['name']
        item.short_name = request.POST['short_name']
        item.save()
        request.engine.redirect(reverse('intranet_albums'))

    items = Album.objects.all().order_by('-is_locked', '-is_active', 'min_lvl', 'price', 'name')

    return render_to_response(
        'intranet/album_index.html', {
            'get': request.GET,
            'items': items,
        }, context_instance=RequestContext(request)
    )


@staff_member_required
def details(request, item_id):
    item = Album.objects.get(pk=item_id)
    item.elements = Car.objects.get_list(item.cars)

    if request.method == 'POST':
        action = request.POST['action']
        car = Car.objects.get(pk=int(request.POST['id']))

        if action == 'add_car':
            item.add_car(car.id)
            car.chance = car.chance + Decimal('0.1')
            car.save()
            return HttpResponse('car added!')

        if action == 'remove_car':
            item.remove_car(car.id)
            car.chance = car.chance - Decimal('0.1')
            car.save()
            return HttpResponse('car removed!')

        if action == 'reorder':
            reordered = []
            for x in request.POST['value'].split('&'):
                x = x.replace('album_items[]=', '').replace('car_', '')
                if len(x) == 0: continue
                reordered.append(str(x))

            item.car = ','.join(reordered)
            item.save()

            return HttpResponse('order changed!')

    gta = None
    manufs = None
    if request.GET.has_key('search'):
        # gta = Car.objects.filter(is_active=True, is_active_in_battle=True)
        gta = Car.objects.filter_with_params(request.GET).exclude(id__in=item.cars)
        manufs = gta.values_list('manuf', flat=True).order_by('manuf').distinct()
        if len(request.GET['manuf']) > 0:
            gta = gta.order_by('manuf', 'model', 'year')
        else:
            gta = gta.order_by('manuf', '-year', 'model')[:100]

    return render_to_response(
        'intranet/album_details.html', {
            'get': request.GET,
            'item': item,
            'manufs': manufs or Car.objects.filter(is_active=True, is_active_in_battle=True).values_list('manuf',
                                                                                                         flat=True).order_by(
                'manuf').distinct(),
            'groups': settings.CAR_GROUPS,
            'results': gta,
        }, context_instance=RequestContext(request)
    )


@staff_member_required
def edit(request, item_id):
    item = Album.objects.get(pk=item_id)

    if request.method == 'POST':
        if request.POST.has_key('remove'):
            item.delete()
        else:
            for k, v in request.POST.iteritems():
                item.__dict__[k] = v.strip()
            if not request.POST.has_key('is_active'): item.__dict__['is_active'] = False
            if not request.POST.has_key('is_locked'): item.__dict__['is_locked'] = False
            item.save()
        return request.engine.redirect(reverse('intranet_albums'))

    return render_to_response(
        'intranet/album_edit.html', {
            'item': item,
        }, context_instance=RequestContext(request)
    )
