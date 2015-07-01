# -*- coding: utf-8 -*-
import logging
from decimal import *

from django.shortcuts import render_to_response
from django.http import HttpResponse  # , Http404
from django.template import RequestContext
from django.conf import settings

from common.helpers.core import reverse
from main.models import Payment
from partner.models import Partner, PartnerPayment


def index(request):
    request.engine.module = 'store'

    return render_to_response(
        'main/payment.fbml', {
            'profile': request.engine.user.profile,
        }, context_instance=RequestContext(request)
    )


def buy(request, item):
    if item == 'premium':
        request.engine.user.buy_premium()
    elif item == '3_cars':
        request.engine.user.buy_cars(3, '3')
    elif item == '3_plus_cars':
        request.engine.user.buy_cars(3, '3+')
    elif item == '5_cars':
        request.engine.user.buy_cars(5, '5')
    elif item == '5_plus_cars':
        request.engine.user.buy_cars(5, '5+')
    else:
        request.engine.log.message(message="Unknown option")

    return request.engine.redirect(reverse('store'))


def srpoints(request, site):
    """
    On the postback, we send the following query arguments:
    new - user earned by filling out offer 'oid'
    total - total amount of accumulated by this user
    uid - the site's user uid (facebook, myspace, etc)
    oid - SuperRewards offer identifier
    You must reply:
    1 - if you updated your system successfully
    0 - if there is a problem on your end (we'll wait and resend the postback again)
    The reply should be just 1 digit (no xml, no tags, just 1 byte reply)
    Example:
    http://www.domain.com/postback.cgi?app=mygreatapp&new=25&total=1000&uid=1234567&oid=123
    Important
    1. 'oid' + 'uid' is not a unique cominbation. There are offers that users can fill out several times and get credited for them.
    2. Please always rely on total value in your calculations.
    """
    import hashlib

    h = hashlib.md5()
    h.update(request.GET['id'] + ':' + request.GET['new'] + ':' + request.GET['uid'] + ':' + settings.SRPOINTS_SECRET[
        str(site)])
    valid = h.hexdigest()

    from userprofile.models import UserProfile
    from django.core.mail import send_mail

    pay = Payment()
    pay.user_id = request.GET['uid']
    pay.site = site
    pay.provider = 'srpoints'
    pay.details = str(request.GET)
    pay.credits = request.GET['new']
    pay.total_credits = request.GET['total']

    if valid != request.GET['sig']:
        pay.status = 'invalid_transaction'
        pay.save()
        send_mail("Payment failure: invalid_transaction by %s" % request.GET['uid'], '', 'Car Battle <robot@madfb.com>',
                  ("madfb@madfb.com",), fail_silently=True)
        return HttpResponse(0)

    if site == 'fb':
        profile = UserProfile.objects.get_by_fb_id(request.GET['uid'])
    else:
        profile = UserProfile.objects.get_by_id(request.GET['uid'])
    if profile is None:
        pay.status = 'user_not_found'
        pay.save()
        send_mail("Payment failure: user_not_found: %s" % request.GET['uid'], '', 'Car Battle <robot@madfb.com>',
                  ("madfb@madfb.com",), fail_silently=True)
        return HttpResponse(0)

    profile.earn('credit', request.GET['new'])
    pay.status = 'ok'
    pay.save()

    if profile.partner != '':
        try:
            partner = Partner.objects.get(name=profile.partner)
            if partner.pay_share > 0:
                pp = PartnerPayment()
                pp.partner = partner
                pp.payment = pay
                pp.amount = (Decimal(num) / Decimal(10)) * Decimal(str(partner.pay_share))
                pp.share = Decimal(str(partner.pay_share))

                # nie plac, jezeli konto nieaktywne
                if not partner.is_active:
                    pp.is_payable = False
                pp.save()
        except Partner.DoesNotExist:
            logging.error("Received payment with unknown partner=%s" % profile.partner)
        except:
            logging.error("Partner share calculation error with payment_id=%s" % pay.id)

    logging.warning("Dodano %s kredytów" % str(pay.credits))
    if int(pay.credits) > 3:
        send_mail("Payment success at %s by %s" % (pay.site, str(pay.user_id)),
                  "%s credits added. %s do far payed by him" % (str(pay.credits), str(pay.total_credits)),
                  'Car Battle <robot@madfb.com>', ("madfb@madfb.com",), fail_silently=True)
    return HttpResponse(1)


