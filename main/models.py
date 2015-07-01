# -*- coding: utf-8 -*-
from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User

import datetime
import cPickle as pickle


class PaymentManager(models.Manager):
    pass


class Payment(models.Model):
    user_id = models.IntegerField()
    site = models.CharField(max_length=10)
    provider = models.CharField(max_length=20)
    details = models.CharField(max_length=255)
    credits = models.PositiveIntegerField()
    total_credits = models.PositiveIntegerField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PaymentManager()

    class Meta:
        db_table = 'payment'
        verbose_name = 'Payment'

    def __unicode__(self):
        return 'UID:%s CREDITS:%s @ %s' % (str(self.user_id), str(self.credits), str(self.created_at))


class PaymentCountryManager(models.Manager):
    pass


class PaymentCountry(models.Model):
    country_id = models.IntegerField()
    # general
    is_srpoints = models.BooleanField(default=True)
    is_paypal = models.BooleanField(default=True)

    is_peanut = models.BooleanField(default=False)
    is_platnosci = models.BooleanField(default=False)

    # sms
    is_webtopay = models.BooleanField(default=False)
    is_furtumo = models.BooleanField(default=False)
    is_paymo = models.BooleanField(default=False)

    objects = PaymentCountryManager()

    class Meta:
        db_table = 'payment_country'
        verbose_name = 'Payment Country'
        verbose_name_plural = 'Payment Countries'

    def __unicode__(self):
        return 'Payments for country: %s' % self.country_id


class PaymentCodeManager(models.Manager):
    def check_code(self, code):
        try:
            return self.get(code=code)
        except PaymentCode.DoesNotExist:
            return None

    def gen_new_code(self, value=0):
        import hashlib

        sha = hashlib.sha1()
        sha.update(str(datetime.datetime.now()))
        sha_code = sha.hexdigest()

        start = 0
        while True:
            try:
                code = sha_code[start:start + 6]

                self.get(code=code)
                start += 1
                continue
            except PaymentCode.DoesNotExist:
                pc = PaymentCode()
                pc.code = code
                pc.value = value
                pc.save()

                return code


class PaymentCode(models.Model):
    code = models.CharField(max_length=6)
    value = models.CharField(max_length=100)

    used_by = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    codes = PaymentCodeManager()

    class Meta:
        db_table = 'payment_code'
        verbose_name = 'Payment Code'

    def __unicode__(self):
        return '%s @ %s' % (str(self.code), str(self.created_at))


class PaymentPromoCodeManager(models.Manager):
    def check_code(self, code):
        try:
            return self.get(code=code)
        except PaymentCode.DoesNotExist:
            return None


class PaymentPromoCode(models.Model):
    code = models.CharField(max_length=20)
    value = models.IntegerField()

    used_by = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(default=datetime.datetime.now())

    objects = PaymentPromoCodeManager()

    class Meta:
        db_table = 'payment_promo_code'
        verbose_name = 'Payment Promo Code'

    def __unicode__(self):
        return '%s @ %s' % (str(self.code), str(self.created_at))


class UserFBSpamManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):
        if user is not None:
            key = 'user_fb_spam_%s' % user.id
        elif user_id is not None:
            key = 'user_fb_spam_%s' % user_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if user is not None:
                item = self.get(user=user)
            elif user_id is not None:
                item = self.get(user__id=user_id)
            else:
                logging.warning('facebook_spam not found. USER:%s, ID:%s' % (str(user), str(user_id)))
                return None

        except UserFBSpam.DoesNotExist:
            fb = UserFBSpam()
            fb.user = user
            fb.save()
            item = fb

        cache.set(key, pickle.dumps(item))
        return item


class UserFBSpam(models.Model):
    user = models.ForeignKey(User)
    next_queue_at = models.DateTimeField(default=datetime.datetime.now())

    sent = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserFBSpamManager()

    class Meta:
        db_table = 'facebook_spam'
        verbose_name = 'Facebook Spam'

    def __unicode__(self):
        return '%s\' facebook spam' % self.user

    def save(self):
        super(UserFBSpam, self).save()  # Call the "real" save() method
        key = 'user_fb_spam_%s' % self.user.id
        cache.set(key, pickle.dumps(self))


class UserFBSpamLog(models.Model):
    user_id = models.IntegerField()
    type = models.CharField(max_length=25)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facebook_spam_log'
        verbose_name = 'Facebook Spam Log'

    def __unicode__(self):
        return '%s: %s > %s' % (self.user_id, self.type, self.message)


