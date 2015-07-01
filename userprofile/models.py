# -*- coding: UTF-8
# import logging
import hashlib
import random
import os

import simplejson as json
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import datetime
import cPickle as pickle


class UserProfileManager(models.Manager):
    # def get_by_id(self, user_id):
    #	key = 'user_%s' % user_id
    #	profile = cache.get(key)
    #
    #	if profile is not None:
    #		return pickle.loads(str(profile))
    #
    #	try:
    #		profile = self.get(user__id=user_id)
    #	except UserProfile.DoesNotExist:
    #		logging.warning('Profile not found. ID:%s' % str(user_id))
    #		return None
    #
    #	cache.set(key, pickle.dumps(profile))
    #	return profile

    def get_by_user(self, user_id=None, user=None, partner_login=None):
        return self.get_by_id(user_id, user, partner_login)

    def get_by_id(self, user_id=None, user=None, partner_login=None):
        if user_id is not None:
            key = 'user_%s' % user_id
        elif user is not None:
            key = 'user_%s' % user.id
        elif partner_login is not None:
            key = 'user_login_%s' % partner_login

            item = cache.get(key)
            if item is not None:
                return pickle.loads(str(item))
        else:
            key = None

        try:
            if user_id is not None:
                item = self.get(user__id=user_id)
            elif user is not None:
                item = self.get(user=user)
            elif partner_login is not None:
                item = self.get(partner_login=partner_login)
            else:
                logging.warning('UserProfile not found with both None parameters.')
                return None

        except UserProfile.DoesNotExist:
            logging.warning('UserProfile not found. ID:%s USER:%s' % (str(user_id), user))
            return None

        cache.set(key or 'user_%s' % item.user.id, pickle.dumps(item))
        return item

    def get_many_by_user_ids(self, user_ids):
        ret = []
        for uid in user_ids:
            ret.append(self.get_by_id(uid))
        return ret

    def get_by_fb_id(self, fb_id):
        key = 'fb_id_to_user_%s' % fb_id
        user_id = cache.get(key)

        if user_id is not None:
            return self.get_by_id(user_id)

        try:
            profile = self.get(fb_id=fb_id)
        except UserProfile.DoesNotExist:
            logging.warning('Profile not found. FB_ID:%s' % str(fb_id))
            return None

        cache.set(key, profile.user.id)
        return profile

    def get_many_by_fb_ids(self, fb_ids):
        ret = []
        for fb_id in fb_ids:
            by_fb = self.get_by_fb_id(fb_id)
            if by_fb is not None:
                ret.append(by_fb)
            else:
                by_id = self.get_by_id(fb_id)
                if by_id is not None:
                    ret.append(by_id)
                else:
                    raise AttributeError

        return ret

    def get_by_invite_key(self, inv_key):
        if len(str(inv_key)) != 16: return None

        try:
            return self.get(invite_key__iexact=inv_key)
        except UserProfile.DoesNotExist:
            return None

    def get_leaderboard(self, limit=10):
        # TODO: add caching
        # key = 'leaderboard_%d' % limit
        # items = cache.get(key)

        return self.filter(is_active=True).only('username', 'level', 'exp').order_by('-exp')[:limit]


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name='User')
    fb_id = models.IntegerField(default=0)
    invite_key = models.CharField(max_length=16)
    username = models.CharField(max_length=20)
    username_color = models.CharField(max_length=150)
    pref_manuf = models.CharField(max_length=25)
    partner = models.CharField(max_length=20)
    partner_login = models.CharField(max_length=20)
    status = models.CharField(max_length=10, default='new')
    domain = models.CharField(max_length=50, default='www.car-battle.com')

    energy = models.PositiveIntegerField(default=settings.DEFAULT_STATS['energy'])
    level = models.PositiveIntegerField(default=settings.DEFAULT_STATS['level'])
    exp = models.PositiveIntegerField(default=settings.DEFAULT_STATS['exp'])
    cars = models.PositiveIntegerField(default=0)
    prev_level_exp = models.PositiveIntegerField(default=settings.DEFAULT_STATS['prev_level_exp'])
    next_level_exp = models.PositiveIntegerField(default=settings.DEFAULT_STATS['next_level_exp'])

    cash = models.IntegerField(default=settings.DEFAULT_STATS['cash'])
    cash_in_bank = models.IntegerField(default=0)
    credit = models.IntegerField(default=settings.DEFAULT_STATS['credits'])

    job_id = models.PositiveIntegerField(default=0)
    job_round = models.PositiveSmallIntegerField(default=1)
    job_tier = models.PositiveSmallIntegerField(default=1)
    job_max_round = models.PositiveSmallIntegerField(default=settings.MAX_ROUNDS_A_DAY)
    job_max_round_today = models.PositiveSmallIntegerField(default=settings.MAX_ROUNDS_A_DAY)
    job_next_day_at = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(days=1))

    friends = models.IntegerField(default=0)
    daily_income = models.IntegerField(default=0)
    daily_outcome = models.IntegerField(default=0)
    last_msg_id = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_spammer = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_premium_until = models.DateTimeField(default=datetime.datetime.now())
    next_energy_at = models.DateTimeField(auto_now_add=True)
    how_to_play = models.CharField(max_length=255)
    notify = models.CharField(max_length=7, default='1111111')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserProfileManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'

    def __unicode__(self):
        return str(self.username)

    def __getattr__(self, name):
        if name == 'login_link':
            h = hashlib.md5()
            h.update(self.invite_key + settings.SECRET_KEY)
            return 'profile/edit/%s/%s/' % (self.invite_key, h.hexdigest()[:16])
        return self.__getattribute__(name)

    def save(self, force_insert=False):
        if self.id is None: self.__just_created()

        try:
            super(UserProfile, self).save(force_insert=force_insert)
        except Exception, e:
            logging.error('Error saving profile %s' % e)
        key = 'user_%s' % self.user.id
        cache.set(key, pickle.dumps(self))

    def delete(self):
        cache.delete('user_%s' % self.user.id)
        super(UserProfile, self).delete()

    # -- Methods

    def __just_created(self):
        h = hashlib.sha1()
        h.update(str(random.random()))
        salt = h.hexdigest()[:5]

        h = hashlib.sha1()
        h.update(salt + self.user.username)

        self.invite_key = h.hexdigest()
        self.username = self.user.username
        self.username_color = self.username

        # domyslny znajomy
        from friend.models import Friend

        f = Friend.objects.get_by_user(user=self.user)
        f.add_friend(settings.DEFAULT_FRIEND)

        # domyslny avatar
        from shutil import copyfile

        path = settings.MEDIA_ROOT + 'avatars/' + str(self.user_id / 1000)
        if not os.path.isdir(path):
            os.makedirs(path)
        copyfile(settings.MEDIA_ROOT + 'avatars/0.jpg', path + '/' + str(self.user_id) + '.jpg')

    def avatar(self):
        return 'avatars/%s/%s.jpg' % (str(self.user_id / 1000), str(self.user_id))

    def has_enough(self, type, num):
        """Czy user ma wystarczajaca ilosc danych obiektow"""
        if type in ('credit', 'cash'):
            try:
                if int(self.__dict__[type]) >= int(num):
                    return True
                else:
                    return False
            except KeyError:
                logging.error('No attribute type: %s' % type)
                return False

        else:
            logging.error('Unsupported type: %s' % type)
            raise NotImplementedError

    def spend(self, type, num, autosave=True):
        """Usuwa obiekty z profilu"""
        if type in ('credit', 'cash'):
            try:
                logging.info('%s just spent %s %s' % (self, num, type))
                try:
                    self.__dict__[type] -= int(num)
                    if hasattr(self, 'engine'):
                        self.engine.notify.add(user=self.user, type=type, key='spend', value=int(num), date=None)
                    else:
                        UserStat.objects.increment(user=self.user, type=type, key='spend', value=int(num), date=None)
                except TypeError:
                    logging.error('Blad przy przypisywaniu wartosci')
                    return False

                if autosave:
                    self.save()
                return True

            except KeyError:
                logging.error('No type: %s' % type)
                return False

        logging.error('Unsupported type: %s' % type)
        return False

    def earn(self, type, num, autosave=True, engine=None):
        """Dodaje obiekty do profilu"""
        if type in ('credit', 'cash', 'exp'):
            try:
                logging.info('%s just earned %s %s' % (self, num, type))
                try:
                    self.__dict__[type] += int(num)
                    if hasattr(self, 'engine'):
                        self.engine.notify.add(user=self.user, type=type, key='earn', value=int(num), date='today')
                        self.engine.notify.add(user=self.user, type=type, key='earn', value=int(num), date=None)
                    else:
                        UserStat.objects.increment(user=self.user, type=type, key='earn', value=int(num), date='today')
                        UserStat.objects.increment(user=self.user, type=type, key='earn', value=int(num), date=None)
                except TypeError:
                    logging.error('Blad przy przypisywaniu wartosci')
                    return False

                if type == 'exp' and self.exp >= self.next_level_exp:
                    while self.exp >= self.next_level_exp:
                        p = int(self.next_level_exp)
                        self.next_level_exp = (p * 1.2) + p
                        self.prev_level_exp = p
                        self.level += 1
                        self.energy = settings.DEFAULT_STATS['energy']  # restore energy

                        if engine is not None and hasattr(engine, 'user'): engine.user.on_level_up(self.level)
                        if hasattr(self, 'engine'):
                            self.engine.notify.add(user=self.user, type=type, key='level_up', date='today')
                            self.engine.notify.add(user=self.user, type=type, key='level_up', date=None,
                                                   stream=str(self.level))
                        else:
                            UserStat.objects.increment(user=self.user, type=type, key='level_up', date='today')
                            UserStat.objects.increment(user=self.user, type=type, key='level_up', date=None)

                if autosave:
                    self.save()
                return True

            except KeyError:
                logging.error('No type: %s' % type)
                return False

        logging.error('Unsupported type: %s' % type)
        return False

    def get_list_of_opponents(self, start=0):
        return UserProfile.objects.filter(level__gte=self.level - 3, level__lte=self.level + 3,
                                          cars__gte=settings.REQ_CARDS_IN_BATTLE).exclude(pk=self.pk).exclude(
            status='tier_bot')[start:settings.DEFAULT_OPPONENTS_PER_PAGE]

    def to_bank(self, amount, autosave=True):
        self.cash -= int(amount)
        self.cash_in_bank += int(amount)
        if autosave:
            self.save()

    def from_bank(self, amount, autosave=True):
        self.cash += int(amount)
        self.cash_in_bank -= int(amount)
        if autosave:
            self.save()

    def how_to_play_status(self, position, value=None):
        self.how_to_play = list(self.how_to_play)

        try:
            if not value:
                return self.how_to_play[position]
            else:
                self.how_to_play[position] = str(value)
        except IndexError:
            while (len(self.how_to_play) <= int(position)):
                self.how_to_play.append('0')

        if value:
            self.how_to_play[position] = str(value)
        self.how_to_play = ''.join(self.how_to_play)
        self.save()

        return self.how_to_play[position]

    # ---

    def add_log(self, log_type='', log_type_id=0, log='', ip=''):
        from django.db import connection

        sql = """
			INSERT INTO
				archive.garage_user_log
			VALUES (
				'%s', '%s', '%s', '%s', '%s', '%s'
			)
		""" % (str(self.user.id), log_type, log_type_id, log, datetime.datetime.now(), str(ip))

        cursor = connection.cursor()
        cursor.execute(sql)


