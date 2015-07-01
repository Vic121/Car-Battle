# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

from common.models import Car


def index(request, gift_id=None):
    request.engine.module = 'gifts'

    if not gift_id:
        return render_to_response('main/gift_1.fbml', {
            # 'gifts': Gift.objects.get_all(),
        }, context_instance=RequestContext(request))

    return render_to_response('main/gift_2.fbml', {
        'gift': Car.objects.get_by_id(gift_id),
    }, context_instance=RequestContext(request))
