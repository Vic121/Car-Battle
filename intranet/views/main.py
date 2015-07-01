# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection


@staff_member_required
def index(request):
    # return HttpResponseRedirect(reverse('intranet_albums'))

    def query(query, one=True):
        cursor = connection.cursor()
        c = cursor.execute(query)
        if one:
            return cursor.fetchone()[0]
        return cursor.fetchall()

    data = {}
    data['jobs_by_tier'] = query(
        'SELECT COUNT(*), tier	FROM car WHERE tier!="0" AND is_active=1 AND is_active_in_garage=1 AND in_garage=1 GROUP BY tier ORDER BY tier',
        False)
    data['jobs'] = query(
        'SELECT COUNT(*) FROM car WHERE tier!="0" AND is_active=1 AND is_active_in_garage=1 AND in_garage=1')

    # users
    data['user_all'] = query('SELECT COUNT(*) FROM user')

    data['user_by_day'] = []
    for day in query(
            'SELECT FROM_DAYS(TO_DAYS(created_at)) as day, COUNT(*) as sum FROM user GROUP BY day ORDER BY created_at DESC LIMIT 7',
            False):
        users = []
        for user in query(
                        'SELECT username FROM user WHERE created_at BETWEEN "%s 00:00:00" AND "%s 23:59:59" ORDER BY created_at DESC LIMIT 100' % (
                        day[0], day[0]), False):
            users.append('%s' % (user[0]))

        data['user_by_day'].append((str(day[0]), day[1], ', '.join(users)))

    data['pay_1day'] = query('SELECT SUM(credits) FROM payment WHERE created_at >= NOW() - INTERVAL 1 DAY') or 0
    data['pay_7day'] = query('SELECT SUM(credits) FROM payment WHERE created_at >= NOW() - INTERVAL 7 DAY') or 0
    data['pay_30day'] = query('SELECT SUM(credits) FROM payment WHERE created_at >= NOW() - INTERVAL 30 DAY') or 0

    data['auction_pending_dealer'] = query('SELECT COUNT(*) FROM auction WHERE is_refunded=0')
    data['auction_pending_not_dealer'] = query('SELECT COUNT(*) FROM auction WHERE is_refunded=0 AND seller_id<>1')

    data['auction_end_3day_dealer'] = query(
        'SELECT COUNT(*) FROM auction WHERE is_refunded=0 AND end_at >= NOW() - INTERVAL 3 DAY')
    data['auction_end_3day_not_dealer'] = query(
        'SELECT COUNT(*) FROM auction WHERE is_refunded=0 AND end_at >= NOW() - INTERVAL 3 DAY AND seller_id<>1')

    # codes = request.session.get('last_generated_codes')
    # if codes:
    # 	del request.session['last_generated_codes']

    return render_to_response(
        'intranet/index.html', {
            'data': data,
            # 'last_generated_codes': codes,
        }, context_instance=RequestContext(request)
    )


@staff_member_required
def social_notify(request):
    from common.im.twitter import Twitter
    from common.im.blip import Blip

    if request.POST.has_key('msg'):
        msg = request.POST['msg'].strip()
        if request.POST.has_key('to_blip'):
            b = Blip()
            b.send(msg)
        if request.POST.has_key('to_twitter'):
            t = Twitter()
            t.send(msg)

    request.user.message_set.create(message="Wysłano wiadomości")
    return HttpResponseRedirect('/intranet/')


@staff_member_required
def code(request):
    from main.models import PaymentPromoCode

    def gen_code():
        import hashlib

        sha = hashlib.sha1()
        sha.update(str(datetime.datetime.now()))
        sha_code = sha.hexdigest()
        return sha_code

    def get_code(value, valid_for_days):
        start = 0
        while True:
            try:
                code = gen_code()[start + 2:start + 22]

                PaymentPromoCode.objects.get(code=code)
                start += 1
            except PaymentPromoCode.DoesNotExist:
                pc = PaymentPromoCode()
                pc.code = code
                pc.value = value
                pc.valid_until = datetime.datetime.now() + datetime.timedelta(days=valid_for_days)
                pc.save()
                return pc

            if start > 10: return None

    try:
        if request.method != 'POST' or \
                                0 > int(request.POST['how_many']) > 100 or \
                                0 > int(request.POST['value']) > 101 or \
                        int(request.POST['valid_for_days']) <= 0:
            return HttpResponseRedirect('/intranet/')
    except KeyError:
        return HttpResponseRedirect('/intranet/')
    except ValueError:
        return HttpResponseRedirect('/intranet/')

    codes = []
    for i in xrange(int(request.POST['how_many'])):
        codes.append(get_code(int(request.POST['value']), int(request.POST['valid_for_days'])).code)

    if len(codes) > 0:
        request.user.message_set.create(message="Dodano kody!")
        request.session['last_generated_codes'] = "<br/>".join(codes)

    return HttpResponseRedirect('/intranet/')
