# -*- coding: utf-8 -*-
# import logging
from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User

import datetime
import cPickle as pickle
from common.models import Car
from userprofile.models import UserProfile


class GiftManager(models.Manager):
    def get_by_link(self, link):
        try:
            item = self.get(link=link, is_active=True)
            if item.is_amount_limited:
                if item.limit_left > 0:
                    return item
                else:
                    return False
            if item.is_time_limited:
                if item.limit_at > datetime.datetime.now():
                    return item
                else:
                    return False
        except Gift.DoesNotExist:
            return False


class Gift(models.Model):
    car = models.ForeignKey(Car)
    link = models.CharField(max_length=16, unique=True)
    sender = models.ForeignKey(User)
    use = models.TextField()

    limit_left = models.SmallIntegerField(default=0)
    limit_at = models.DateTimeField(auto_now_add=True)
    is_amount_limited = models.BooleanField(default=False)
    is_time_limited = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GiftManager()

    def __getattr__(self, name):
        if name == 'used':
            if len(self.use) == 0: return []
            return self.use.split(',')
        else:
            return self.__getattribute__(name)

    def save(self):
        h = hashlib.md5()
        h.update('%s+%s+%s' % (self.sender, settings.SECRET_KEY, datetime.datetime.now()))
        if len(self.link) == 0: self.link = h.hexdigest()[:16]
        super(Gift, self).save()

    class Meta:
        db_table = 'gift'
        verbose_name = 'Gift'

    def use_gift(self, user):
        garage = Garage.objects.get_by_user(user=user)
        garage.add_car(self.car.id)

        if self.is_amount_limited:
            self.limit_left -= 1
            if self.limit_left == 0:
                self.is_active = False

        used = self.used
        used.append(str(user.id))
        self.use = ','.join(used)
        self.save()


class UserGiftManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):
        if user is not None:
            key = 'gifts_%s' % user.id
        elif user_id is not None:
            key = 'gifts_%s' % user_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if user is not None:
                item = self.get(user=user)
            elif user_id is not None:
                item = self.get(user__id=user_id)

        except UserGift.DoesNotExist:
            item = UserGift()
            if user:
                item.user = user
            elif user_id:
                item.user = User.objects.get(pk=user_id)
            item.save()

        cache.set(key, pickle.dumps(item))
        return item

    def expand(self, dataset):
        new_data = []
        for data in dataset:
            car_id, user_id = data.split(';')
            new_data.append(
                {'car': Car.objects.get_by_id(car_id), 'sender': UserProfile.objects.get_by_user(user_id=user_id)})
        return new_data


class UserGift(models.Model):
    user = models.ForeignKey(User)
    pending = models.TextField()

    objects = UserGiftManager()

    class Meta:
        db_table = 'user_gift'
        verbose_name = 'UserGift'

    def __unicode__(self):
        return 'pending gifts of %s' % self.user

    def __getattr__(self, name):
        if name == 'pendings':
            if not self.pending: return []
            return self.pending.split(',')
        return self.__getattribute__(name)

    def save(self):
        super(UserGift, self).save()
        cache.delete('gifts_%s' % (self.user.id))

    def delete(self):
        u = int(self.user.id)
        super(UserGift, self).delete()
        cache.delete('gifts_%s' % u)

    def has_in_pending(self, car_id, user_id):
        if len(self.pending) == 0: return False
        return '%s;%s' % (car_id, user_id) in self.pendings

    def confirm(self, car_id, user_id):
        if not self.remove_pending(car_id, user_id): return False

        from job.models import Garage

        garage = Garage.objects.get_by_user(user=self.user)
        garage.add_car(car_id)

        self.engine.notify.add(user=self.user, type='gift', key='confirm_gift', date='today')
        self.engine.notify.add(user=self.user, type='gift', key='confirm_gift', date=None, stream='%s|%s' % (
            Car.objects.get_by_id(car_id), str(UserProfile.objects.get_by_id(user_id))))

        return True

    def decline(self, car_id, user_id):
        if not self.remove_pending(car_id, user_id): return False

        self.engine.notify.add(user=self.user, type='gift', key='decline_gift', date='today')
        self.engine.notify.add(user=self.user, type='gift', key='decline_gift', date=None)

        return True

    def add_pending(self, car_id, user_id):
        if self.has_in_pending(car_id, user_id): return False

        pendings = self.pendings
        pendings.append('%s;%s' % (car_id, user_id))
        self.pending = ','.join(pendings)
        self.save()

        self.engine.notify.add(user=self.user, type='gift', key='add_pending', date='today')
        self.engine.notify.add(user=self.user, type='gift', key='add_pending', date=None)

        return True

    def remove_pending(self, car_id, user_id):
        if not self.has_in_pending(car_id, user_id): return False

        pendings = self.pendings
        del pendings[pendings.index('%s;%s' % (car_id, user_id))]
        self.pending = ','.join(pendings)
        self.save()

        return True


class UserGiftLogManager(models.Manager):
    pass


class UserGiftLog(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user')
    to_user = models.ForeignKey(User, related_name='to_user')
    item_type = models.CharField(max_length=20)
    item_id = models.PositiveIntegerField()
    action = models.CharField(max_length=20)  # wishlist or sth

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserGiftLogManager()

    class Meta:
        db_table = 'user_gift_log'
        verbose_name = 'UserGiftLog'

    def __unicode__(self):
        return '%s gave type:%s id:%s to %s (%s)' % (
            self.from_user, self.item_type, self.item_id, self.friend, self.action)
