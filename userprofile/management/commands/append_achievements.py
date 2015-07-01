# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

import datetime

# from common.helpers.slughifi import slughifi
# import simplejson as json

from userprofile.models import UserProfile, UserStat
from engine.modules.achieve import Achieve


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        a = Achieve(None)

        for profile in UserProfile.objects.all():
            for stat in UserStat.objects.filter(date=datetime.date(1970, 1, 1), user=profile.user):
                a.trigger(user=profile.user, type=stat.type, key=stat.key, new_value=int(stat.value), date=None)
