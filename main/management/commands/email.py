# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import simplejson as json

from common.models import Car, Task, Mail as MailModel
from main.models import News
from userprofile.models import UserProfile


class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        for task in Task.objects.filter(task='mail'):
            mail = Mail()
            if len(task.comment) > 0:
                for k, v in json.loads(task.comment).iteritems():
                    if k == 'car':
                        v = Car.objects.get_by_id(v)
                    mail.__dict__[k] = v
            mail.user = task.user
            eval('mail.%s()' % task.source)
            mail.send()

            if not settings.DEBUG:
                task.delete()


class Mail(object):
    def __init__(self):
        pass

    def gift_received(self):
        self.subject = 'Gift received from %s' % str(self.user)
        profile = UserProfile.objects.get_by_id(self.recipient)
        self.message = render_to_string('mail/gift_received.html', {
            'car': self.car,
            'car_img': '%s%s' % (settings.BASE_MEDIA_URL, self.car.img.replace('.jpg', '_m.jpg')),
            'sender': str(UserProfile.objects.get_by_id(self.sender)),
            'receiver': str(profile),
            'profile': profile,
        })
        self.recipient = profile.user.email

    def daily_summary(self):
        self.subject = 'Your daily summary'

    def friend_request(self):
        self.subject = 'New friend request'
        profile = UserProfile.objects.get_by_id(self.recipient)
        self.message = render_to_string('mail/friend_request.html', {
            'sender': str(UserProfile.objects.get_by_id(self.sender)),
            'profile': profile,
            'receiver': str(profile),
        })
        self.recipient = profile.user.email

    def new_auction(self):
        from auction.models import Auction

        self.subject = 'New auction you may like'
        profile = UserProfile.objects.get_by_id(self.recipient)
        auctions = Auction.objects.filter(id__in=self.auctions)
        self.message = render_to_string('mail/new_auction.html', {
            'profile': profile,
            'auctions': auctions,
            'receiver': str(profile),
        })
        self.recipient = profile.user.email

    def new_message(self):
        self.subject = 'Received new message'
        profile = UserProfile.objects.get_by_id(self.recipient)
        self.message = render_to_string('mail/new_msg.html', {
            'sender': str(UserProfile.objects.get_by_id(self.sender)),
            'receiver': str(profile),
            'profile': profile,
        })
        self.recipient = profile.user.email

    def registered(self):
        self.subject = 'Hello, Car Lover'  # Fan, later
        profile = UserProfile.objects.get_by_id(self.recipient)
        self.message = render_to_string('mail/registered.html', {
            'profile': profile,
        })
        self.recipient = profile.user.email

    def activate_reminder(self):
        self.subject = 'Hope you haven\'t forget about us'
        profile = UserProfile.objects.get_by_id(self.recipient)
        self.message = render_to_string('mail/registered_reminder.html', {
            'profile': profile,
        })
        self.recipient = profile.user.email

    def hello_activated(self):
        self.subject = 'Hola! Car Lover'
        profile = UserProfile.objects.get_by_id(self.recipient)
        self.message = render_to_string('mail/registered_confirmed.html', {
            'profile': profile,
        })
        self.recipient = profile.user.email

    def missing_you(self):
        if self.last_news == 0:
            n = []
        else:
            n = News.objects.filter(pk__gte=self.last_news).order_by('-created_at')[:20]

        self.subject = 'We\'re a bit lonely without you'
        profile = UserProfile.objects.get_by_id(self.recipient)
        self.message = render_to_string('mail/missing_you.html', {
            'receiver': str(profile),
            'news': n,
            'profile': profile,
        })
        self.recipient = profile.user.email

    def send(self):
        if settings.DEBUG:
            self.recipient = 'marek.mikuliszyn@gmail.com'
            self.subject = '[TEST] ' + self.subject

        msg = EmailMessage(self.subject, self.message, 'Car Battle <hello@car-battle.com>', [self.recipient])
        msg.content_subtype = "html"
        msg.send()

        mm = MailModel()
        mm.user = self.user
        mm.sender = 'hello@car-battle.com'
        mm.receiver = self.recipient
        mm.subject = self.subject
        mm.content = self.message
        mm.is_send = True
        mm.save()
