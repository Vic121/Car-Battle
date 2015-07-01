# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('encyclopedia.views',
                       url(r'^$', 'index', name='encyclopedia'),
                       url(r'^cars/(?P<manuf_url>[\w-]+)/$', 'car_list', name='encyclopedia_cars',
                           kwargs={'page_no': 1}),
                       url(r'^cars/(?P<manuf_url>[\w-]+)/(?P<page_no>\d+)/$', 'car_list', name='encyclopedia_cars'),
                       url(r'^car/(?P<manuf_url>[\w-]+)/(?P<model_url>[\w-]+)/(?P<car_id>\d+)/$', 'car_details',
                           name='encyclopedia_car'),

                       url(r'^albums/$', 'album_list', name='encyclopedia_albums', kwargs={'page_no': 1}),
                       url(r'^albums/(?P<page_no>\d+)/$', 'album_list', name='encyclopedia_albums'),
                       url(r'^album/(?P<album_url>[\w-]+)/(?P<album_id>\d+)/$', 'album_details',
                           name='encyclopedia_album'),

                       url(r'^achievements/$', 'achievement_list', name='encyclopedia_achievements'),
                       url(r'^achievement/(?P<group_url>[\w-]+)/(?P<name_url>\d+)/$', 'achievement_details',
                           name='encyclopedia_achievement'),
                       )