class UserStatManager(models.Manager):
    def increment(self, *args, **kwargs):
        return self.__value(kwargs['user'], kwargs['type'], kwargs['key'], value=kwargs.get('value') or 1,
                            date=kwargs.get('date'), action='increment')

    def decrement(self, *args, **kwargs):
        return self.__value(kwargs['user'], kwargs['type'], kwargs['key'], value=kwargs.get('value') or 1,
                            date=kwargs.get('date'), action='decrement')

    def __value(self, user, type, key, value, date=None, action='increment'):
        try:
            if date == 'today':
                stat, c = self.get_or_create(user=user, type=type, key=key, date=datetime.date.today(),
                                             defaults={'user': user, 'type': type, 'key': key,
                                                       'date': datetime.date.today(), 'value': int(value)})
            elif date is not None:
                stat, c = self.get_or_create(user=user, type=type, key=key, date=date,
                                             defaults={'user': user, 'type': type, 'key': key, 'date': date,
                                                       'value': int(value)})
            else:
                stat, c = self.get_or_create(user=user, type=type, key=key, date=datetime.date(1970, 1, 1),
                                             defaults={'user': user, 'type': type, 'key': key, 'value': int(value)})

            if not c:
                if action == 'increment':
                    stat.value = int(stat.value) + int(value)
                elif action == 'decrement':
                    stat.value = int(stat.value) - int(value)
                else:
                    logging.warning('Unknown UserStat.__value action: %s' % action)
                    return None

            stat.save()

            logging.debug('Stat %s. %s, %s=%s.' % (stat.user, stat.type, stat.key, stat.value))
            return stat.value

        except Exception, e:
            logging.error('Error saving stats. %s' % e)


