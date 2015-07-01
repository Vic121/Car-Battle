# -*- coding: utf-8 -*-
import logging
import random

from django.conf import settings

import datetime


# from django.db import models
# from django.db import connection
from userprofile.models import UserProfile
# from django.core.cache import cache

from job.models import Garage
from friend.models import Friend


class User(object):
    def __init__(self, engine):
        self.engine = engine
        self.refresh_profile()

        self.energy_progress()
        self.garage = None
        self.friends = None

    def get_by_id(self, user=None, user_id=None, fb_id=None):
        if user:
            return UserProfile.objects.get_by_id(user_id=user.id)
        if user_id:
            return UserProfile.objects.get_by_id(user_id=user_id)
        if fb_id:
            return UserProfile.objects.get_by_fb_id(fb_id)
        raise UserProfile.DoesNotExist

    def refresh_profile(self):
        self.profile = UserProfile.objects.get(user=self.engine.request.user)
        self.user = self.profile.user

    def on_level_up(self, new_level):
        self.engine.log.message(message="<p>PROMOTED! You're now on level %d!</p>" % new_level)

        if 0 < new_level <= 10:
            tier = 3
        elif 10 < new_level <= 20:
            tier = 4
        else:
            tier = 5

        self.buy_cars(1, [tier - 1], msg="""As you promoted we give you a new piece to your garage""", price=0)
        self.buy_cars(1, ['P', 'U', 'N', 'X'], msg="", price=0)

    def get_garage(self, user=None):
        if user is not None:
            return Garage.objects.get_by_user(user=user)

        if self.garage is None:
            self.garage = Garage.objects.get_by_user(user=self.user)
            self.garage.engine = self.engine
        return self.garage

    def get_friends(self):
        if self.friends is None:
            self.friends = Friend.objects.get_by_user(user=self.user)
        return self.friends

    def energy_progress(self):
        if not hasattr(self, 'profile'): return
        if self.profile.next_energy_at > datetime.datetime.now(): return

        delta = (datetime.datetime.now() - self.profile.next_energy_at)

        diff = delta.seconds + delta.days * 3600 * 24
        diff = int(diff / int(self.engine.settings.ADD_ENERGY_EVERY_SECONDS)) + 1

        self.profile.energy += diff
        if self.profile.energy > settings.MAX_ENERGY:
            self.profile.energy = settings.MAX_ENERGY
        self.profile.next_energy_at = datetime.datetime.now() + datetime.timedelta(
            seconds=int(self.engine.settings.ADD_ENERGY_EVERY_SECONDS))
        self.profile.save()

    # --- Buy

    def buy_premium(self):
        price = settings.PRICING['premium']

        if not self.profile.has_enough('credit', price):
            self.engine.log.message(message="You have not enough credits to upgrade your account. Buy some first.")
            return

        self.profile.spend('credit', price)
        if self.profile.is_premium:
            self.profile.is_premium_until += datetime.timedelta(days=30)
        else:
            self.profile.is_premium_until = datetime.datetime.now() + datetime.timedelta(days=30)
        self.profile.is_premium = True
        self.profile.save()

        self.engine.log.message(message="Account upgraded. Thank you!")
        self.engine.log.add_log('+premium')
        logging.warning('%s upgraded to premium' % self.user)

    def check_premium(self):
        if self.profile.is_premium:
            if self.profile.is_premium_until < datetime.datetime.now():
                self.profile.is_premium = False
                self.profile.save()
                logging.warning("%s no longer a supporter" % self.profile)

    def buy_cars(self, how_many, config, msg=None, price=None):
        from common.models import Car

        if price is None:
            try:
                price = settings.PRICING['cars'][str(config)]
                config = settings.PRICING_CAR_CONFIG[str(config)]
            except KeyError:
                self.engine.log.message(message="Unknown option: %s/%s" % (how_many, config))
                return

        if not self.profile.has_enough('credit', price):
            self.engine.log.message(message="You have not enough credits. Buy some first.")
            return

        self.profile.spend('credit', price)
        self.profile.save()

        self.engine.register('job')
        self.get_garage()

        how_many = int(how_many)
        new_cars = []
        for x in xrange(0, how_many):
            r = random.choice(config)

            try:
                new_car = Car.objects.draw_cars(self.profile)[str(r)]
            except KeyError:
                continue

            self.garage.add_car(new_car.id)
            new_cars.append(new_car)

        self.engine.user.profile.cars = len(self.garage)
        self.engine.user.profile.save()
        self.engine.user.refresh_profile()

        self.engine.add_summary('shop', 'new_cars', {'cars': new_cars})

        if price > 0:
            logging.debug('%s bought %d cars' % (self.user, how_many))
        else:
            logging.debug('%s got %d cars' % (self.user, how_many))
