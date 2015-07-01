# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('msg.views',
                       url(r'^$', 'list', {'type': 'inbox'}, name='msgs'),
                       url(r'^inbox/$', 'list', {'type': 'inbox'}, name='msg_inbox'),
                       url(r'^outbox/$', 'list', {'type': 'outbox'}, name='msg_outbox'),
                       url(r'^send/$', 'form', name='msg_send'),
                       )
