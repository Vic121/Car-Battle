# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import Http404

import datetime
from common.helpers.core import reverse
from annoying.decorators import render_to
from auction.forms import SellForm
from common.paginator import DiggPaginator as Paginator


@render_to()
def index(request, tab, page_no):
    if not hasattr(request.engine, 'user'):
        return index_anon(request, page_no)

    request.engine.register('auction', tab)
    request.engine.module = 'auction'
    template_tab = 'auction'

    if request.GET.get('tier') and request.GET['tier'] in settings.TIERS:
        filter = request.GET['tier']
    else:
        filter = None

    if tab == 'auction':
        paginator = Paginator(request.engine.auction.items, settings.DEFAULT_AUCTIONS_PER_PAGE, body=8, padding=2)
        selected = request.engine.auction.items[
                   (int(page_no) - 1) * settings.DEFAULT_AUCTIONS_PER_PAGE:int(
                       page_no) * settings.DEFAULT_AUCTIONS_PER_PAGE
                   ]

    elif tab == 'watch':
        pass

    elif tab in ('bidding', 'bidded'):
        paginator = Paginator(request.engine.auction.items, settings.DEFAULT_AUCTIONS_PER_PAGE, body=8, padding=2)
        selected = request.engine.auction.items[
                   (int(page_no) - 1) * settings.DEFAULT_AUCTIONS_PER_PAGE:int(
                       page_no) * settings.DEFAULT_AUCTIONS_PER_PAGE
                   ]
        template_tab = 'status'

    else:
        return request.engine.redirect(reverse('auction'))

    try:
        current_page = paginator.page(page_no)
    except:
        raise Http404

    return {
        'TEMPLATE': 'auction/index_%s.fbml' % template_tab,
        'tab': tab,
        'page_no': int(page_no),
        'page': current_page,
        'selected': selected,
        'filter': filter,
        'items_count': len(request.engine.auction.items),
    }


@render_to('auction/index_auction_anon.html')
def index_anon(request, page_no):
    request.engine.register('auction', 'auction')
    request.engine.module = 'auction'

    if request.GET.get('tier') and request.GET['tier'] in settings.TIERS:
        filter = request.GET['tier']
    else:
        filter = None

    paginator = Paginator(request.engine.auction.items, settings.DEFAULT_AUCTIONS_PER_PAGE, body=8, padding=2)
    selected = request.engine.auction.items[
               (int(page_no) - 1) * settings.DEFAULT_AUCTIONS_PER_PAGE:int(page_no) * settings.DEFAULT_AUCTIONS_PER_PAGE
               ]

    try:
        current_page = paginator.page(page_no)
    except:
        raise Http404

    return {
        'page_no': int(page_no),
        'page': current_page,
        'selected': selected,
        'filter': filter,
        'items_count': len(request.engine.auction.items),
    }


@render_to()
def details(request, slug, auction_id):
    if not hasattr(request.engine, 'user'):
        return details_anon(request, auction_id)

    request.engine.register('auction')
    request.engine.module = 'auction_details'

    if not request.engine.auction.set_auction(auction_id):
        return request.engine.redirect(reverse('auction'))

    if datetime.datetime.now() > request.engine.auction.auction.end_at:
        return {
            'TEMPLATE': 'auction/details_fin.fbml',
            'item': request.engine.auction,
        }
    return {
        'TEMPLATE': 'auction/details.fbml',
        'item': request.engine.auction,
    }


@render_to()
def details_anon(request, auction_id):
    request.engine.register('auction')
    request.engine.module = 'auction_details'

    if not request.engine.auction.set_auction(auction_id):
        return request.engine.redirect(reverse('auction'))

    if datetime.datetime.now() > request.engine.auction.auction.end_at:
        return {
            'TEMPLATE': 'auction/details_fin_anon.html',
            'item': request.engine.auction,
        }
    return {
        'TEMPLATE': 'auction/details_anon.html',
        'item': request.engine.auction,
    }


def bid(request):
    request.engine.register('auction')
    request.engine.auction.bid(request.POST.get('item_id'), request.POST.get('amount'))

    return request.engine.redirect(
        reverse('auction_details', args=[request.POST.get('item_slug'), request.POST.get('item_id')]))


def buy_now(request):
    request.engine.register('auction')
    request.engine.auction.buy_now(request.POST.get('item_id'))

    return request.engine.redirect(
        reverse('auction_details', args=[request.POST.get('item_slug'), request.POST.get('item_id')]))


@render_to('auction/sell.fbml')
def sell(request, item_type, item_id):
    from auction.models import Auction
    from common.models import Car
    from job.models import Garage

    item = Car.objects.get_by_id(item_id)
    garage = Garage.objects.get_by_user(user=request.engine.user.user)

    if item is None or not garage.has_car(item.id):
        return request.engine.redirect(reverse('garage'))

    form = SellForm()
    if request.method == 'POST' and request.POST.has_key('duration'):
        form = SellForm(request.POST)

        if form.is_valid():
            a = Auction()
            a.title = "%s %s" % (item.manuf, item.name)
            a.seller = request.engine.user.user
            a.car = item
            a.tier = item.tier
            a.start_price = form.cleaned_data.get('start_price') or 0
            a.buy_it_now_price = form.cleaned_data.get('buy_it_now_price') or 0
            a.current_price = form.cleaned_data['start_price']
            a.is_for_credits = False
            a.is_refunded = False
            a.start_at = datetime.datetime.now()
            a.end_at = datetime.datetime.now() + datetime.timedelta(days=int(form.cleaned_data['duration']))
            a.save()

            garage.engine = request.engine
            garage.remove_car(item.id)
            request.engine.user.profile.cars = len(garage)
            request.engine.user.profile.save()

            return request.engine.redirect(reverse('auction'))

    return {
        'item_type': item_type,
        'item_id': item_id,
        'item': item,
        'form': form,
    }
