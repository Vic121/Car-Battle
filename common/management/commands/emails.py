# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage
# from common.models import Mail

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        self.subject = 'blog tip'
        self.content = """hi,

I respect your time, so I'll keep it short.

I read a wide range of football blogs and I respect all the hard work
you guys do, so I was thinking - what could I do to give something
back to the community and make blogs even better?

Looking over the blogs I normally read, what I usually find missing is
live scores and up-to-date league tables. Having this kind of data
on-site has a lot of benefits, but it takes time to keep them
up-to-date. This is why I decided to create set of widgets that
readers would find useful and offer them for free to anyone with a
blog or website.

All I'd like to ask is that you take a look at
http://pickscore.net/partners/ in a spare moment and if you are
interested, create some widgets, play with them and see if it’s
something you want for your website. If you have any questions or
feedback just let me know.

PS. It's hosted on my score prediction website but don't worry about
this, it was just a convenient place to store the widgets.

greetings,
Marek
"""

        emails = [

        ]

        for self.receiver in emails:
            print self.receiver
            self.send_mail()
        print 'sent %d emails' % len(emails)

    def send_mail(self):
        msg = EmailMessage(self.subject, self.content, 'Marek <marek@pickscore.net>', [self.receiver])
        # msg.content_subtype = "html"
        msg.send()
