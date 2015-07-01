from django.conf.urls import patterns, include, url
from django.conf import settings

# admin.autodiscover()

urlpatterns = patterns('',
                       # (r'^admin/stats/', include('admin.urls')),
                       # (r'^admin/(.*)', admin.site.root),
                       # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # (r'^i18n/', include('django.conf.urls.i18n')),
                       (r'^accounts/', include('registration.urls')),
                       # (r'^facebook/', include('facebookconnect.urls')),
                       (r'^encyclopedia/', include('encyclopedia.urls')),

                       url(r'^$', 'main.views.index.index', name='home'),
                       url(r'^jobs/$', 'job.views.index', name='jobs'),
                       url(r'^job/(.+)/$', 'job.views.collect', name='job_collect'),
                       url(r'^garage/$', 'userprofile.views.garage', name='garage'),
                       url(r'^my_garage/$', 'userprofile.views.public', name='public_albums'),
                       url(r'^store/$', 'main.views.payment.index', name='store'),
                       url(r'^store/buy/(.+)/$', 'main.views.payment.buy', name='store_buy'),
                       url(r'^gifts/$', 'main.views.gift.index', name='gifts'),
                       url(r'^gifts/friend/(\d+)/$', 'main.views.gift.index', name='gifts'),
                       url(r'^confirm_close/$', 'userprofile.views.confirm_close', name='confirm_close'),

                       (r'^profile/', include('userprofile.urls')),
                       (r'^main/', include('main.urls')),
                       (r'^auction/', include('auction.urls')),
                       (r'^album/', include('album.urls')),
                       (r'^intranet/', include('intranet.urls')),
                       (r'^achievement/', include('achievement.urls')),
                       (r'^battle/', include('battle.urls')),
                       (r'^wishlist/', include('wishlist.urls')),
                       (r'^friends/', include('friend.urls')),
                       (r'^gift/', include('gift.urls')),
                       (r'^msg/', include('msg.urls')),
                       url(r'^partner.html$', 'main.views.index.partner', name='partner'),
                       (r'^partner-test.html$', 'main.views.index.partner_test'),
                       (r'^partner/', include('partner.urls')),

                       # url(r'^maintance/$', 'main.views.index.maintance', name="maintance"),
                       url(r'^ping_on_install/$', 'main.views.index.ping_on_install'),
                       url(r'^ping_on_uninstall/$', 'main.views.index.ping_on_uninstall'),

                       url(r'^achievements/$', 'achievement.views.list', name="achievements"),
                       url(r'^tutorial/$', 'main.views.index.tutorial', name="tutorial"),
                       url(r'^leaderboard/$', 'main.views.index.leaderboard', name="leaderboard"),
                       url(r'^contact/$', 'main.views.index.contact', name="contact"),
                       url(r'^about/$', 'main.views.index.about', name="about"),
                       url(r'^help_me/$', 'main.views.link.help_me', name="help_me_link"),
                       url(r'^add_me/$', 'main.views.link.add_me', name="add_me_link"),
                       url(r'^gift/$', 'main.views.link.gift', name="gift_link"),
                       url(r'^post_car/(\d+)/$', 'main.views.link.post_car', name="post_car_link"),
                       url(r'^post_help/(\d+)/$', 'main.views.link.post_help', name="post_help_link"),

                       (r'^auth-gowalla$', 'main.views.index.auth_gowalla'),
                       (r'^auth-foursquare$', 'main.views.index.auth_foursquare'),
                       )

# TEMPORARY
if settings.LOCAL:
    urlpatterns += patterns('',
                            url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
                            )
