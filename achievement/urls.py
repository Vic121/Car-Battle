# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('achievement.views',
                       url(r'^(?P<type>[\w,-]+)/$', 'details', name='achievement'),
                       )
