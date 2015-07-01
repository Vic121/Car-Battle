# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('wishlist.views',
                       url(r'^$', 'index', name='wishlist'),
                       url(r'^(?P<user_id>\d+)/$', 'index', name='wishlist'),
                       url(r'^(?P<user_id>\d+)/gift/(?P<car_id>\d+)/$', 'gift', name='wishlist_gift'),
                       url(r'^add/(?P<car_id>\d+)/$', 'add_car', name='wishlist_add'),
                       url(r'^remove/(?P<car_id>\d+)/$', 'remove_car', name='wishlist_remove'),
                       )
