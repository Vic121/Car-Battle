# import logging
# import datetime
# import cPickle as pickle
from django.db import models
# from django.core.cache import cache
import simplejson as json
from common.models import Task
from django.contrib.auth.models import User
# from userprofile.models import UserProfile

class MsgManager(models.Manager):
    def get_by_user(self, user, start=0, end=None, catalog='inbox'):
        if catalog == 'inbox':
            msgs = self.filter(receiver=user)
        else:
            msgs = self.filter(sender=user, is_deleted=False)

        msgs = msgs.filter(is_spam=False).order_by('-sent_at')

        # TODO: load more in background
        # if end is None:
        # 	return msgs[start:start+settings.DEFAULT_MSGS_PER_PAGE]
        # else:
        # 	return msgs[start:end]

        return msgs

    def get_unread_count(self, user, last_id):
        return self.filter(receiver=user, is_spam=False, is_to_self=False, pk__gt=last_id).count()


class MsgSendManager(models.Manager):
    def send_to(self, sender, receiver, msg):
        try:
            user = User.objects.get(username__iexact=receiver)
            return self._send_to_user(sender, user, msg)
        except User.DoesNotExist:
            pass

        logging.debug('No msg receiver %s' % receiver)
        return False

    def _send_to_user(self, sender, user, txt):
        msg = Msg()
        msg.sender = sender
        msg.receiver = user
        if txt.startswith('@'):
            msg.is_to_self = False
        else:
            msg.is_to_self = True
        msg.content = txt
        msg.save()

        # wysylamy powiadomienie mailem
        if sender != user:
            Task(user=user, task='mail', source='new_message',
                 comment=json.dumps({'recipient': user.id, 'sender': sender.id})).save()

        logging.info('sent message from %s to %s' % (sender, user))
        return True


class Msg(models.Model):
    """Internal msging system"""

    sender = models.ForeignKey(User, related_name='sender')
    receiver = models.ForeignKey(User, related_name='receiver')
    content = models.CharField(max_length=160)

    is_to_self = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    send = MsgSendManager()
    objects = MsgManager()

    class Meta:
        db_table = 'msg'

    def __unicode__(self):
        return "Msg from %s to %s @ %s" % (self.sender, self.receiver, str(self.sent_at))

    def as_spam(self):
        self.is_spam = True
        self.save()
