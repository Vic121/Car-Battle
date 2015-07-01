# -*- coding: utf-8 -*-
# import logging
from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import cPickle as pickle
from common.helpers.slughifi import slughifi
from userprofile.models import UserProfile


class FriendManager(models.Manager):
    def get_by_user(self, user=None, user_id=None):
        if user is not None:
            key = 'friends_%s' % user.id
        elif user_id is not None:
            key = 'friends_%s' % user_id

        item = cache.get(key)
        if item is not None:
            return pickle.loads(str(item))

        try:
            if user is not None:
                item = self.get(user=user)
            elif user_id is not None:
                item = self.get(user__id=user_id)

        except Friend.DoesNotExist:
            item = Friend()
            if user:
                item.user = user
            elif user_id:
                item.user = User.objects.get(pk=user_id)
            item.save()

        cache.set(key, pickle.dumps(item))
        return item


class Friend(models.Model):
    user = models.ForeignKey(User)
    friend = models.TextField()
    pending = models.TextField()

    objects = FriendManager()

    class Meta:
        db_table = 'user_friend'
        verbose_name = 'Friend'

    def __getattr__(self, name):
        if name == 'friends':
            if not self.friend: return []
            return self.friend.split(',')
        elif name == 'pendings':
            if not self.pending: return []
            return self.pending.split(',')
        return self.__getattribute__(name)

    def __unicode__(self):
        return '%s friend of %s' % (self.user, self.friend)

    def save(self):
        super(Friend, self).save()
        cache.delete('friends_%s' % (self.user.id))

    def delete(self):
        u = int(self.user.id)
        super(Friend, self).delete()
        cache.delete('friends_%s' % u)

    def has_in_friends(self, uid):
        if len(self.friend) == 0: return False
        return uid in self.friends

    def has_in_pending(self, uid):
        if len(self.pending) == 0: return False
        return uid in self.pendings

    def confirm(self, uid):
        a = self.add_friend(str(uid))
        b = self.remove_pending(str(uid))

        if not a or not b: return False

        self.engine.notify.add(user=self.user, type='friend', key='confirm_friend', date='today')
        self.engine.notify.add(user=self.user, type='friend', key='confirm_friend', date=None)

        return True

    def decline(self, uid):
        if not self.remove_pending(uid): return False

        self.engine.notify.add(user=self.user, type='friend', key='decline_pending', date='today')
        self.engine.notify.add(user=self.user, type='friend', key='decline_pending', date=None)

        return True

    def add_friend(self, uid):
        if self.has_in_friends(uid): return False

        friends = self.friends
        friends.append(uid)
        self.friend = ','.join(friends)
        self.save()

        profile = UserProfile.objects.get_by_id(uid)

        if hasattr(self, 'engine'):
            self.engine.notify.add(user=self.user, type='friend', key='add_friend', date='today')
            self.engine.notify.add(user=self.user, type='friend', key='add_friend', date=None, stream='%s|%s' % (
                reverse('profile', args=[slughifi(str(profile))]),
                str(profile)
            ))

        return True

    def remove_friend(self, uid):
        if not self.has_in_friends(uid): return False

        friends = self.friends
        del friends[friends.index(uid)]
        self.friend = ','.join(friends)
        self.save()

        self.engine.notify.add(user=self.user, type='friend', key='remove_friend', date='today')
        self.engine.notify.add(user=self.user, type='friend', key='remove_friend', date=None)

        return True

    def add_pending(self, uid):
        if self.has_in_friends(uid) or self.has_in_pending(uid): return False

        pendings = self.pendings
        pendings.append(uid)
        self.pending = ','.join(pendings)
        self.save()

        self.engine.notify.add(user=self.user, type='friend', key='add_pending', date='today')
        self.engine.notify.add(user=self.user, type='friend', key='add_pending', date=None)

        return True

    def remove_pending(self, uid):
        if not self.has_in_pending(uid): return False

        pendings = self.pendings
        del pendings[pendings.index(uid)]
        self.pending = ','.join(pendings)
        self.save()

        return True
