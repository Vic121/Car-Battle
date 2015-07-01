# -*- coding: utf-8 -*-
import random
import logging
import StringIO

from django.conf import settings

import pycurl
from main.models import UserFBSpam, UserFBSpamLog, FBCache

SPAM_FREQUENCY = 4


class Facebook(object):
    def __init__(self, engine):
        self.engine = engine
        self.fb_spam = UserFBSpam.objects.get_by_user(user=self.engine.user.user)
        self.fb_cache = FBCache.objects.get_by_page(user=self.engine.user.user, page=self.engine.request.path[1:])

        self.access_token = self.engine.request.fbc_token

    def dashboard_publishActivity(msg):
        pass

    def get_cache_status(self, handler=None, url=None):
        if not handler and not url: return False

        try:
            if handler:
                fbc = FBCache.objects.get(user=self.engine.user.user, handler=handler)
            else:
                fbc = FBCache.objects.get(user=self.engine.user.user, url=url)
        except FBCache.DoesNotExist:
            fbc = FBCache()
            fbc.handler = handler
            fbc.url = url
            fbc.save()
            return False

        if fbc.to_refresh:
            return False
        return True

    def set_cache(self, handler=None, url=None, content=None):
        if (not handler and not url) or (not handler and not content): return False

        try:
            if handler:
                fbc = FBCache.objects.get(user=self.engine.user.user, handler=handler)
            else:
                fbc = FBCache.objects.get(user=self.engine.user.user, url=url)
        except FBCache.DoesNotExist:
            fbc = FBCache()
            if handler: fbc.handler = handler
            if url:        fbc.url = url

        if handler:
            self.engine.request.facebook.fbml.setRefHandle(handler, content)
        if url:
            self.engine.request.facebook.fbml.refreshRefUrl(url)

        fbc.to_refresh = False
        fbc.save()
        return True

    # --- Permissions

    def get_app_permissions(self, permission_type):
        if permission_type in (
                'publish_stream', 'email', 'offline_access', 'status_update', 'photo_upload', 'create_listing',
                'create_event',
                'rsvp_event', 'sms'):
            return self.engine.request.facebook.users.hasAppPermission(permission_type)
        else:
            return False

    # --- Stream.publish

    def post_help(self, job, msg=None, action_links=None, help_link=None):
        # if self.fb_spam.next_queue_at > datetime.datetime.now(): return

        msg = msg or ""
        action_links = action_links or ['<a href="%shelp_me/link=%s">Help me</a>' % (settings.SITE_URL, help_link)]

        try:
            response = self.engine.request.facebook.stream.publish(msg, {
                'images': [{'src': '%s%s' % (settings.MEDIA_URL, job.img), 'href': action_links}, ]}, '')
        except Exception, e:
            logging.warning('Cannot publish message / %s' % (e))
            log = UserFBSpamLog()
            log.user_id = self.engine.user.user.id
            log.type = e
            log.message = msg
            log.save()
            return

        # Spam
        self.fb_spam.sent += 1
        self.fb_spam.save()
        log = UserFBSpamLog()
        log.user_id = self.engine.user.user.id
        log.type = 'publish'
        log.message = msg
        log.save()

        logging.info('%s: post message %s.%s' % (self.engine.user.user, msg, response))

    def post_car(self, car):
        msg = "I own this car!"
        action_links = ['<a href="%s">Build your own garage</a>' % (settings.SITE_URL)]
        self.post_help(car, msg)

    # --- Status.set

    def set_status(self, content, clear=False):
        """Potrzebne odpowiednie uprawnienia

        <fb:prompt-permission perms="status_update">
        Grant permission for status updates
        </fb:prompt-permission>
        """
        response = self.engine.request.facebook.users.setStatus(content, clear)

        logging.info('set_status %s' % response)

    # --- Extras

    def get_random_friends(self, num=5):
        friends = self.engine.request.facebook.friends.get()
        rand = []
        for i in xrange(0, num):
            rand.append(random.choice(friends))

        return set(rand)

    def __request(self, params, new_api=True):
        if new_api:
            self.url = 'https://graph.facebook.com/%s/' % self.engine.request.fbc_uid
        else:
            self.url = 'https://api.facebook.com/method/'

        c = pycurl.Curl()
        c.setopt(pycurl.URL, self.url)
        # c.setopt(pycurl.POST, 1)
        # c.setopt(pycurl.POSTFIELDS, "request=%s" % wrapper)

        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        c.close()
        data = b.getvalue()
