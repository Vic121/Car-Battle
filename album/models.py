from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User

import datetime
import cPickle as pickle

# from userprofile.models import UserProfile
# from common.models import Car

class AlbumManager(models.Manager):
    def get_by_id(self, item_id):
        key = 'album_%s' % str(item_id)

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            item = self.get(pk=item_id, is_active=True, is_locked=True)
        except Album.DoesNotExist:
            return None

        cache.set(key, pickle.dumps(item))
        return item

    def get_latest(self, limit=5):
        return self.filter(is_active=True, is_locked=True, is_hidden=False).order_by('-created_at')[:limit]


class Album(models.Model):
    name = models.CharField(max_length=40)
    short_name = models.CharField(max_length=25)
    desc = models.CharField(max_length=255)
    car = models.CharField(max_length=255)
    exp = models.PositiveIntegerField(default=0)

    min_lvl = models.PositiveSmallIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    search = models.CharField(max_length=255)
    credits = models.TextField()
    hidden_info = models.CharField(max_length=255)

    is_hidden = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AlbumManager()

    class Meta:
        db_table = 'album'
        verbose_name = 'Album'

    def __unicode__(self):
        return 'Album %s' % str(self.id)

    def __len__(self):
        return len(self.cars)

    def __getattr__(self, name):
        if name == 'cars':
            if not self.car: return []
            return self.car.split(',')
        return self.__getattribute__(name)

    def save(self):
        super(Album, self).save()
        key = 'album_%s' % (self.pk)
        cache.set(key, pickle.dumps(self))

    def delete(self):
        k = self.pk
        super(Album, self).delete()
        cache.delete('album_%s' % (k))

    # ---

    def add_car(self, car_id):
        c = self.cars
        if str(car_id) in c:
            return False
        c.append(str(car_id))
        self.car = ','.join(c)
        self.save()
        return True

    def remove_car(self, car_id):
        c = self.cars
        try:
            del c[c.index(str(car_id))]
        except ValueError:
            return False

        self.car = ','.join(c)
        self.save()
        return True


class UserAlbumManager(models.Manager):
    def get_by_id(self, item_id):
        key = 'user_album_%s' % str(item_id)

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            item = self.get(pk=item_id)
        except UserAlbum.DoesNotExist:
            return None

        cache.set(key, pickle.dumps(item))
        return item

    def get_by_user(self, user=None, user_id=None):
        if user is not None:
            key = 'user_albums_%s' % user.id
        elif user_id is not None:
            key = 'user_albums_%s' % user_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if user is not None:
                item = self.filter(user=user, is_active=True)
            elif user_id is not None:
                item = self.filter(user__id=user_id, is_active=True)

        except UserAlbum.DoesNotExist:
            item = []

        # cache.set(key, pickle.dumps(list(item)))
        return item


class UserAlbum(models.Model):
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album)

    car = models.CharField(max_length=255)
    left = models.PositiveSmallIntegerField(default=0)
    total = models.PositiveSmallIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserAlbumManager()

    class Meta:
        db_table = 'user_album'
        verbose_name = 'User\'s Album'

    def __unicode__(self):
        return '%s\'s Album' % self.user

    def __len__(self):
        return len(self.cars)

    def __getattr__(self, name):
        if name == 'cars':
            if not self.car: return []
            return self.car.split(',')
        return self.__getattribute__(name)

    def save(self):
        self.left = self.total - len(self)

        super(UserAlbum, self).save()
        key = 'user_album_%s' % (self.pk)
        # cache.set(key, pickle.dumps(self))
        cache.delete('user_albums_%s' % (self.user.id))

    def delete(self):
        k, u = int(self.pk), int(self.user.id)
        super(UserAlbum, self).delete()
        cache.delete('user_album_%s' % (k))
        cache.delete('user_albums_%s' % (u))

    # ---

    def stick_card(self, card_id):
        if str(card_id) in self.cars:
            return False

        cars = self.cars
        cars.append(str(card_id))
        self.car = ','.join(cars)
        self.left -= 1
        self.save()
        return True


class AlbumStatManager(models.Manager):
    def get_by_album(self, album=None, album_id=None):
        if album is not None:
            key = 'album_stat_%s' % album.id
        elif album_id is not None:
            key = 'album_stat_%s' % album_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if album is not None:
                item = self.get(album=album)
            elif album_id is not None:
                item = self.get(album__id=album_id)

        except AlbumStat.DoesNotExist:
            item = AlbumStat()
            if album:
                item.album = album
            elif album_id:
                item.album = Album.objects.get(pk=album_id)
            item.save()

        cache.set(key, pickle.dumps(item))
        return item


class AlbumStat(models.Model):
    album = models.ForeignKey(Album, unique=True)
    got = models.PositiveIntegerField(default=0)
    non_zero_got = models.PositiveIntegerField(default=0)
    filled = models.PositiveIntegerField(default=0)
    avg_fill = models.DecimalField(max_digits=5, decimal_places=2)

    last_did = models.PositiveIntegerField(default=0)
    last_did_at = models.DateTimeField(default=datetime.datetime.now())
    last_started = models.PositiveIntegerField(default=0)
    last_started_at = models.DateTimeField(default=datetime.datetime.now())

    objects = AlbumStatManager()

    class Meta:
        db_table = 'album_stat'
        verbose_name = 'Album Stat'

    def __unicode__(self):
        return 'stats of album_id:%d' % self.pk

    def save(self):
        self.avg_fill = self.filled / self.non_zero_got

        super(AlbumStat, self).save()
        cache.delete('album_stat_%s' % self.album.id)

    def delete(self):
        aid = self.album.id
        super(AlbumStat, self).delete()
        cache.delete('album_stat_%s' % aid)


class AlbumStatUserManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):
        if user is not None:
            key = 'album_stat_user_%s' % user.id
        elif user_id is not None:
            key = 'album_stat_user_%s' % user_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if user is not None:
                item = self.get(user=user)
            elif user_id is not None:
                item = self.get(user__id=user_id)

        except AlbumStatUser.DoesNotExist:
            item = AlbumStatUser()
            if user:
                item.user = user
            elif user_id:
                item.user = User.objects.get(pk=user_id)
            item.save()

        cache.set(key, pickle.dumps(item))
        return item


class AlbumStatUser(models.Model):
    user = models.ForeignKey(User)
    username = models.CharField(max_length=50)
    got = models.PositiveIntegerField(default=0)
    non_zero_got = models.PositiveIntegerField(default=0)
    filled = models.PositiveIntegerField(default=0)
    avg_fill = models.DecimalField(max_digits=5, decimal_places=2)

    last_filled_id = models.PositiveIntegerField()
    last_filled_at = models.DateTimeField(default=datetime.datetime.now())
    last_got_id = models.PositiveIntegerField()
    last_got_at = models.DateTimeField(default=datetime.datetime.now())

    objects = AlbumStatUserManager()

    class Meta:
        db_table = 'album_stat_user'
        verbose_name = 'User\'s Album Stat'

    def __unicode__(self):
        return 'stats of album of user:%d' % self.pk

    def save(self):
        self.avg_fill = self.filled / self.non_zero_got

        super(AlbumStatUser, self).save()
        cache.delete('album_stat_user_%s' % self.user.id)

    def delete(self):
        uid = self.user.id
        super(AlbumStatUser, self).delete()
        cache.delete('album_stat_user_%s' % uid)