class FBCacheManager(models.Manager):
    def get_by_page(self, user, page):
        return self.filter(user=user, page=page)


class FBCache(models.Model):
    user = models.ForeignKey(User)
    handler = models.CharField(max_length=255)
    url = models.URLField()

    page = models.CharField(max_length=255)
    to_refresh = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FBCacheManager()

    class Meta:
        db_table = 'facebook_cache'
        verbose_name = 'Facebook Cache'

    def __unicode__(self):
        return '%s: cache of %s, %s (to refresh: %s)' % (self.user_id, self.handler, self.url, self.to_refresh)


class NewsManager(models.Manager):
    def get_latest(self, lang='en', limit=3):
        key = 'news_%s' % lang

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            item = self.filter(lang=lang).order_by('-created_at')[:limit]
        except News.DoesNotExist:
            return None

        cache.set(key, pickle.dumps(item))
        return item


class News(models.Model):
    source = models.CharField(max_length=20)
    lang = models.CharField(max_length=2)

    title = models.CharField(max_length=100)
    content_short = models.CharField(max_length=255)
    content = models.TextField()
    img = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = NewsManager()

    class Meta:
        db_table = 'news'
        verbose_name = 'News'

    def save(self):
        super(News, self).save()  # Call the "real" save() method
        cache.delete('news_%s' % self.lang)

    def __unicode__(self):
        return '%s @ %s' % (str(self.title), str(self.created_at))

    def __getattr__(self, name):
        if name == 'imgs':
            if not self.img: return []
            return self.img.split(',')
        return self.__getattribute__(name)


class UserStreamManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):
        return self.filter(user=user)

    def get_by_friend(self, user=None, user_id=None):
        from friend.models import Friend

        friends = Friend.objects.get_by_user(user=user, user_id=user_id).friends
        friends.append(user.id)
        return self.filter(user__id__in=friends)

    def get_latest(self, user=None, user_id=None, limit=10):
        return self.get_by_user(user, user_id).order_by('-created_at')[:limit]

    def get_latest_public(self, user=None, user_id=None, limit=10):
        return self.get_by_user(user, user_id).filter(is_private=False).order_by('-created_at')[:limit]

    def get_latest_wall_to_wall(self, user=None, user_id=None, limit=10):
        return self.get_by_user(user, user_id).filter(sender_id__gt=0).order_by('-created_at')[:limit]

    def get_friend_wall(self, user=None, user_id=None, limit=10):
        return self.get_by_friend(user=user, user_id=user_id).order_by('-created_at')[:limit]

    def get_friend_wall_public(self, user=None, user_id=None, limit=10):
        return self.get_by_friend(user=user, user_id=user_id).filter(is_private=False).order_by('-created_at')[:limit]


class UserStream(models.Model):
    user = models.ForeignKey(User)
    sender_id = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=20)
    key = models.CharField(max_length=20)
    content = models.CharField(max_length=255)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserStreamManager()

    class Meta:
        db_table = 'user_stream'
        verbose_name = 'User Stream'

    def save(self):
        super(UserStream, self).save()  # Call the "real" save() method
        cache.delete('user_stream_%s' % self.user.id)

    def __unicode__(self):
        return '%s: %s @ %s' % (str(self.user), str(self.content), str(self.created_at))

    def template_name(self):
        # print 'partials/wall/%s,%s.html' % (self.type, self.key or '')
        return 'partials/wall/%s,%s.html' % (self.type, self.key or '')

    def __getattr__(self, name):
        if name == 'contents':
            return self.content.split('|')
        else:
            return self.__getattribute__(name)


class CountryManager(models.Manager):
    def get_all(self):
        key = 'countries'
        items = cache.get(key)

        if items is not None:
            return pickle.loads(str(items))

        try:
            items = self.all().order_by('name_en')
        except Country.DoesNotExist:
            return None

        cache.set(key, pickle.dumps(items))
        return items


class Country(models.Model):
    code = models.CharField(max_length=2)
    name_en = models.CharField(max_length=100)
    name_en_url = models.CharField(max_length=100)
    name_pl = models.CharField(max_length=100)
    name_pl_url = models.CharField(max_length=100)

    objects = CountryManager()

    class Meta:
        db_table = 'country'
        verbose_name = 'country'
        verbose_name_plural = 'countries'

    def __unicode__(self): return self.name_en
