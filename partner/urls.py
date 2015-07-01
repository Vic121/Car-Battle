# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('',
                       url(r'^$', 'partner.views.index', name='partners'),
                       url(r'^edit/(\d+)/$', 'partner.views.edit', name='partner_edit'),
                       url(r'^stat/(\d+)/$', 'partner.views.stat', name='partner_stat'),
                       url(r'^add/$', 'partner.views.add', name='partner_add'),

                       url(r'^integration.html$', 'main.views.index.partner', kwargs={'page': 'integration'},
                           name='partner_integration'),
                       url(r'^commissions.html$', 'main.views.index.partner', kwargs={'page': 'commissions'},
                           name='partner_commissions'),
                       url(r'^faq.html$', 'main.views.index.partner', kwargs={'page': 'faq'}, name='partner_faq'),
                       url(r'^terms.html$', 'main.views.index.partner', kwargs={'page': 'terms'}, name='partner_terms'),
                       )
