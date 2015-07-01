# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('gift.views',
                       url(r'^send/(?P<car_id>\d+)/$', 'friend_send', name='friend_send'),
                       url(r'^accept/(?P<car_id>\d+)/(?P<user_id>\d+)/$', 'accept', name='gift_accept'),
                       url(r'^decline/(?P<car_id>\d+)/(?P<user_id>\d+)/$', 'decline', name='gift_decline'),
                       )