def offerpal(request, site):
    """The callback server URL is how our servers ping your servers on offer completions.

    Notes: The callback URL format you will receive from our servers is as shown below:

    http://www.yourserver.com/anypath/reward.php?snuid=[Facebook	 user ID]&currency=[currency credit to user]
    snuid is the users id value of the Facebook	 user ID
    currency is the positive whole number
    Security: For security you can optionally white list Offerpal Media server IPs:

    74.205.58.114
    99.132.162.242
    99.132.162.243
    99.132.162.244
    99.132.162.245
    """

    from main.models import Payment
    from userprofile.models import UserProfile
    from django.core.mail import send_mail

    pay = Payment()
    pay.user_id = request.GET['snuid']
    pay.site = site
    pay.provider = 'offerpal'
    pay.details = str(request.GET)
    pay.credits = request.GET['currency']
    pay.total_credits = 0

    if site == 'fb':
        profile = UserProfile.objects.get_by_fb_id(request.GET['snuid'])
    else:
        profile = UserProfile.objects.get_by_id(request.GET['snuid'])
    if profile is None:
        pay.status = 'user_not_found'
        pay.save()
        send_mail("Payment failure: user_not_found: %s" % request.GET['snuid'], '', 'Car Battle <robot@madfb.com>',
                  ("madfb@madfb.com",), fail_silently=True)
        return HttpResponse(0)

    profile.earn('credit', request.GET['currency'])
    pay.status = 'ok'
    pay.save()

    if profile.partner != '':
        try:
            partner = Partner.objects.get(name=profile.partner)
            if partner.pay_share > 0:
                pp = PartnerPayment()
                pp.partner = partner
                pp.payment = pay
                pp.amount = (Decimal(num) / Decimal(10)) * Decimal(str(partner.pay_share))
                pp.share = Decimal(str(partner.pay_share))

                # nie plac, jezeli konto nieaktywne
                if not partner.is_active:
                    pp.is_payable = False
                pp.save()
        except Partner.DoesNotExist:
            logging.error("Received payment with unknown partner=%s" % profile.partner)
        except:
            logging.error("Partner share calculation error with payment_id=%s" % pay.id)

    logging.warning("Dodano %s kredytów" % str(pay.credits))
    if int(pay.credits) > 3:
        send_mail("Payment success at %s by %s" % (pay.site, str(pay.user_id)),
                  "%s credits added. %s do far payed by him" % (str(pay.credits), str(pay.total_credits)),
                  'Car Battle <robot@madfb.com>', ("madfb@madfb.com",), fail_silently=True)
    return HttpResponse(1)


def webtopay(request):
    """https://www.webtopay.com/specification_sms.html"""
    from main.models import Payment, PaymentCode
    from django.core.mail import send_mail

    pay = Payment()
    pay.user_id = 0
    pay.site = 'sms'
    pay.provider = 'webtopay'
    pay.details = str(request.GET)
    pay.credits = 0
    pay.total_credits = 0
    pay.status = 'ok'
    pay.save()

    if profile.partner != '':
        try:
            partner = Partner.objects.get(name=profile.partner)
            if partner.pay_share > 0:
                pp = PartnerPayment()
                pp.partner = partner
                pp.payment = pay
                pp.amount = (Decimal(num) / Decimal(10)) * Decimal(str(partner.pay_share))
                pp.share = Decimal(str(partner.pay_share))

                # nie plac, jezeli konto nieaktywne
                if not partner.is_active:
                    pp.is_payable = False
                pp.save()
        except Partner.DoesNotExist:
            logging.error("Received payment with unknown partner=%s" % profile.partner)
        except:
            logging.error("Partner share calculation error with payment_id=%s" % pay.id)

    send_mail("SMS Payment success by %s" % (pay.provider), "%s PLN" % str(request.GET['amount']),
              'Car Battle <robot@madfb.com>', ("madfb@madfb.com",), fail_silently=True)

    code = PaymentCode.codes.gen_new_code(value=request.GET['amount'])
    return HttpResponse('Car Battle: %s' % code)


def furtumo(request):
    """http://fortumo.com/main/about_premium
    81.20.151.38
    81.20.148.122
    """
    from main.models import Payment, PaymentCode
    from django.core.mail import send_mail

    pay = Payment()
    pay.user_id = 0
    pay.site = 'sms'
    pay.provider = 'furtumo'
    pay.details = str(request.GET)
    pay.credits = 0
    pay.total_credits = 0
    pay.status = 'ok'
    pay.save()

    send_mail("SMS Payment success by %s" % (pay.provider), "%s PLN" % str(request.GET['price']),
              'Car Battle <robot@madfb.com>', ("madfb@madfb.com",), fail_silently=True)

    code = PaymentCode.codes.gen_new_code(value=request.GET['price'])
    return HttpResponse('Car Battle: %s' % code)
