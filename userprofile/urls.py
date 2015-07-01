# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('userprofile.views',
                       url(r'^$', 'profile', name='profile'),
                       url(r'^edit/$', 'edit', {'invite_code': None, 'secret_code': None}, name='profile_edit'),
                       url(r'^edit/(?P<invite_code>[\w\-_0-9]{16})/(?P<secret_code>[\w\-_0-9]{16})/$', 'edit',
                           name='profile_edit'),
                       url(r'^(?P<username>[\w\-_]{1,})/$', 'public', name='profile'),
                       url(r'^(?P<username>[\w\-_]{1,})/(?P<album_id>\d+)/(?P<url>.+)/$', 'public_album',
                           name='public_album'),
                       url(r'^sell/(?P<car_id>\d+)/$', 'sell', name='garage_sell'),
                       )
