import logging
import random

from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User

import datetime
import cPickle as pickle
from common.helpers.slughifi import slughifi


class DummyRequest(object):
    def __init__(self, uid):
        from userprofile.models import UserProfile

        self.profile = UserProfile.objects.get_by_id(uid)
        self.user = self.profile.user

        self.session = {}
        self.LANGUAGE_CODE = getattr(self.profile, "pref_lang", 'en')
        self.META = {'HTTP_ACCEPT_LANGUAGE': getattr(self.profile, "pref_lang", 'en')}
        self.GET = {}
        self.POST = {}


class TaskManager(models.Manager):
    def get_current(self, user):
        if self.filter(day=datetime.datetime.today().weekday()).exclude(started_at=datetime.datetime.now()).count() > 0:
            for t in self.filter(day=datetime.datetime.today().weekday()):
                ta = TaskArchive()
                ta.task = t
                ta.done = t.done
                ta.save()

                t.done = False
                t.started_at = datetime.date.today()
                t.save()

        days = [datetime.date.today().weekday(),
                (datetime.datetime.now() + datetime.timedelta(days=-1)).date().weekday()]
        return self.filter(user=user, day__in=days, done=False).order_by('-started_at', 'priority')


class Task(models.Model):
    # user_id = models.IntegerField()
    user = models.ForeignKey(User)
    task = models.CharField(max_length=255, default='')
    source = models.CharField(max_length=10)
    comment = models.CharField(max_length=255, default='')
    run_at = models.DateTimeField(default=str(datetime.datetime.now()))
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TaskManager()

    class Meta:
        db_table = 'task'
        verbose_name = 'Task'

    def __unicode__(self):
        return 'UID:%s TASK:%s @ %s' % (str(self.user_id), str(self.task), str(self.run_at))


FB_MESSAGE_STATUS = (
    (0, 'Explanation'),
    (1, 'Error'),
    (2, 'Success'),
)


class MessageManager(models.Manager):
    def get_and_delete_all(self, uid):
        messages = []
        for m in self.filter(uid=uid):
            messages.append(m)
            m.delete()
        return messages


class Message(models.Model):
    """Represents a message for a Facebook user."""
    uid = models.CharField(max_length=25)
    status = models.IntegerField(choices=FB_MESSAGE_STATUS)
    message = models.CharField(max_length=300)
    objects = MessageManager()

    class Meta:
        db_table = 'django_message'

    def __unicode__(self):
        return self.message

    def _fb_tag(self):
        return self.get_status_display().lower()

    def as_fbml(self):
        return mark_safe(u'<fb:%s message="%s" />' % (
            self._fb_tag(),
            escape(self.message),
        ))


class MailManager(models.Manager):
    def get_unsent(self):
        return self.filter(is_send=False)


class Mail(models.Model):
    user = models.ForeignKey(User)
    sender = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    content = models.TextField()

    is_send = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MailManager()

    class Meta:
        db_table = 'user_mail'

    def __unicode__(self):
        return "email from %s to %s with subj: %s" % (self.sender, self.receiver, self.subject)

    def send(self, user, subject, template, replacements):
        from django.template import loader, Context
        from userprofile.models import UserProfile

        profile = UserProfile.objects.get_by_user(user=user)

        t = loader.get_template('mail/%s' % template)
        c = Context(replacements)

        self.user = user
        self.sender = settings.DEFAULT_FROM_EMAIL
        self.receiver = user.email
        self.subject = subject
        self.content = t.render(c)
        self.save()


