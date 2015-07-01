# -*- coding: utf-8 -*-
from userprofile.models import UserStat


class Notify(object):
    def __init__(self, engine):
        self.engine = engine

    def add(self, *args, **kwargs):  # user, type, key, value, date=None, stream=None
        """
        notifications and stream

        - car_country
        - car_manuf
        - car_tier [1-6, PUNX]
        - cash [earn, spend]
        - credit [earn, spend]
        - exp [earn, level_up]
        - fight [win, draw, lost]
        - friend [add_friend]
        - garage [cars, cars_add, cars_remove]
        - job [done, help]
        - wishlist [add_item, remove_item]

        - achievement [ITEM]
        - auction [started, won, lost, sold, not_sold, outbid]
        - album [stick, completed, buy]
        """

        if hasattr(self.engine, 'user'):
            if not kwargs.has_key('user'):
                kwargs['user'] = self.engine.user.user

        if kwargs['type'] not in ('car_id'):
            kwargs['new_value'] = UserStat.objects.increment(*args, **kwargs)

            a, b = self.engine.achieve.trigger(*args, **kwargs)
            if a is not None or b is not None:
                for item in (a, b):
                    if item is None: continue
                    self.engine.stream.trigger(kwargs['user'], 'achievement', None, item)
                    UserStat.objects.increment(user=self.engine.user.user, type='achievement', key=item.name.lower(),
                                               value=1, date=None)

        if kwargs['date'] is None and kwargs.has_key('new_value'):
            wall = self.engine.stream.trigger(kwargs['user'], kwargs['type'], kwargs['key'], kwargs.get('stream'))

    def remove(self, *args, **kwargs):  # user, type, key, value, date=None
        # wall = self.engine.stream.trigger(*args, **kwargs)
        stat = UserStat.objects.decrement(*args, **kwargs)
