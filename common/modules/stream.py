# -*- coding: utf-8 -*-

from main.models import UserStream


class Stream(object):
    def __init__(self, engine):

        self.engine = engine

        self.STREAM = {
            'album': {
                'stick': ['wall'],
                'completed': ['wall'],
                'buy': ['wall', 'private'],
            },
            'auction': {
                'started': [],
                'won': ['wall'],
                'lost': ['wall', 'private'],
                'sold': ['wall'],
                'not_sold': ['wall', 'private'],
                'outbid': ['wall', 'private'],
            },
            'achievement': {
                'done': ['wall'],
            },
            'car_country': [],
            'car_manuf': [],
            'car_tier': [],
            'cash': {
                'earn': [],
                'spend': [],
            },
            'exp': {
                'level_up': ['wall'],
            },
            'fight': {
                'win': [],
                'draw': [],
                'lost': [],
            },
            'friend': {
                'add_friend': ['wall'],
            },
            'garage': {
                'cars': ['wall'],
                'cars_add': [],
                'cars_remove': [],
            },
            'job': {
                'done': [],
                'help': [],
            },
            'gift': {
                'add_pending': [],
                'confirm_gift': ['wall'],
                'decline_gift': [],
            },
            'wishlist': {
                'add_item': ['wall'],
                'remove_item': [],
            },
        }

    def trigger(self, user, type, key, translate):

        if not self.STREAM.has_key(type) and type != 'achievement':
            return
        try:
            if not self.STREAM[type].has_key(key):
                return
        except AttributeError:
            return

        if key is None:
            stream = self.STREAM[type]
        else:
            stream = self.STREAM[type][key]

        if 'wall' not in stream:
            return

        un = UserStream()
        un.type = type
        un.key = key or ''
        if user is not None:
            un.user = user
        un.content = translate
        if 'private' in stream:
            un.is_private = True
        un.save()

    def translate(self, txt, trans_part):
        if len(trans_part) == 0 or txt.find('[[') < 0: return txt

        i = 0
        for text in trans_part.split('|'):
            txt = txt.replace('[[%d]]' % i, text)
            i = i + 1
        return txt
