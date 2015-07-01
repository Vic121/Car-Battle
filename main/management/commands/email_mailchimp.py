# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

from userprofile.models import UserProfile
from greatape import MailChimp


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        mail = Mail()

        for profile in UserProfile.objects.all():
            email = profile.user.email
            if email.endswith('.ru') or email.endswith('.cc') or email.endswith('madfb.com') or email.endswith(
                    'car-battle.com') or email.endswith('w3net.pl'): continue

            try:
                print profile.user.email, mail.listSubscribe(mail.campaign_id, profile)
            except:
                continue


class Mail(object):
    def __init__(self):
        self.chimp = MailChimp('c208efd742b3f02aa8d2f23a10d0a407-us2', debug=True)
        self.campaign_id = self.listCampaigns()[0]['id']

    def listCampaigns(self):
        return self.chimp.lists()

    def listSubscribe(self, list_id, profile):
        return self.chimp.listSubscribe(id=list_id, email_address=profile.user.email,
                                        merge_vars={'FNAME': profile.username}, double_optin=False)
