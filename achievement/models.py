# import logging
import random

import simplejson as json
from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

import datetime
from common.models import Car


class AchievementManager(models.Manager):
    def get_all(self, type=None, key=None):
        items = self.filter(is_hidden=False)
        if type is not None:
            items = items.filter(type=type)
        if key is not None:
            items = items.filter(key=key)
        return items.order_by('type', 'key', 'level', 'exp')

    def get_details(self, t, k):
        return self.filter(type=t[:15], key=k[:15], is_hidden=False).order_by('level', 'exp')


class Achievement(models.Model):
    type = models.CharField(max_length=15)
    key = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    level = models.PositiveSmallIntegerField(default=0)
    start_value = models.PositiveIntegerField()
    value = models.PositiveIntegerField()
    value_in = models.CharField(max_length=255)
    img = models.CharField(max_length=255)
    exp = models.PositiveIntegerField(default=0)
    cash = models.PositiveIntegerField(default=0)
    credit = models.PositiveIntegerField(default=0)
    car_id = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    is_income_hidden = models.BooleanField(default=False)
    is_day_wise = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AchievementManager()

    class Meta:
        db_table = 'achievement'
        verbose_name = 'Achievement'

    def get_car(self):
        if self.car_id > 0:
            if not hasattr(self, 'car'):
                self.car = Car.objects.get_by_id(self.car_id)
            return self.car

    def type_key(self):
        return '%s,%s' % (self.type, self.key)


class UserAchievementManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):
        try:
            return self.get(user=user)
        except UserAchievement.DoesNotExist:
            ua = UserAchievement()
            ua.user = user
            ua.save()
            return ua


class UserAchievement(models.Model):
    user = models.ForeignKey(User)
    pending = models.TextField()
    done = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserAchievementManager()

    class Meta:
        db_table = 'user_achievement'
        verbose_name = 'User Achievement'

    def save(self):
        super(UserAchievement, self).save()  # Call the "real" save() method
        cache.delete('user_achievement_%s' % self.user.id)

    def __unicode__(self):
        return 'Achievements of %s' % str(self.user)

    def __getattr__(self, name):
        if name == 'pendings':
            if self.pending == '':
                return {}
            return json.loads(self.pending)
        elif name == 'dones':
            if self.done == '':
                return {}
            return json.loads(self.done)
        elif name == 'random_pendings':
            if self.pending == '':
                return {}
            pendings = json.loads(self.pending)
            keys = pendings.keys()

            if sum([len(pendings[k]) for k in keys]) <= 5:
                return pendings

            data = {}
            while len(data.keys()) < settings.ACHIEVEMENTS_ON_DASH:
                key = random.choice(keys)
                if len(pendings[key]) == 0: continue

                key2 = random.choice(pendings[key].keys())
                if len(pendings[key][key2]) == 0: continue
                if not data.has_key(key2):
                    data[key] = {}
                data[key][key2] = pendings[key][key2]
            return data

        else:
            return self.__getattribute__(name)

    def add(self, key, item):
        name = item.name.lower()
        key = key.lower()

        dones = self.dones
        if not dones.has_key(key): dones[key] = {}
        dones[key][name] = {'date': str(datetime.datetime.now()), 'level': item.level}
        if item.level == 0:
            del dones[key][name]['level']
        self.done = json.dumps(dones)

        pendings = self.pendings
        try:
            del pendings[key]
            self.pending = json.dumps(pendings)
        except KeyError:
            pass

        self.save()

        if hasattr(self, 'engine'):

            if item.level == 0:
                stream = item.name
            else:
                stream = '%s (%s)' % (item.name, item.level)

            self.engine.notify.add(user=self.user, type='achievement', key='done', date='today')
            self.engine.notify.add(user=self.user, type='achievement', key='done', date=None, stream=stream)

        return True

    def add_pending(self, key, item, value=0):
        name = item.name.lower()
        key = key.lower()

        pendings = self.pendings
        if not pendings.has_key(key):
            pendings[key] = {}
        pendings[key][name] = {'value': value, 'level': item.level}
        if item.level == 0:
            del pendings[key][name]['level']
        self.pending = json.dumps(pendings)
        self.save()

        return True
