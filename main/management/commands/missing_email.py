# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
import simplejson as json

import datetime
from common.models import Task
from main.models import News
from userprofile.models import UserProfile


class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        minus10 = datetime.datetime.now() - datetime.timedelta(days=10)
        minus40 = datetime.datetime.now() - datetime.timedelta(days=40)

        for p in UserProfile.objects.filter(updated_at__lte=minus10, updated_at__gte=minus40):

            news = News.objects.filter(created_at__gte=p.updated_at).order_by('created_at')[:1]
            if len(news) > 0:
                n = news[0].id
            else:
                n = 0

            task = Task()
            task.user = p.user
            task.task = 'mail'
            task.source = 'missing_you'
            task.comment = json.dumps({'recipient': p.id, 'last_news': n})
            task.save()
