# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('friend.views',
                       url(r'^accept/(?P<username>\d+)/$', 'add', name='friend_add'),
                       url(r'^accept/(?P<uid>\d+)/$', 'accept', name='friend_accept'),
                       url(r'^decline/(?P<uid>\d+)/$', 'decline', name='friend_decline'),
                       )
