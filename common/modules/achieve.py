# -*- coding: utf-8 -*-
# import os, os.path
# import datetime
from job.models import Garage
from achievement.models import UserAchievement, Achievement as AchievementModel
from userprofile.models import UserProfile


class Achieve(object):
    def __init__(self, engine):
        self.engine = engine

        self.achievements = {
            'car_id,__in__': [

            ],
            'car_manuf,Porsche': [
                Achievement(name='Porsche Fan', level=1, start_value=1, value=10, cash=10000, exp=500, credit=1,
                            car_id=16688),
                Achievement(name='Porsche Fan', level=2, start_value=11, value=25, cash=25000, exp=1000, credit=1,
                            car_id=16686),
                Achievement(name='Porsche Fan', level=3, start_value=26, value=40, cash=50000, exp=2000, credit=1,
                            car_id=16698),
            ],
            'car_manuf,Lamborghini': [
                Achievement(name='Lamborghini Fan', start_value=1, level=1, value=10, cash=10000, exp=500, credit=1,
                            car_id=13711),
                Achievement(name='Lamborghini Fan', start_value=11, level=2, value=25, cash=25000, exp=1000, credit=1,
                            car_id=13714),
                Achievement(name='Lamborghini Fan', start_value=26, level=3, value=40, cash=50000, exp=2000, credit=1,
                            car_id=16695),
            ],
            'car_manuf,Ferrari': [
                Achievement(name='Ferrari Fan', level=1, start_value=1, value=10, cash=10000, exp=500, credit=1,
                            car_id=16304),
                Achievement(name='Ferrari Fan', level=2, start_value=11, value=25, cash=25000, exp=1000, credit=1,
                            car_id=757),
                Achievement(name='Ferrari Fan', level=3, start_value=26, value=40, cash=50000, exp=2000, credit=1,
                            car_id=16290),
            ],
            'car_manuf,BMW': [
                Achievement(name='BMW Fan', level=1, start_value=1, value=10, cash=8000, exp=500, credit=1,
                            car_id=16429),
                Achievement(name='BMW Fan', level=2, start_value=11, value=25, cash=20000, exp=1000, credit=1,
                            car_id=16448),
                Achievement(name='BMW Fan', level=3, start_value=26, value=40, cash=40000, exp=2000, credit=1,
                            car_id=16461),
            ],
            'car_manuf,Aston Martin': [
                Achievement(name='Aston Martin Fan', level=1, start_value=1, value=10, cash=10000, exp=500, credit=1,
                            car_id=14144),
                Achievement(name='Aston Martin Fan', level=2, start_value=11, value=25, cash=25000, exp=1000, credit=1,
                            car_id=16696),
                Achievement(name='Aston Martin Fan', level=3, start_value=26, value=40, cash=50000, exp=2000, credit=1,
                            car_id=15816),
            ],
            'car_manuf,Cadillac': [
                Achievement(name='Cadillac Fan', level=1, start_value=1, value=10, cash=8000, exp=500, credit=1,
                            car_id=16693),
                Achievement(name='Cadillac Fan', level=2, start_value=11, value=25, cash=20000, exp=1000, credit=1,
                            car_id=16586),
                Achievement(name='Cadillac Fan', level=3, start_value=26, value=40, cash=40000, exp=2000, credit=1,
                            car_id=16590),
            ],
            'car_manuf,Lexus': [
                Achievement(name='Lexus Fan', level=1, start_value=1, value=10, cash=8000, exp=500, credit=1,
                            car_id=16697),
                Achievement(name='Lexus Fan', level=2, start_value=11, value=25, cash=20000, exp=1000, credit=1,
                            car_id=8693),
                Achievement(name='Lexus Fan', level=3, start_value=26, value=40, cash=40000, exp=2000, credit=1,
                            car_id=8698),
            ],
            'car_year,__in__': [
                # Achievement(name='Grandpa', level=1, start_value=1,  value=5, value_in=('1880', '1890' '1900', '1910', '1920', '1930', '1940', '1950')),
                # Achievement(name='Grandpa', level=2, start_value=6,  value=15, value_in=('1880', '1890' '1900', '1910', '1920', '1930', '1940', '1950')),
                # Achievement(name='Grandpa', level=3, start_value=16, value=25, value_in=('1880', '1890' '1900', '1910', '1920', '1930', '1940', '1950'), credit=10),
            ],
            'car_year,1960': [
                # Achievement(name='60s', level=1, start_value=1,  value=5,  cash=18000,  exp=2500,  credit=0, car_id=0),
                # Achievement(name='60s', level=2, start_value=6,  value=15, cash=42000,  exp=4000,  credit=0, car_id=0),
                # Achievement(name='60s', level=3, start_value=16, value=25, cash=75000,  exp=7500,  credit=5, car_id=0),
            ],
            'car_year,1970': [
                # Achievement(name='70s', level=1, start_value=1,  value=5,  cash=14000,  exp=1500,  credit=0, car_id=0),
                # Achievement(name='70s', level=2, start_value=6,  value=15, cash=36000,  exp=2500,  credit=0, car_id=0),
                # Achievement(name='70s', level=3, start_value=16, value=25, cash=60000,  exp=4000,  credit=4, car_id=0),
            ],
            'car_year,1980': [
                Achievement(name='80s', level=1, start_value=1, value=5, cash=10000, exp=750, credit=0, car_id=5506),
                Achievement(name='80s', level=2, start_value=6, value=15, cash=24000, exp=1500, credit=0, car_id=1154),
                Achievement(name='80s', level=3, start_value=16, value=25, cash=48000, exp=2500, credit=3,
                            car_id=13716),
            ],
            'car_year,1990': [
                Achievement(name='90s', level=1, start_value=1, value=5, cash=8000, exp=500, credit=0, car_id=14151),
                Achievement(name='90s', level=2, start_value=6, value=15, cash=20000, exp=1000, credit=0, car_id=6869),
                Achievement(name='90s', level=3, start_value=16, value=25, cash=40000, exp=2000, credit=3, car_id=9879),
            ],
            'car_bhp,300': [
                # Achievement(name='300 BHP', level=1, start_value=1,  value=5),
                # Achievement(name='300 BHP', level=2, start_value=6,  value=15),
                # Achievement(name='300 BHP', level=3, start_value=16, value=25),
            ],
            'car_bhp,400': [
                # Achievement(name='400 BHP', level=1, start_value=1,  value=5),
                # Achievement(name='400 BHP', level=2, start_value=6,  value=15),
                # Achievement(name='400 BHP', level=3, start_value=16, value=25),
            ],
            'car_bhp,500': [
                # Achievement(name='500 BHP', level=1, start_value=1,  value=5),
                # Achievement(name='500 BHP', level=2, start_value=6,  value=15),
                # Achievement(name='500 BHP', level=3, start_value=16, value=25),
            ],
            'car_bhp,600': [
                # Achievement(name='600 BHP', level=1, start_value=1,  value=5),
                # Achievement(name='600 BHP', level=2, start_value=6,  value=15),
                # Achievement(name='600 BHP', level=3, start_value=16, value=25),
            ],
            'car_bhp,700': [
                # Achievement(name='700 BHP', level=1, start_value=1,  value=5),
                # Achievement(name='700 BHP', level=2, start_value=6,  value=15),
                # Achievement(name='700 BHP', level=3, start_value=16, value=25),
            ],
            'car_bhp,__in__': [
                # Achievement(name='800+ BHP', level=1, start_value=1,  value=5, value_in=('800', '900', '1000', '1100', '1200')),
                # Achievement(name='800+ BHP', level=2, start_value=6,  value=15, value_in=('800', '900', '1000', '1100', '1200')),
                # Achievement(name='800+ BHP', level=3, start_value=16, value=25, value_in=('800', '900', '1000', '1100', '1200')),
            ],
            'car_tier,6': [
                Achievement(name='VIP', start_value=1, value=100, cash=1000000, exp=50000, credit=5, car_id=11526),
            ],
            'job,done': [
                Achievement(name='Workoholic', level=1, start_value=1, value=25, cash=5000, exp=100, credit=0,
                            car_id=15112),
                Achievement(name='Workoholic', level=2, start_value=26, value=50, cash=10000, exp=250, credit=0,
                            car_id=6781),
                Achievement(name='Workoholic', level=3, start_value=51, value=100, cash=15000, exp=750, credit=0,
                            car_id=16361),
                Achievement(name='Serious Addiction', level=1, start_value=101, value=250, cash=50000, exp=1000,
                            credit=1, car_id=1627),
                Achievement(name='Serious Addiction', level=2, start_value=251, value=500, cash=100000, exp=2500,
                            credit=1, car_id=742),
                Achievement(name='Serious Addiction', level=3, start_value=501, value=1000, cash=150000, exp=7500,
                            credit=1, car_id=16691),
            ],
            'job,help': [
                Achievement(name='Helping Hand', level=1, start_value=1, value=10, cash=10000, exp=200, credit=0,
                            car_id=8628),
                Achievement(name='Helping Hand', level=2, start_value=11, value=25, cash=20000, exp=500, credit=0,
                            car_id=7160),
                Achievement(name='Helping Hand', level=3, start_value=26, value=50, cash=30000, exp=1500, credit=0,
                            car_id=13699),
            ],
            'car_country,UK': [
                Achievement(name='Tea Time', level=1, start_value=1, value=25, cash=6000, exp=500, credit=0,
                            car_id=14264),
                Achievement(name='Tea Time', level=2, start_value=26, value=50, cash=18000, exp=1000, credit=0,
                            car_id=11871),
                Achievement(name='Tea Time', level=3, start_value=51, value=100, cash=36000, exp=2000, credit=3,
                            car_id=15816),
            ],
            'car_country,USA': [
                Achievement(name='Jankee', level=1, start_value=1, value=25, cash=6000, exp=500, credit=0,
                            car_id=11472),
                Achievement(name='Jankee', level=2, start_value=26, value=50, cash=18000, exp=1000, credit=0,
                            car_id=1395),
                Achievement(name='Jankee', level=3, start_value=51, value=100, cash=36000, exp=2000, credit=3,
                            car_id=11450),
            ],
            'car_country,Germany': [
                Achievement(name='Cartoberfest', level=1, start_value=1, value=25, cash=6000, exp=500, credit=0,
                            car_id=9016),
                Achievement(name='Cartoberfest', level=2, start_value=26, value=50, cash=18000, exp=1000, credit=0,
                            car_id=1195),
                Achievement(name='Cartoberfest', level=3, start_value=51, value=100, cash=36000, exp=2000, credit=3,
                            car_id=11850),
            ],
            'car_country,Italy': [
                Achievement(name='Italian Job', level=1, start_value=1, value=25, cash=6000, exp=500, credit=0,
                            car_id=13720),
                Achievement(name='Italian Job', level=2, start_value=26, value=50, cash=18000, exp=1000, credit=0,
                            car_id=13679),
                Achievement(name='Italian Job', level=3, start_value=51, value=100, cash=36000, exp=2000, credit=3,
                            car_id=15518),
            ],
            'car_country,France': [
                Achievement(name='Eiffel Power', level=1, start_value=1, value=25, cash=6000, exp=500, credit=0,
                            car_id=1950),
                Achievement(name='Eiffel Power', level=2, start_value=26, value=50, cash=18000, exp=1000, credit=0,
                            car_id=9951),
                Achievement(name='Eiffel Power', level=3, start_value=51, value=100, cash=36000, exp=2000, credit=3,
                            car_id=2291),
            ],
            'car_country,__in__': [
                Achievement(name='Fast & Furious', level=1, start_value=1, value=25,
                            value_in=('Japan', 'China', 'Malaysia', 'South Korea'), cash=6000, exp=500, credit=0,
                            car_id=16034),
                Achievement(name='Fast & Furious', level=2, start_value=26, value=50,
                            value_in=('Japan', 'China', 'Malaysia', 'South Korea'), cash=6000, exp=500, credit=0,
                            car_id=12909),
                Achievement(name='Fast & Furious', level=3, start_value=51, value=100,
                            value_in=('Japan', 'China', 'Malaysia', 'South Korea'), cash=6000, exp=500, credit=3,
                            car_id=15978),
            ],
            'friend,add_friend': [
                Achievement(name='Celebrity', level=1, start_value=1, value=5, cash=10000, exp=500, credit=1,
                            car_id=4141),
                Achievement(name='Celebrity', level=2, start_value=6, value=20, cash=25000, exp=1500, credit=5,
                            car_id=16206),
                Achievement(name='Celebrity', level=3, start_value=21, value=50, cash=100000, exp=3500, credit=10,
                            car_id=725),
            ],
            'album,stick': [
                Achievement(name='First Sticker', start_value=0, value=1, cash=5000, exp=500, credit=1, car_id=686),
                Achievement(name='Serial Sticker', level=1, start_value=1, value=10, cash=10000, exp=1000, credit=1,
                            car_id=14088),
                Achievement(name='Serial Sticker', level=2, start_value=11, value=25, cash=15000, exp=1500, credit=1,
                            car_id=15974),
                Achievement(name='Serial Sticker', level=3, start_value=26, value=50, cash=25000, exp=2500, credit=1,
                            car_id=2298),
            ],
            'album,buy': [
                Achievement(name='First Album', start_value=0, value=1, cash=5000, exp=500, credit=1, car_id=15419),
                Achievement(name='Albums Fan', level=1, start_value=1, value=5, cash=10000, exp=1000, credit=1,
                            car_id=12631),
                Achievement(name='Albums Fan', level=2, start_value=6, value=10, cash=15000, exp=1500, credit=1,
                            car_id=16448),
                Achievement(name='Albums Fan', level=3, start_value=11, value=20, cash=25000, exp=2500, credit=1,
                            car_id=13720),
            ],
            'album,completed': [
                Achievement(name='Book Closed', level=1, start_value=0, value=1, cash=5000, exp=500, credit=5,
                            car_id=16454),
                Achievement(name='Book Closed', level=2, start_value=2, value=3, cash=10000, exp=1000, credit=5,
                            car_id=6540),
                Achievement(name='Book Closed', level=3, start_value=4, value=8, cash=15000, exp=1500, credit=5,
                            car_id=15520),
                Achievement(name='Book Closed', level=4, start_value=14, value=15, cash=25000, exp=2500, credit=10,
                            car_id=16480),
                Achievement(name='Book Closed', level=5, start_value=16, value=25, cash=75000, exp=7500, credit=15,
                            car_id=16292),
            ],
            'auction,income': [
                Achievement(name='Business Virgin', start_value=0, value=1, cash=5000, exp=500, credit=1, car_id=7678),
                Achievement(name='Businessman', level=1, start_value=1, value=30000, cash=10000, exp=1000, credit=1,
                            car_id=15632),
                Achievement(name='Businessman', level=2, start_value=30001, value=100000, cash=15000, exp=1500,
                            credit=1, car_id=6032),
                Achievement(name='Businessman', level=3, start_value=100001, value=1000000, cash=25000, exp=2500,
                            credit=1, car_id=762),
                # Achievement(name='Investor', level=1, start_value=1000001, value=2000000),
                # Achievement(name='Investor', level=2, start_value=2000001, value=5000000),
                # Achievement(name='Investor', level=3, start_value=5000001, value=10000000),
            ],
            'auction,outcome': [
                Achievement(name='Shopping First-timer', start_value=0, value=1, cash=5000, exp=500, credit=1,
                            car_id=11481),
                Achievement(name='Shopping Spree', level=1, start_value=2, value=20000, cash=5000, exp=500, credit=1,
                            car_id=13868),
                Achievement(name='Shopping Spree', level=2, start_value=20001, value=100000, cash=15000, exp=1500,
                            credit=1, car_id=9497),
                Achievement(name='Shopping Spree', level=3, start_value=100001, value=1000000, cash=25000, exp=2500,
                            credit=1, car_id=138),
                # Achievement(name='Shopoholic', level=1, start_value=1000001, value=2000000),
                # Achievement(name='Shopoholic', level=2, start_value=2000001, value=5000000),
                # Achievement(name='Shopoholic', level=3, start_value=5000001, value=10000000),
            ],
        }

        self.achievement_desc = {
            'friend': {
                'title': '',
                'desc': '',
            },
            'friend,add_friend': {
                'title': 'Add friends',
                'desc': 'invite given number of friends to complete',
                'currency': 'friends',
            },
            'car_country': {
                'title': '',
                'desc': '',
            },
            'car_country,__in__': {
                'title': '',
                'desc': '',
                'currency': 'Asian cars',
            },
            'car_id': {
                'title': '',
                'desc': '',
            },
            'car_id,__in__': {
                'title': '',
                'desc': '',
                'currency': 'cars',
            },
            # 'car_bhp': {
            # 	'title': '',
            # 	'desc': '',
            # },
            # 'car_bhp,300': {
            # 	'title': '',
            # 	'desc': '',
            # 	'currency': 'cars',
            # },
            # 'car_bhp,400': {
            # 	'title': '',
            # 	'desc': '',
            # 	'currency': 'cars',
            # },
            # 'car_bhp,500': {
            # 	'title': '',
            # 	'desc': '',
            # 	'currency': 'cars',
            # },
            # 'car_bhp,600': {
            # 	'title': '',
            # 	'desc': '',
            # 	'currency': 'cars',
            # },
            # 'car_bhp,700': {
            # 	'title': '',
            # 	'desc': '',
            # 	'currency': 'cars',
            # },
            # 'car_bhp,__in__': {
            # 	'title': '',
            # 	'desc': '',
            # 	'currency': 'cars',
            # },
            'car_manuf': {
                'title': '',
                'desc': '',
            },
            'car_manuf,Aston Martin': {
                'title': '',
                'desc': '',
                'currency': 'Aston Martin cars',
            },
            'car_manuf,BMW': {
                'title': '',
                'desc': '',
                'currency': 'BMW cars',
            },
            'car_manuf,Cadillac': {
                'title': '',
                'desc': '',
                'currency': 'Cadillac cars',
            },
            'car_manuf,Lamborghini': {
                'title': '',
                'desc': '',
                'currency': 'Lamborghini cars',
            },
            'car_manuf,Porsche': {
                'title': '',
                'desc': '',
                'currency': 'Porsche cars',
            },
            'car_manuf,Lexus': {
                'title': '',
                'desc': '',
                'currency': 'Lexus cars',
            },
            'car_manuf,Ferrari': {
                'title': '',
                'desc': '',
                'currency': 'Ferrari cars',
            },
            'car_country': {
                'title': '',
                'desc': '',
            },
            'car_country,Germany': {
                'title': '',
                'desc': '',
                'currency': 'German cars',
            },
            'car_country,France': {
                'title': '',
                'desc': '',
                'currency': 'French cars',
            },
            'car_country,UK': {
                'title': '',
                'desc': '',
                'currency': 'British cars',
            },
            'car_country,USA': {
                'title': '',
                'desc': '',
                'currency': 'American cars',
            },
            'car_country,Italy': {
                'title': '',
                'desc': '',
                'currency': 'Italian cars',
            },
            'car_country,__in__': {
                'title': '',
                'desc': '',
                'currency': 'cars',
            },
            'car_year': {
                'title': '',
                'desc': '',
            },
            'car_year,1960': {
                'title': '',
                'desc': '',
                'currency': '1960-1969 cars',
            },
            'car_year,1970': {
                'title': '',
                'desc': '',
                'currency': '1970-1979 cars',
            },
            'car_year,1980': {
                'title': '',
                'desc': '',
                'currency': '1980-1989 cars',
            },
            'car_year,1990': {
                'title': '',
                'desc': '',
                'currency': '1990-1999 cars',
            },
            # 'car_year,__in__': {
            # 	'title': '',
            # 	'desc': '',
            # 	'currency': '',
            # }
            'car_tier': {
                'title': '',
                'desc': '',
            },
            'car_tier,6': {
                'title': '',
                'desc': '',
                'currency': 'Tier 6 cars',
            },
            'auction': {
                'title': '',
                'desc': '',
            },
            'auction,income': {
                'title': '',
                'desc': '',
                'currency': 'revenue of auctions',
            },
            'auction,outcome': {
                'title': '',
                'desc': '',
                'currency': 'spent on auctions',
            },
            'album': {
                'title': '',
                'desc': '',
            },
            'album,stick': {
                'title': '',
                'desc': '',
                'currency': 'cars sticked',
            },
            'album,buy': {
                'title': '',
                'desc': '',
                'currency': 'albums bought',
            },
            'album,completed': {
                'title': '',
                'desc': '',
                'currency': 'albums completed',
            },
            'job': {
                'title': '',
                'desc': '',
            },
            'job,help': {
                'title': '',
                'desc': '',
                'currency': 'helpers',
            },
            'job,done': {
                'title': '',
                'desc': '',
                'currency': 'completed jobs',
            },
        }

    def trigger(self, *args, **kwargs):  # user, type, key, value, date=None

        def _perform_trigger(ua, key, item, value, date):
            if not item.is_day_wise and date is not None: return
            if ua.dones.has_key(key) and ua.dones[key].has_key(item.name.lower()):
                if ua.dones[key][item.name.lower()].has_key('level'):
                    if int(ua.dones[key][item.name.lower()]['level']) >= int(item.level): return
                else:
                    return
            if item.start_value > value: return

            if value < item.value:
                ua.add_pending(key, item, value)
                if self.engine:
                    self.engine.add_summary('achieve', 'pending', item.as_dict(key, value))
                return 0

            # achievement done!
            ua.add(key, item)
            if self.engine:
                self.engine.add_summary('achieve', 'done', item.as_dict(key, value))

            if item.exp > 0 or item.cash > 0 or item.credit > 0:
                p = UserProfile.objects.get_by_user(user=kwargs['user'])
                if item.exp > 0:
                    p.earn('exp', item.exp, False)
                if item.cash > 0:
                    p.earn('cash', item.cash, False)
                if item.credit > 0:
                    p.earn('credit', item.credit, False)
                p.save()

            if item.car_id > 0:
                garage = Garage.objects.get_by_user(user=kwargs['user'])
                if self.engine:
                    garage.engine = self.engine
                garage.add_car(item.car_id)

            return item

        ua = self.get_by_user(user=kwargs['user'])
        a, b = None, None
        key_1 = '%s,%s' % (kwargs['type'].lower(), unicode(kwargs['key']).lower())
        key_2 = '%s,__in__' % (kwargs['type'].lower())

        if self.achievements.has_key(key_1):
            for item in self.achievements[key_1]:
                a = _perform_trigger(ua, key_1, item, kwargs['new_value'], kwargs['date'])
                if a == 0:
                    a = None
                    break
                if a is None: continue

        if self.achievements.has_key(key_2):
            for item in self.achievements[key_2]:
                if kwargs['key'] not in item.value_in: continue
                b = _perform_trigger(ua, key_2, item, kwargs['new_value'], kwargs['date'])
                if b == 0:
                    b = None
                    break
                if b is None: continue

        return a, b

    def get_by_user(self, user):
        return UserAchievement.objects.get_by_user(user=user)


class Achievement(object):
    def __init__(self, **kwargs):
        self.name = ''
        self.level = 0
        self.value = 0
        self.value_in = ()
        self.exp = 0
        self.cash = 0
        self.credit = 0
        self.car_id = 0
        self.is_hidden = False
        self.is_income_hidden = False
        self.is_day_wise = False

        for k, v in kwargs.iteritems():
            self.__dict__[k] = v

        # self.img = 'images/achievements/%s.jpg' % slughifi(self.name)
        self.img = 'images/achievements/%s.png' % str(self.level)

    def save(self, type, key):
        try:
            a = AchievementModel.objects.get(type=type, key=key, name=self.name, level=self.level)
        except AchievementModel.DoesNotExist:
            a = AchievementModel()
            a.type = type
            a.key = key

        for k, v in self.__dict__.iteritems():
            a.__dict__[k] = v
        a.save()

    def as_dict(self, tk, value):
        t, k = tk.split(',')
        a = AchievementModel.objects.get(type=t, key=k, name=self.name, level=self.level)

        d = {}
        for k, v in self.__dict__.iteritems():
            d[k] = a.__dict__[k]
        d['type'] = a.type
        d['key'] = a.key
        d['typekey'] = tk
        d['current_value'] = value
        return d
