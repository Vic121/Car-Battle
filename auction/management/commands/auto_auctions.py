#!/usr/bin/python
import random

import simplejson as json
from django.core.management.base import NoArgsCommand

import datetime


# from django.db import connection
# from django.core.cache import cache
from django.contrib.auth.models import User

import logging
from auction.models import Auction
from common.models import Car

SELLER = User.objects.get(pk=71)


class Command(NoArgsCommand):
    def __add_auction(self, car):

        if car.tier in (1, 2):
            days = 1
        elif car.tier in (3, 4):
            days = 2
        else:
            days = 3

        a = Auction()
        a.seller = SELLER
        a.title = "%s %s" % (car.manuf, car.name)
        a.car = car
        a.tier = car.tier
        a.details = json.dumps(
            {"engine": str(car.engine_up), "product_type": "car", "hp": str(car.power_bhp), "year": str(car.year),
             "product_id": int(car.id)})
        a.start_price = int(car.tier) * 4000
        if int(car.tier) == 6:
            a.start_price = 50000
        a.current_price = a.start_price
        a.end_at = datetime.datetime.now() + datetime.timedelta(days=days, hours=random.randint(0, 12),
                                                                minutes=random.randint(0, 60))
        a.save()

    def handle_noargs(self, **options):
        logging.debug('auto_auctions.py started @ %s' % str(datetime.datetime.now()))

        CONFIG = {'6': 1, '5': 1, '4': 3, '3': 3, '2': 3, '1': 3, 'P': 3, 'U': 2, 'X': 2}

        tier = {}
        for x in xrange(1, 7):
            tier[str(x)] = Car.objects.filter(is_active=True, is_active_in_battle=True, in_battle=True, tier=x)

        for k, v in CONFIG.iteritems():
            if not tier.has_key(k) or len(tier[k]) == 0: continue
            [self.__add_auction(random.choice(tier[k])) for x in xrange(0, v)]

        logging.debug('auto_auctions.py finished @ %s' % str(datetime.datetime.now()))
