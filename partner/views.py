# -*- coding: utf-8 -*-
from django.http import Http404
from django.conf import settings

from annoying.decorators import render_to
from common.helpers.core import reverse
from partner.forms import PartnerForm, PartnerAddForm
from partner.models import Partner, PartnerPayment


@render_to('partner/index.html')
def index(request):
    partners = Partner.objects.get_by_user(user=request.engine.user.user)
    income = {}
    if len(partners):
        for partner in partners:
            income[partner.name] = PartnerPayment.objects.get_total_by_partner(partner=partner)

    return {
        'partners': partners,
        'income': income,
    }


@render_to('partner/stat.html')
def stat(request, partner_id):
    try:
        partner = Partner.objects.get(pk=partner_id)
    except Partner.DoesNotExist:
        return Http404

    if partner.user != request.engine.user.user:
        return Http404

    income = PartnerPayment.objects.get_by_partner(partner=partner)
    # registered = UserProfile.objects.filter(partner=partner.name)

    stats = income  # add registered stats later

    return {
        'partner': partner,
        'stats': stats,
    }


@render_to('partner/add.html')
def add(request):
    form = PartnerAddForm(instance=Partner())
    if request.method == 'POST':
        form = PartnerAddForm(request.POST, instance=Partner())

        if form.is_valid():
            partner = form.save(commit=False)
            partner.user = request.engine.user.user
            partner.pay_share = settings.PARTNER_SHARE
            partner.save()

            return request.engine.redirect(reverse('partner_edit', args=[partner.id]))

        return {
            'form': form,
        }

    return {
        'form': form,
    }


@render_to('partner/edit.html')
def edit(request, partner_id):
    try:
        partner = Partner.objects.get(pk=partner_id)
    except Partner.DoesNotExist:
        return Http404

    if partner.user != request.engine.user.user:
        return Http404

    form = PartnerForm(instance=partner)

    if request.method == 'POST':
        form = PartnerForm(request.POST, instance=partner)

        if form.is_valid():
            form.save()
            return request.engine.redirect(reverse('partners'))

        return {
            'form': form,
            'partner': partner,
        }

    return {
        'form': form,
        'partner': partner,
    }
