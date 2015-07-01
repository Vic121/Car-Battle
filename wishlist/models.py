# import logging
from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User

import cPickle as pickle
from common.helpers.slughifi import slughifi
from common.models import Car


class WishListManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):

        if user is not None:
            key = 'wishlist_%s' % user.id
        elif user_id is not None:
            key = 'wishlist_%s' % user_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            # if user is not None:
            item = self.get(user=user)
        # elif user_id is not None:
        # item = self.get(user__id=user_id)

        except WishList.DoesNotExist:
            item = WishList()
            if user:
                item.user = user
            elif user_id:
                item.user = User.objects.get(pk=user_id)
            item.save()

        cache.set(key, pickle.dumps(item))
        return item


class WishList(models.Model):
    user = models.ForeignKey(User)
    item = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WishListManager()

    class Meta:
        db_table = 'user_wishlist'
        verbose_name = 'WishList'

    def __getattr__(self, name):
        if name == 'items':
            if not self.item: return []
            return self.item.split(',')
        return self.__getattribute__(name)

    def __len__(self):
        return len(self.items)

    def __unicode__(self):
        return 'Wish List of %s' % self.user

    def save(self):
        super(WishList, self).save()
        cache.delete('wishlist_%s' % (self.user.id))

    def delete(self):
        u = int(self.user.id)
        super(WishList, self).delete()
        cache.delete('wishlist_%s' % u)

    def has_item(self, iid):
        if len(self.item) == 0: return False
        return iid in self.items

    def add_item(self, iid):
        if self.has_item(str(iid)): return False
        if len(self) >= settings.MAX_WISHLIST_SIZE: return False

        items = self.items
        items.append(str(iid))
        self.item = ','.join(items)
        self.save()

        car = Car.objects.get_by_id(iid)
        self.engine.notify.add(user=self.user, type='wishlist', key='add_item', date='today')
        self.engine.notify.add(user=self.user, type='wishlist', key='add_item', date=None, stream='%s|%s' % (
            reverse('encyclopedia_car', args=[slughifi(car.manuf), slughifi(car.name), str(car.id)]),
            car.display_short_name()))

        return True

    def remove_item(self, iid):
        if not self.has_item(str(iid)): return False

        items = self.items
        del items[items.index(str(iid))]
        self.item = ','.join(items)
        self.save()

        car = Car.objects.get_by_id(iid)
        self.engine.notify.add(user=self.user, type='wishlist', key='remove_item', date='today')
        self.engine.notify.add(user=self.user, type='wishlist', key='remove_item', date=None, stream='%s|%s' % (
            reverse('encyclopedia_car', args=[slughifi(car.manuf), slughifi(car.name), str(car.id)]),
            car.display_short_name()))

        return True
