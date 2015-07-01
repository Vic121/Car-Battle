# -*- coding: utf-8 -*-
# import simplejson as json
from django.core.urlresolvers import reverse

from common.helpers.slughifi import slughifi
from common.models import Car
from album.models import Album as AlbumModel, UserAlbum


class Album(object):
    def __init__(self, engine):
        self.engine = engine
        self.item = None
        self._list = None

    def get_list(self):
        if self._list is None:
            self._list = UserAlbum.objects.get_by_user(user=self.engine.user.user)
        return self._list

    def set_list(self, user):
        self._list = UserAlbum.objects.get_by_user(user=user)

    list = property(get_list, set_list)

    def set_item(self, item_id):
        self.item = UserAlbum.objects.get_by_id(item_id)

        if self.item.user != self.engine.user.user:
            self.item = None
            return

        self.engine.user.get_garage()
        in_garage = self.engine.user.garage.car_ids
        cars = []
        for car in self.item.album.cars:
            if str(car) in self.item.cars:
                st = 1
            elif str(car) in in_garage:
                st = 0
            else:
                st = -1

            cars.append([Car.objects.get_by_id(car), st])

        self.item.elements = cars

    def stick_item(self, item_id):
        if self.item.stick_card(item_id):
            self.engine.user.get_garage().remove_car(item_id)
            self.engine.user.profile.cars = len(self.engine.user.garage)
            self.engine.user.profile.save()

            car = Car.objects.get_by_id(item_id)
            self.engine.notify.add(user=self.engine.user.user, type='album', key='stick', date='today')
            self.engine.notify.add(user=self.engine.user.user, type='album', key='stick', date=None,
                                   stream='%s|%s|%s|%s' % (
                                       reverse('encyclopedia_car',
                                               args=[slughifi(car.manuf), slughifi(car.name), str(car.id)]),
                                       car.display_short_name(),
                                       reverse('encyclopedia_album',
                                               args=[slughifi(self.item.album.name), self.item.id]),
                                       self.item.album.name
                                   ))

        if self.item.left == 0:
            prev_exp, prev_lvl = self.engine.user.profile.exp, self.engine.user.profile.level
            self.engine.user.profile.earn('exp', self.item.album.exp, engine=self.engine)
            self.engine.user.refresh_profile()

            self.engine.notify.add(user=self.engine.user.user, type='album', key='completed', date='today')
            self.engine.notify.add(user=self.engine.user.user, type='album', key='completed', date=None,
                                   stream='%s|%s' % (
                                       reverse('encyclopedia_album',
                                               args=[slughifi(self.item.album.name), self.item.id]),
                                       str(self.item.album.name)
                                   ))
            self.engine.log.message(message="<p>EXP +%d</p>" % self.item.album.exp)

    def group(self, items):
        group = {'Empty': [], 'Full': [], 'Incomplete': []}
        for item in items:
            if item.left == 0:
                group['Full'].append(item)
            elif item.left == item.total:
                group['Empty'].append(item)
            else:
                group['Incomplete'].append(item)

        if hasattr(self.engine, 'user'):
            group['Buy more'] = AlbumModel.objects.filter(min_lvl__lte=self.engine.user.profile.level, is_locked=True,
                                                          is_active=True).exclude(
                id__in=[x.album_id for x in items]).order_by('name')
        else:
            group['Buy more'] = ()
        return group

    def buy(self, album_id):
        album = AlbumModel.objects.get_by_id(album_id)
        if not album: return

        if album.min_lvl > self.engine.user.profile.level:
            self.engine.log.message(message="Your're not experienced enough!")
            return

        if album.price > self.engine.user.profile.cash:
            self.engine.log.message(message="Not enough cash!")
            return

        if album.id in [x.album.id for x in self.list]:
            self.engine.log.message(message="You already have this album!")
            return

        ua = UserAlbum()
        ua.user = self.engine.user.user
        ua.album = album
        ua.left = len(album.cars)
        ua.total = ua.left
        ua.save()

        self.engine.user.profile.spend('cash', album.price)
        self.engine.user.refresh_profile()
        self.engine.notify.add(user=self.engine.user.user, type='album', key='buy', date='today')
        self.engine.notify.add(user=self.engine.user.user, type='album', key='buy', date=None, stream='%s|%s' % (
            reverse('encyclopedia_album', args=[slughifi(album.name), album.id]),
            str(album.name)
        ))

        if album.price == 0:
            self.engine.log.message(message="Got %s" % album.name)
        else:
            self.engine.log.message(message="Bought %s for $%d" % (album.name, album.price))
