# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('intranet.views',
                       url(r'^$', 'main.index', name='intranet_home'),
                       url(r'^albums/$', 'album.index', name='intranet_albums'),
                       url(r'^album/(\d+)/$', 'album.details', name='intranet_album'),
                       url(r'^album/(\d+)/edit/$', 'album.edit', name='intranet_album_edit'),

                       url(r'^merge/$', 'merge.index', name='intranet_merge'),

                       url(r'^user/$', 'user.index', name='intranet_user'),

                       url(r'^social/$', 'main.social_notify', name='admin_social'),
                       # url(r'^gen_promo_code/$', 'main.code', name='promo_codes'),
                       )
