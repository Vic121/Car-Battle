# -*- coding: utf-8 -*-
import simplejson as json
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.conf import settings

import datetime
from common.helpers.core import reverse


# import urllib, urlparse, os, shutil
# from PIL import Image
from common.models import Car
from battle.models import Battle
from auction.models import Auction
# from album.models import Album, UserAlbum
from job.models import Garage
from wishlist.models import WishList


@staff_member_required
def index(request):
    def query(query):
        cursor = connection.cursor()
        c = cursor.execute(query)
        return cursor.fetchall()

    def __replace_id(f_id, t_id, s):
        arr = s.split(',')
        f_id, t_id = str(f_id), str(t_id)

        if f_id not in arr: return s

        arr[arr.index(f_id)] = t_id
        return ','.join(arr)

    if request.method == 'POST':
        if not request.POST.has_key('left'): return HttpResponseRedirect(reverse('auction_merge'))

        to_car_id = str(request.POST['left'])
        to_car = Car.objects.get(pk=int(request.POST['left']))
        for k, car_id in request.POST.iteritems():
            if not k.startswith('right_'): continue

            from_car_id = str(car_id)
            from_car = Car.objects.get(pk=int(car_id))

            # replace all car_ids
            for album in Album.objects.all():
                album.car = __replace_id(from_car_id, to_car_id, album.car)
                album.save()

            for album in UserAlbum.objects.all():
                album.car = __replace_id(from_car_id, to_car_id, album.car)
                album.save()

            for auction in Auction.objects.filter(car=from_car):
                auction.car = to_car
                auction.name = to_car.name
                auction.tier = to_car.tier
                auction.save()

            for battle in Battle.objects.all():
                battle.left_card = __replace_id(from_car_id, to_car_id, battle.left_card)
                battle.right_card = __replace_id(from_car_id, to_car_id, battle.right_card)
                if len(battle.state) > 0:
                    state = json.loads(battle.state)
                    if from_car_id not in state.keys(): continue
                    state[to_car_id] = state[from_car_id]
                    del state[from_car_id]
                    battle.state = json.dumps(state)
                battle.save()

            for garage in Garage.objects.all():
                if len(garage.car) == 0: continue

                items = json.loads(garage.car)
                if from_car_id not in items.keys(): continue
                items[to_car_id] = items[from_car_id]
                del items[from_car_id]
                garage.car = json.dumps(items)
                garage.save()

            for wishlist in WishList.objects.all():
                wishlist.item = __replace_id(from_car_id, to_car_id, wishlist.item)
                wishlist.save()

            from_car.in_battle = False
            from_car.is_active_in_battle = False
            from_car.save()
            query("UPDATE common.car SET in_battle=0, is_active_in_battle=0 WHERE id=%d" % int(from_car.id))

            query("INSERT INTO stat.merge_log(from_car_id, to_car_id, created_at) VALUES('%s', '%s', '%s')" % (
                car_id, request.POST['left'], str(datetime.datetime.now())[:19]))

        if request.META.has_key('HTTP_REFERER'):
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            return HttpResponseRedirect(reverse('intranet_merge'))

    gta = None
    manufs = None
    if request.GET.has_key('search'):
        gta = Car.objects.filter_with_params(request.GET).filter(is_active=True, is_active_in_battle=True,
                                                                 in_battle=True)
        manufs = gta.values_list('manuf', flat=True).order_by('manuf').distinct()
    else:
        gta = Car.objects.filter(is_active=True, is_active_in_battle=True, in_battle=True)

    if request.GET.has_key('manuf') and len(request.GET['manuf']) > 0:
        gta = gta.order_by('manuf', 'name', 'year')
    else:
        gta = gta.order_by('manuf', '-year', 'name')[:100]

    return render_to_response(
        'intranet/merge.html', {
            'get': request.GET,
            # 'item': item,
            'manufs': manufs or Car.objects.filter(is_active=True, is_active_in_battle=True,
                                                   in_battle=True).values_list('manuf', flat=True).order_by(
                'manuf').distinct(),
            'groups': settings.CAR_GROUPS,
            'results': gta,
        }, context_instance=RequestContext(request)
    )
