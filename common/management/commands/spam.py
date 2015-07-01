# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

# from django.db import connection
# from urllib2 import Request, urlopen, URLError, HTTPError
# from BeautifulSoup import BeautifulSoup
# import simplejson as json
from django.core.mail import EmailMessage


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        self.sender = 'Marek - Car Battle <marek@car-battle.com>'
        self.subject = 'new opportunity'
        self.content = """
hi,

got an opportunity for your site to engage your visitors and generate additional income. How? I recently created an unique game for car enthusiasts. The latest feature is ability to embed our game to any website, engage users and share revenue from their in-game payments. We give you up to 20% of every payment. All this for 100% free of course and super easy to implement, can be done in less than 15 minutes. Details to find on www.car-battle.com/partner.html.

Even if that doesn’t works for you, please let me know as your feedback is appreciated.

greetings and have a good day,
Marek		
"""

        for rcv in []:
            self.send_mail(rcv)
            print 'send to %s' % rcv

    def send_mail(self, rcv):
        msg = EmailMessage(self.subject, self.content, self.sender, [rcv])
        # msg.content_subtype = "html"
        msg.send()
