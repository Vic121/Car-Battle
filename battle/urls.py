# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('battle.views',
                       url(r'^$', 'index', name='battle'),
                       url(r'^random/$', 'tier_battle', name='tier_battle'),
                       url(r'^random/(?P<param>\w+)/$', 'tier_battle', name='tier_battle'),
                       url(r'^details/(?P<user_id>\d+)/$', 'details', name='battle_details'),
                       url(r'^fight/(?P<user_id>\d+)/$', 'battle', name='battle_user'),
                       url(r'^fight/(?P<param>\w+)/$', 'battle', name='battle_user'),
                       )
