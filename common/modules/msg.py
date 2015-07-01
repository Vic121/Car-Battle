# coding=utf-8
from django.conf import settings

from msg.models import Msg as MsgModel


class Msg(object):
    def __init__(self, engine):
        self.engine = engine

        self.inbox = None
        self.outbox = None
        self.unread_messages = MsgModel.objects.get_unread_count(self.engine.user.user,
                                                                 self.engine.user.profile.last_msg_id)

    def get_inbox(self, page=0):
        if self.inbox is None:
            self.inbox = MsgModel.objects.get_by_user(self.engine.user.user,
                                                      start=page * settings.DEFAULT_MSGS_PER_PAGE)
        return self.inbox

    def get_outbox(self, page=0):
        if self.outbox is None:
            self.outbox = MsgModel.objects.get_by_user(self.engine.user.user, catalog='outbox',
                                                       start=page * settings.DEFAULT_MSGS_PER_PAGE)
        return self.outbox

    def mark_unread_as_read(self):
        if self.unread_messages > 0:
            last_msg = MsgModel.objects.filter(receiver=self.engine.user.user,
                                               pk__gt=self.engine.user.profile.last_msg_id).order_by('-sent_at')[0]
            self.engine.user.profile.last_msg_id = last_msg.id
            self.engine.user.profile.save()
