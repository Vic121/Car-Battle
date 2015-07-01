# -*- coding: UTF-8
# import logging
import hashlib

import simplejson as json
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache

import cPickle as pickle
import datetime
from userprofile.models import UserProfile
from common.helpers.slughifi import slughifi
from common.models import Car


class UserJobManager(models.Manager):
    def get_by_user(self, user=None, user_id=None, profile=None):
        if user is not None:
            key = 'user_job_%s' % user.id
        elif user_id is not None:
            key = 'user_job_%s' % user_id

        # item = cache.get(key)
        # if item is not None:
        # 	item = pickle.loads(str(item))
        # 	return item

        try:
            if user is not None:
                item = self.get(user=user, is_active=True)
            elif user_id is not None:
                item = self.get(user__id=user_id, is_active=True)

        except UserJob.DoesNotExist:
            if profile.job_round > profile.job_max_round_today and profile.job_next_day_at > datetime.datetime.now():
                return None

            item = UserJob()
            if user is not None:
                item.user = user
            elif user_id is not None:
                item.user = User.objects.get(pk=user_id)

            jobs = Car.objects.draw_cars(profile or UserProfile.objects.get_by_id(user_id=item.user.id),
                                         all_tiers=False)
            jobs = [jobs['1'], jobs['2'], jobs['3'], jobs['4'], jobs['5']]  # , jobs['6']]

            h = hashlib.md5()
            h.update('%s+%s+%s' % (item.user, settings.SECRET_KEY, datetime.datetime.now()))

            item.last_tier = profile.job_tier
            item.job = ','.join([str(c.id) for c in jobs])
            item.help_need = sum(settings.JOB_HELPERS_NEEDED)
            item.help_has = 0
            item.link = h.hexdigest()[:16]
            item.is_active = True
            item.save()

            profile.job_id = item.id
            profile.save()

            for job in jobs:
                job_stat = JobStat.objects.get_by_job(job=job)
                job_stat.started += 1
                job_stat.last_started = profile.user
                job_stat.last_started_at = datetime.datetime.now()
                job_stat.save()

        item.jobs = item.jobs  # put it also to cache
        cache.set(key, pickle.dumps(item))
        return item


class UserJob(models.Model):
    user = models.ForeignKey(User)
    job = models.CharField(max_length=255)
    helper = models.CharField(max_length=100)

    round = models.PositiveSmallIntegerField(default=1)
    last_tier = models.PositiveSmallIntegerField(default=1)
    help_need = models.PositiveSmallIntegerField(default=0)
    help_has = models.PositiveSmallIntegerField(default=0)

    link = models.CharField(max_length=16)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserJobManager()

    class Meta:
        db_table = 'user_job'
        verbose_name = 'User\'s job'

    def __unicode__(self):
        return "%s's jobs" % (self.user)

    def __getattr__(self, name):
        if name == 'jobs':
            return Car.objects.get_list(self.job.split(','))
        elif name == 'helpers':
            if len(self.helper) == 0: return []
            return self.helper.split(',')
        else:
            return self.__getattribute__(name)

    def save(self):
        super(UserJob, self).save()  # Call the "real" save() method
        cache.delete('user_job_%s' % self.user.id)

    def new_helper(self, helper_id):
        profile = UserProfile.objects.get_by_id(self.user.id)
        if str(helper_id) in self.helpers and not self.user.is_superuser: return 'duplicate'  # cheat for super users

        helpers = self.helpers
        helpers.append(str(helper_id))
        self.helper = ','.join(helpers)

        if self.help_need >= self.help_has:
            self.help_has += 1

        if len(helpers) >= sum(settings.JOB_HELPERS_NEEDED[:self.last_tier + 1]) and (
                    (self.last_tier < 5 and not profile.is_premium) or (self.last_tier < 6 and profile.is_premium)):
            self.last_tier += 1

        self.save()
        return 'ok'