class CarManager(models.Manager):
    def filter_with_params(self, params):

        def query(query, one=True):
            from django.db import connection

            cursor = connection.cursor()
            c = cursor.execute(query)
            if one:
                try:
                    return cursor.fetchone()[0]
                except:
                    return None
            return cursor.fetchall()

        gta = self.all()

        arr = {}
        for k, v in params.iteritems():
            if len(v) > 0:
                arr[k] = v

        if arr.has_key('tier'):
            arr['tier'] = params.getlist('tier')

        if arr.has_key('manuf'): gta = gta.filter(manuf__icontains=arr['manuf'])
        if arr.has_key('model'): gta = gta.filter(model__icontains=arr['model'])
        if arr.has_key('engine'): gta = gta.filter(engine_up=str(float(arr['engine'])))

        if arr.has_key('bhp_from'): gta = gta.filter(power_bhp__gte=str(float(arr['bhp_from'])))
        if arr.has_key('bhp_to'): gta = gta.filter(power_bhp__lte=str(float(arr['bhp_to'])))
        if arr.has_key('year_from'): gta = gta.filter(year__gte=arr['year_from'])
        if arr.has_key('year_to'): gta = gta.filter(year__lte=arr['year_to'])
        if arr.has_key('sprint_from'): gta = gta.filter(sprint_0_100__gte=str(float(arr['sprint_from'])))
        if arr.has_key('sprint_to'): gta = gta.filter(sprint_0_100__lte=str(float(arr['sprint_to'])))
        if arr.has_key('pw_from'): gta = gta.filter(power_to_weight__gte=str(float(arr['pw_from'])))
        if arr.has_key('pw_to'): gta = gta.filter(power_to_weight__lte=str(float(arr['pw_to'])))
        if arr.has_key('weight_from'): gta = gta.filter(weight__gte=arr['weight_from'])
        if arr.has_key('weight_to'): gta = gta.filter(weight__lte=arr['weight_to'])
        if arr.has_key('max_from'): gta = gta.filter(top_speed__gte=arr['max_from'])
        if arr.has_key('max_to'): gta = gta.filter(top_speed__lte=arr['max_to'])
        if arr.has_key('drive'): gta = gta.filter(drive__iexact=arr['drive'])
        if arr.has_key('doors'): gta = gta.filter(doors=arr['doors'])
        if arr.has_key('source'): gta = gta.filter(source=arr['source'])
        if arr.has_key('no_img'): gta = gta.filter(img__iexact='')
        if arr.has_key('with_img'):    gta = gta.exclude(img__exact='')
        if arr.has_key('tier'): gta = gta.filter(tier__in=arr['tier'])
        if arr.has_key('country'): gta = gta.filter(country__iexact=arr['country'])

        if arr.has_key('in_crimecorp'): gta = gta.filter(in_crimecorp=True, is_active_in_crimecorp=True)
        if arr.has_key('in_battle'): gta = gta.filter(in_battle=True, is_active_in_battle=True)
        if arr.has_key('in_mobile'): gta = gta.filter(in_mobile=True, is_active_in_mobile=True)
        if arr.has_key('in_idealer'): gta = gta.filter(in_idealer=True, is_active_in_idealer=True)
        if arr.has_key('not_in_crimecorp'): gta = gta.filter(in_crimecorp=False)
        if arr.has_key('not_in_battle'): gta = gta.filter(in_battle=False)
        if arr.has_key('not_in_mobile'): gta = gta.filter(in_mobile=False)
        if arr.has_key('not_in_idelaer'): gta = gta.filter(in_idealer=False)
        if arr.has_key('is_confirmed'): gta = gta.filter(is_confirmed=True)
        if arr.has_key('is_not_confirmed'): gta = gta.filter(is_confirmed=False)
        if arr.has_key('is_not_active'):
            gta = gta.filter(is_active=False)
        else:
            gta = gta.filter(is_active=True)

        if arr.has_key('in_albums'):
            cars = []
            for car in query('SELECT car FROM garage.album WHERE car!=""', False):
                cars.extend(car[0].split(','))
            gta = gta.filter(id__in=list(set(cars)))

        return gta

    def get_by_id(self, item_id):
        key = 'car_%s' % str(item_id)

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            item = self.get(pk=item_id)
        except Car.DoesNotExist:
            return None

        cache.set(key, pickle.dumps(item))
        return item

    def get_list(self, item_list):
        # TODO: z czasem pomyslec o optymalizacji, poki co starczy
        items = []

        for item in item_list:
            items.append(self.get_by_id(item))

        return items

    def get_dict(self, item_list):
        items = {}

        for k, v in item_list.iteritems():
            if not isinstance(item_list[k], basestring):
                if not items.has_key(k): items[k] = []
                items[k].append(self.get_by_id(v))
            else:
                items[k] = self.get_by_id(v)

        return items

    def draw_cars(self, profile=None, all_tiers=True):
        drawed = {}
        pref_manuf = ''

        car_tiers = settings.CAR_GROUPS
        if not all_tiers:
            car_tiers = settings.CAR_GROUPS[:6]

        for tier_id, tier_name in car_tiers:
            cars = Car.objects.values_list('id', 'chance').filter(tier=tier_id, chance__gt=0, is_active=True,
                                                                  is_active_in_battle=True, in_battle=True)

            # pref manuf only if has cars like this in db and then cleanup
            if len(pref_manuf) == 0:
                pref_manuf = profile.pref_manuf
                profile.pref_manuf = ''
            # profile.save()
            if profile is not None and len(pref_manuf) > 0:
                test = cars.filter(manuf=pref_manuf)
                if test.count() > 0:
                    jobs = test

            # combine chances for all matched vehicles
            chances = []
            for car_id, car_chance in cars:
                [chances.append(car_id) for i in xrange(0, (car_chance * 1000))]

            if len(chances) == 0:
                logging.debug('Could not draw any car for %s / %s' % (tier_name, profile.user))
                continue

            drawed[str(tier_id)] = str(random.choice(chances))

        return self.get_dict(drawed)

    def get_manuf_dict(self):
        cars = cache.get('manuf_dict')
        if cars is not None:
            return cars

        cars = {}
        [cars.update({slughifi(manuf): manuf}) for manuf in
         self.filter(is_active=True, is_active_in_battle=True, in_battle=True).values_list('manuf',
                                                                                           flat=True).distinct()]
        cache.set('manuf_dict', cars)
        return cars

    def get_manuf_list(self):
        cars = cache.get('manuf_list')
        if cars is not None:
            return cars

        cars = [[manuf, slughifi(manuf)] for manuf in
                self.filter(is_active=True, is_active_in_battle=True, in_battle=True).values_list('manuf',
                                                                                                  flat=True).order_by(
                    'manuf').distinct()]
        cache.set('manuf_list', cars)
        return cars

    def get_by_manuf(self, manuf=None, manuf_url=None):
        if manuf_url is not None:
            try:
                manuf = self.get_manuf_dict()[manuf]
            except KeyError:
                return None

        # cars = cache.get('cars_by_manuf_%s' % manuf)
        # if cars is not None:
        # 	return cars

        cars = self.filter(is_active=True, is_active_in_battle=True, in_battle=True, manuf=manuf).order_by('year',
                                                                                                           'name',
                                                                                                           'power_bhp')

        # cache.set('cars_by_manuf_%s' % manuf, cars)
        return cars


