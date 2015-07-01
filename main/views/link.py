# -*- coding: utf-8 -*-
import datetime
# from django.shortcuts import render_to_response
# from django.template import RequestContext
from common.helpers.core import reverse
from django.conf import settings
from common.models import Car


def set_cookie(response, key, value, expire=None):
    if expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = expire
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                         "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                        secure=settings.SESSION_COOKIE_SECURE or None)


def _save(request, name, back='home'):
    response = request.engine.redirect(reverse(back))

    if not request.GET.has_key('link') or (request.GET.has_key('link') and len(request.GET['link'].strip()) != 16):
        return response

    set_cookie(response, name, request.GET['link'].strip())
    return response


def help_me(request):
    return _save(request, 'help_me_link')


def add_me(request):
    return _save(request, 'add_me_link')


def gift(request):
    return _save(request, 'gift_link')


def post_help(request, car_id, help_link):
    car = Car.objects.get_by_id(car_id)

    if hasattr(request.engine, 'facebook'):
        request.engine.facebook.post_help(car, help_link=help_link)
    else:
        print 'posted help for %s on profile' % car.name

    request.engine.log.message(message="Request for help posted to profile")
    return request.engine.redirect(reverse('jobs'))


def post_car(request, car_id):
    car = Car.objects.get_by_id(car_id)

    if hasattr(request.engine, 'facebook'):
        request.engine.facebook.post_car(car)
    else:
        print 'posted %s to profile' % car.name

    request.engine.log.message(message="%s posted to profile" % car.name)
    return request.engine.redirect(reverse('garage'))
