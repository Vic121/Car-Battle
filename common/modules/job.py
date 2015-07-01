# -*- coding: utf-8 -*-
import logging

from django.conf import settings

import datetime
from common.helpers.core import reverse
from job.models import UserJob, JobStat


class Job(object):
    def __init__(self, engine):
        self.engine = engine
        if not hasattr(engine, 'user'): return engine.redirect(reverse('home'))

        profile = engine.user.profile
        if profile.job_next_day_at is None or profile.job_next_day_at <= datetime.datetime.now():
            UserJob.objects.filter(is_active=True).update(is_active=False)

            profile.job_round = 1
            profile.job_tier = 1
            profile.job_max_round_today = profile.job_max_round
            profile.job_next_day_at = datetime.datetime.now() + datetime.timedelta(days=1)
            profile.job_id = 0
            profile.save()

        self.user_job = UserJob.objects.get_by_user(user=engine.user.user, profile=engine.user.profile)

        # time left
        self.time_left = str(profile.job_next_day_at - datetime.datetime.now()).split('.')[0].split(':')

        if len(self.time_left) > 3:
            self.time_left = ''
        elif len(self.time_left) == 3:
            if int(self.time_left[0]) == 0 and int(self.time_left[1]) == 0:
                self.time_left = 'almost finished'
            elif int(self.time_left[0]) == 0:
                self.time_left = '%smin left' % (self.time_left[1].lstrip('0'))
            else:
                self.time_left = '%sh %smin left' % (self.time_left[0].lstrip('0'), self.time_left[1].lstrip('0'))
        else:
            self.time_left = 'almost finished'

    def collect_job(self, car_id):
        car = None

        if not self.user_job or not self.user_job.is_active: return

        try:
            for i in xrange(0, self.user_job.last_tier):
                if self.user_job.jobs[i].id == int(car_id):
                    car = self.user_job.jobs[i]
                    break
            if not car: raise KeyError  # ten sam blad, gdy zly car_id
        except KeyError:
            logging.warning("%s tried to link-collect-hack" % self.engine.user.user)
            # statystyki
            self.engine.log.message(message="You're not yet allowed to collect this car.")
            return

        if car.tier == '6' and not self.engine.user.profile.is_premium:
            self.engine.log.message(
                message="Tier 6 cars are for Supporters only. <a href='%s'>Become a supporter</a>." % reverse('store'))
            return

        # garaz
        self.engine.user.get_garage()
        self.engine.user.garage.add_car(car.id)
        self.engine.user.profile.cars = len(self.engine.user.garage)

        # kasa
        self.engine.user.profile.earn('cash', settings.TIER_INCOME[str(self.user_job.last_tier)], False)
        self.engine.user.profile.earn('exp', settings.EXP['collect_car_tier_%s' % car.tier], engine=self.engine)

        self.engine.user.refresh_profile()

        self.engine.add_summary('job', 'done', {'cash': settings.TIER_INCOME[str(self.user_job.last_tier)],
                                                'exp': settings.EXP['collect_car_tier_%s' % car.tier], 'car': car})

        self.engine.notify.add(user=self.engine.user.user, type='job', key='done', date='today')
        self.engine.notify.add(user=self.engine.user.user, type='job', key='done', date=None)
        if self.user_job.help_has > 0:
            self.engine.notify.add(user=self.engine.user.user, type='job', key='help', date='today')
            self.engine.notify.add(user=self.engine.user.user, type='job', key='help', date=None)

        # finish round
        job_stat = JobStat.objects.get_by_job(job=car)
        job_stat.done += 1
        job_stat.last_did = self.engine.user.user
        job_stat.last_did_at = datetime.datetime.now()
        job_stat.save()

        self.new_round()

    def new_round(self):
        UserJob.objects.filter(is_active=True).update(is_active=False)

        profile = self.engine.user.profile
        profile.job_id = 0
        if profile.job_round <= profile.job_max_round_today:
            profile.job_round += 1
            profile.job_tier = 1
        profile.save()
