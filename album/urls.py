# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('album.views',
                       url(r'^$', 'index', name='albums'),
                       url(r'^(\d+)/$', 'details', name='album'),
                       url(r'^buy/(\d+)/$', 'buy', name='album_buy'),
                       url(r'^(\d+)/(\d+)/$', 'stick', name='album_stick'),
                       )