class JobStatManager(models.Manager):
    def get_by_job(self, job=None, job_id=None):
        if job is not None:
            key = 'job_stat_%s' % job.id
        elif job_id is not None:
            key = 'job_stat_%s' % job_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if job is not None:
                item = self.get(job=job)
            elif job_id is not None:
                item = self.get(job__id=job_id)

        except JobStat.DoesNotExist:
            item = JobStat()
            if job:
                item.job = job
            elif job_id:
                item.job = Car.objects.get(pk=job_id)
            item.save()

        cache.set(key, pickle.dumps(item))
        return item


class JobStat(models.Model):
    job = models.ForeignKey(Car, unique=True)
    done = models.PositiveIntegerField(default=0)
    started = models.PositiveIntegerField(default=0)

    last_did = models.PositiveIntegerField(default=0)
    last_did_at = models.DateTimeField(default=datetime.datetime.now())
    last_started = models.PositiveIntegerField(default=0)
    last_started_at = models.DateTimeField(default=datetime.datetime.now())

    objects = JobStatManager()

    class Meta:
        db_table = 'job_stat'
        verbose_name = 'Job Stat'

    def __unicode__(self):
        return 'stats of job_id:%d' % self.pk

    def save(self):
        super(JobStat, self).save()
        cache.delete('job_stat_%s' % self.job.id)

    def delete(self):
        jid = self.job.id
        super(JobStat, self).delete()
        cache.delete('job_stat_%s' % jid)


class JobStatUserManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):
        if user is not None:
            key = 'job_stat_user_%s' % user.id
        elif user_id is not None:
            key = 'job_stat_user_%s' % user_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if user is not None:
                item = self.get(user=user)
            elif user_id is not None:
                item = self.get(user__id=user_id)

        except JobStatUser.DoesNotExist:
            item = JobStatUser()
            if user:
                item.user = user
            elif user_id:
                item.user = User.objects.get(pk=user_id)
            item.save()

        cache.set(key, pickle.dumps(item))
        return item


class JobStatUser(models.Model):
    user = models.ForeignKey(User)
    username = models.CharField(max_length=50)
    done = models.PositiveIntegerField(default=0)
    started = models.PositiveIntegerField(default=0)

    last_did_id = models.PositiveIntegerField()
    last_did_at = models.DateTimeField(default=datetime.datetime.now())
    last_started_id = models.PositiveIntegerField()
    last_started_at = models.DateTimeField(default=datetime.datetime.now())

    objects = JobStatUserManager()

    class Meta:
        db_table = 'job_stat_user'
        verbose_name = 'User\'s Job Stat'

    def __unicode__(self):
        return 'stats of jobs of user_id:%d' % self.pk

    def save(self):
        super(JobStatUser, self).save()
        cache.delete('job_stat_user_%s' % self.job.id)

    def delete(self):
        jid = self.job.id
        super(JobStatUser, self).delete()
        cache.delete('job_stat_user_%s' % jid)


class GarageManager(models.Manager):
    def get_by_user(self, user):
        key = 'garage_%s' % user.id
        item = cache.get(key)

        if item is not None:
            return pickle.loads(str(item))

        try:
            item = self.get(user=user)
        except Garage.DoesNotExist:
            item = Garage()
            item.user = user
            item.save()

        item.cars = item.cars
        cache.set(key, pickle.dumps(item))
        return item


