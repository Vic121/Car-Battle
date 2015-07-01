# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.conf import settings


def is_group_member(func):
    def decorator(*args, **argv):
        try:
            ug = UserInterestGroup.objects.get(user=args[0].user, interestgroup__id=argv['group_id'])
        except UserInterestGroup.DoesNotExist:
            return HttpResponseRedirect(settings.GROUP_URL)

        return func(*args, **argv)

    return decorator
