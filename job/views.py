# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from common.helpers.core import reverse
from common.helpers._gta import get_help_me_cookie, get_gift_cookie


def index(request):
    request.engine.module = 'jobs'
    request.engine.register('job')

    if request.GET.has_key('exp'):
        request.engine.user.profile.earn('exp', int(request.GET['exp']), engine=request.engine)

    response = render_to_response(
        'jobs/index.fbml', {
            'user_job': request.engine.job.user_job,
            'profile': request.engine.user.profile,
            'tier_income': settings.TIER_INCOME,
            'tier_exp': {'1': settings.EXP['collect_car_tier_1'], '2': settings.EXP['collect_car_tier_2'],
                         '3': settings.EXP['collect_car_tier_3'], '4': settings.EXP['collect_car_tier_4'],
                         '5': settings.EXP['collect_car_tier_5'], '6': settings.EXP['collect_car_tier_6']},
        }, context_instance=RequestContext(request)
    )

    get_help_me_cookie(request, response)
    get_gift_cookie(request, response)

    return response


def collect(request, car_id):
    request.engine.register('job')
    request.engine.job.collect_job(car_id)
    return request.engine.redirect(reverse('jobs'))
