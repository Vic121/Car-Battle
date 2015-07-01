# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('main.views',
                       url(r'^payment/process/srpoints/$', 'payment.srpoints', name='payment_process_srpoints',
                           kwargs={'site': 'fb'}),
                       url(r'^payment/process/www/$', 'payment.srpoints', name='payment_process_srpoints',
                           kwargs={'site': 'www'}),
                       url(r'^payment/process/offerpal/$', 'payment.offerpal', name='payment_process_offerpal',
                           kwargs={'site': 'fb'}),
                       url(r'^payment/process/offerpal_www/$', 'payment.offerpal', name='payment_process_offerpal',
                           kwargs={'site': 'www'}),
                       url(r'^payment/process/webtopay/$', 'payment.webtopay', name='payment_process_webtopay'),
                       url(r'^payment/process/furtumo/$', 'payment.furtumo', name='payment_process_furtumo'),
                       )