class Garage(models.Model):
    user = models.ForeignKey(User)
    car = models.TextField()  # {'job_id': amnt, ...}

    objects = GarageManager()

    class Meta:
        db_table = 'user_garage'
        verbose_name = 'Garage'

    def __unicode__(self):
        return '%s\'s garage' % (self.user)

    def __getattr__(self, name):
        if name == 'cars':
            cars = {}
            for t in settings.TIERS: cars[t] = []

            if not self.car: return cars
            for car, amnt in json.loads(self.car).iteritems():
                car_obj = Car.objects.get_by_id(car)
                if not car_obj:
                    self.remove_car(car)
                    continue

                cars[car_obj.tier].append((car_obj, amnt))
            return cars
        if name == 'car_ids':
            if not self.car: return []
            return json.loads(self.car).keys()
        elif name == 'engine':
            return None
        else:
            return self.__getattribute__(name)

    def __len__(self):
        return self.count()

    def save(self):
        super(Garage, self).save()
        cache.delete('garage_%s' % self.user.id)

    def delete(self):
        uid = self.user.id
        super(Garage, self).delete()
        cache.delete('garage_%s' % uid)

    def has_car(self, cid):
        if len(self.car) == 0: return False
        return json.loads(self.car).has_key(str(cid))

    def add_car(self, cid):
        if len(self.car) > 0:
            cars = json.loads(self.car)
        else:
            cars = {}

        if cars.has_key(str(cid)):
            cars[str(cid)] += 1
        else:
            cars[str(cid)] = 1

        self.car = json.dumps(cars)
        self.save()

        c = Car.objects.get_by_id(cid)
        if self.engine:
            self.engine.notify.add(user=self.user, type='garage', key='cars_add', date='today')
            self.engine.notify.add(user=self.user, type='garage', key='cars', date=None, stream='%s|%s' % (
                reverse('encyclopedia_car', args=[slughifi(c.manuf), slughifi(c.name), str(c.id)]),
                c.display_short_name()))
            self.engine.notify.add(user=self.user, type='car_manuf', key=c.manuf, date=None)
            self.engine.notify.add(user=self.user, type='car_country', key=c.country, date=None)
            self.engine.notify.add(user=self.user, type='car_tier', key=c.tier, date=None)
            self.engine.notify.add(user=self.user, type='car_manuf', key=c.manuf, date=None)
            self.engine.notify.add(user=self.user, type='car_country', key=c.country, date=None)
            self.engine.notify.add(user=self.user, type='car_tier', key=c.tier, date=None)
            self.engine.notify.add(user=self.user, type='car_id', key=c.id, date=None)

        if c.year > 0:
            year = (c.year / 10) * 10
            if self.engine: self.engine.notify.add(user=self.user, type='car_year', key=year, date=None)
        if c.power_bhp > 0:
            bhp = (c.power_bhp / 100) * 100
            if self.engine: self.engine.notify.add(user=self.user, type='car_bhp', key=str(int(bhp)), date=None)
        # if c.sprint_0_100 > 0:
        # self.engine.notify.add(user=self.user, type='car_sprint', key=str(int(c.sprint_0_100)), date=None)
        if c.top_speed > 0:
            speed = (c.top_speed / 10) * 10
            if self.engine: self.engine.notify.add(user=self.user, type='car_speed', key=str(int(speed)), date=None)
        if c.weight > 0:
            weight = (c.weight / 100) * 100
            if self.engine: self.engine.notify.add(user=self.user, type='car_weight', key=str(int(weight)), date=None)

        return True

    def remove_car(self, cid):
        if len(self.car) > 0:
            cars = json.loads(self.car)
        else:
            return

        if not cars.has_key(str(cid)):
            return
        if cars.has_key(str(cid)):
            cars[str(cid)] -= 1
        if cars[str(cid)] == 0:
            del cars[str(cid)]

        self.car = json.dumps(cars)
        self.save()

        c = Car.objects.get_by_id(cid)
        if self.engine:
            self.engine.notify.remove(user=self.user, type='garage', key='cars_remove', date='today')
            self.engine.notify.remove(user=self.user, type='car_manuf', key=c.manuf, date=None)
            self.engine.notify.remove(user=self.user, type='car_country', key=c.country, date=None)
            self.engine.notify.remove(user=self.user, type='car_tier', key=c.tier, date=None)

        return True

    def count(self, unique=False):
        if len(self.car) == 0: return 0
        car = json.loads(self.car)
        if unique:
            return len(car.keys())
        else:
            return sum(car.values())