class UserStat(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(max_length=50)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    date = models.DateField()

    objects = UserStatManager()

    class Meta:
        db_table = 'user_stat'
        verbose_name = 'User\'s Stat'

    def __unicode__(self):
        return 'stats of %s' % self.user


class Avatar(models.Model):
    """
    Avatar model
    """
    image = models.ImageField(upload_to="avatars/%Y/%b/%d")
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField()

    class Meta:
        db_table = 'user_avatar'
        unique_together = (('user', 'valid'),)

    def __unicode__(self):
        return _("%s's Avatar") % self.user

    def delete(self):
        base, filename = os.path.split(self.image.path)
        name, extension = os.path.splitext(filename)
        for key in AVATAR_SIZES:
            try:
                logging.debug("deleting cache for" + CACHE_AVATAR + "_" + self.user.username + "_" + str(key))
                delete_cache(CACHE_AVATAR, self.user.username + "_" + str(key))
                os.remove(os.path.join(base, "%s.%s%s" % (name, key, extension)))
            except Exception, e:
                logging.debug("Fatal exception occurred when deleting avatar!")
                logging.debug(e)

        super(Avatar, self).delete()

    def save(self):
        for avatar in Avatar.objects.filter(user=self.user, valid=self.valid).exclude(id=self.id):
            base, filename = os.path.split(avatar.image.path)
            name, extension = os.path.splitext(filename)
            avatar.delete()

        super(Avatar, self).save()


class UserDetailManager(models.Manager):
    pass


class UserDetail(models.Model):
    user = models.ForeignKey(User)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=255)
    pic_small = models.URLField()
    pic_big = models.URLField()
    pic_square = models.URLField()
    pic = models.URLField()
    msn = models.CharField(max_length=100)
    skype = models.CharField(max_length=100)
    jabber = models.CharField(max_length=100)
    gg = models.CharField(max_length=10)
    yahoo = models.CharField(max_length=100)
    icq = models.CharField(max_length=15)
    about = models.CharField(max_length=255)
    affiliations = models.TextField()
    timezone = models.CharField(max_length=50)
    religion = models.CharField(max_length=50)
    birthday = models.CharField(max_length=50)
    birthday_date = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    hometown_location = models.CharField(max_length=255)
    meeting_sex = models.CharField(max_length=255)
    meeting_for = models.CharField(max_length=255)
    relationship_status = models.CharField(max_length=255)
    significant_other_id = models.CharField(max_length=25)
    political = models.CharField(max_length=50)
    current_location = models.CharField(max_length=255)
    activities = models.CharField(max_length=255)
    interests = models.CharField(max_length=255)
    is_app_user = models.BooleanField(default=False)
    music = models.CharField(max_length=255)
    tv = models.CharField(max_length=255)
    movies = models.CharField(max_length=255)
    books = models.CharField(max_length=255)
    quotes = models.CharField(max_length=255)
    hs_info = models.CharField(max_length=255)
    education_history = models.CharField(max_length=255)
    work_history = models.CharField(max_length=255)
    notes_count = models.PositiveIntegerField(default=0)
    wall_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=255)
    online_presence = models.CharField(max_length=25)
    locale = models.CharField(max_length=25)
    profile_url = models.URLField()
    allowed_restrictions = models.CharField(max_length=255)
    verified = models.CharField(max_length=50)
    profile_blurb = models.CharField(max_length=255)
    family = models.TextField()
    is_blocked = models.BooleanField(default=True)

    objects = UserDetailManager()

    class Meta:
        db_table = 'user_detail'

    def __unicode__(self):
        return

    def save_from_fql(self, result):
        for k, v in result.iteritems():
            if self.__dict__.has_key(k):
                if not v: v = ''

                try:
                    if not isinstance(v, basestring):
                        self.__dict__[k] = json.dumps(v)
                    else:
                        self.__dict__[k] = v or 0
                except:
                    logging.warning('Cannot write user details %s/%s' % (str(k), str(v)))
                    continue

        self.save(force_insert=True)