class Car(models.Model):
    manuf = models.CharField(max_length=50)
    tuner = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=25)
    tier = models.CharField(max_length=1, default='1')
    country = models.CharField(max_length=30)
    desc = models.CharField(max_length=255)

    year = models.PositiveSmallIntegerField()
    engine = models.PositiveSmallIntegerField(default=0)
    engine_up = models.CharField(max_length=30)
    engine_location = models.CharField(max_length=10)
    drive = models.CharField(max_length=3)
    doors = models.PositiveSmallIntegerField(default=0)
    type = models.CharField(max_length=100, default='')
    group = models.CharField(max_length=100)

    cylinders = models.CharField(max_length=4, default='')
    power_bhp = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    power_kw = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    power_rpm = models.PositiveSmallIntegerField(default=0)
    torque_nm = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    torque_rpm = models.PositiveSmallIntegerField(default=0)
    power_to_weight = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    weight = models.PositiveSmallIntegerField(default=0)
    weight_unit = models.CharField(max_length=3, default='kg')
    size_unit = models.CharField(max_length=3, default='mm')
    length = models.PositiveSmallIntegerField(default=0)
    height = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)

    top_speed = models.PositiveSmallIntegerField(default=0)
    top_speed_unit = models.CharField(max_length=4, default='km/h')
    sprint_0_80 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    sprint_0_100 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    sprint_0_180 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    sprint_0_200 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    sprint_0_100_0 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    sprint_0_200_0 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    break_100_0 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    break_180_0 = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    break_200_0 = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    co2 = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    co2_unit = models.CharField(max_length=8, default='g/km')
    fuel_min = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    fuel_avg = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    fuel_max = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    fuel_cap = models.PositiveSmallIntegerField(default=0)

    url = models.URLField()
    source = models.CharField(max_length=20)
    source_id = models.CharField(max_length=20)
    img = models.URLField()
    img_org = models.URLField()
    chance = models.DecimalField(max_digits=5, decimal_places=4, default="0.1")
    to_refresh = models.BooleanField(default=False)
    in_crimecorp = models.BooleanField(default=False)
    in_battle = models.BooleanField(default=False)
    in_garage = models.BooleanField(default=False)
    in_mobile = models.BooleanField(default=False)
    in_idealer = models.BooleanField(default=False)
    is_active_in_crimecorp = models.BooleanField(default=True)
    is_active_in_battle = models.BooleanField(default=True)
    is_active_in_garage = models.BooleanField(default=True)
    is_active_in_mobile = models.BooleanField(default=True)
    is_active_in_idealer = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_confirmed = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CarManager()

    class Meta:
        db_table = 'car'
        verbose_name = 'Car'

    def __unicode__(self):
        return "Car %s %s" % (self.manuf, self.name)

    def display_name(self):
        return "%s %s %s" % (self.year, self.manuf, self.name)

    def display_short_name(self):
        return "%s %s %s" % (self.year, self.manuf, self.short_name)

    def if_won(self, card, params):
        """
        Car Battle
        Sprawdza czy biezaca karta wygrala z podana w parametrze na podstawie listy parametrow
        """

        positive = ('engine', 'power_bhp', 'top_speed', 'power_to_weight')
        negative = ('year', 'weight', 'sprint_0_100')

        score = 0
        for param in params:
            if self.__dict__[param] > card.__dict__[param]:
                # print param, self.__dict__[param], '>', card.__dict__[param]
                s = 1
            elif self.__dict__[param] < card.__dict__[param]:
                # print param, self.__dict__[param], '<', card.__dict__[param]
                s = -1
            else:
                s = 0
            # print param, self.__dict__[param], '=', card.__dict__[param]

            if param in negative: s = s * -1
            score += s

        return score


class CarDetailManager(models.Manager):
    pass


class CarDetail(models.Model):
    car = models.ForeignKey(Car)
    attr = models.TextField()

    objects = CarDetailManager()

    class Meta:
        db_table = 'car_detail'
        verbose_name = 'Car Detail'

    def __unicode__(self):
        return "Details of Car %s %s" % (self.car.manuf, self.car.name)


class CarPhotoManager(models.Manager):
    pass


class CarPhoto(models.Model):
    car = models.ForeignKey(Car)
    url = models.URLField()
    img = models.CharField(max_length=255)

    class Meta:
        db_table = 'car_photo'

    def __unicode__(self):
        return "Car's: %s photo (%s)" % (self.car, self.url)


class CarWikiManager(models.Manager):
    pass


class CarWiki(models.Model):
    car = models.ForeignKey(Car)
    content = models.TextField()

    objects = CarWikiManager()

    class Meta:
        db_table = 'car_wiki'
        verbose_name = 'Car Wiki'
        verbose_name_plural = 'Cars Wiki'

    def __unicode__(self):
        return "Wiki of Car %s %s" % (self.car.manuf, self.car.name)
