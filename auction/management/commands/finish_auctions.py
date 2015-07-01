#!/usr/bin/python
import logging

from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User

import datetime
from engine.engine import Engine
from common.models import DummyRequest
from auction.models import Auction as AuctionModel, AuctionOffer
from userprofile.models import UserProfile

SELLER = User.objects.get(pk=71)


class Auction(object):
    def __init__(self):
        pass

    def start(self):
        auctions = AuctionModel.objects.filter(end_at__lt=datetime.datetime.now, is_refunded=False)

        for self.auction in auctions:
            logging.debug("Finishing auction of %s" % self.auction.title)

            self.seller = Engine(DummyRequest(self.auction.seller.id))
            self.seller.start()
            self.buyer = None

            self.bids = AuctionOffer.objects.get_by_auction(auction=self.auction)
            self.finish_auction()

            self.auction.is_refunded = True
            if self.buyer:
                self.auction.buyer_id = self.buyer.user.profile.user_id
            self.auction.save()

    def finish_auction(self):
        # Refund
        if len(self.bids) == 0:
            if self.auction.seller != SELLER:
                self.give_item(self.seller)

            return True

        # Buyer
        if not self.auction.is_buy_now or self.auction.buyer_id == 0:
            bid = self.bids[0]
            self.buyer = Engine(DummyRequest(bid.buyer.id))
            self.buyer.start()
            self.buyer.user.profile.earn('cash', bid.max_price - bid.price)

            bid.is_refunded = True
            bid.save()
        else:
            self.buyer = Engine(DummyRequest(self.auction.buyer_id))
            self.buyer.start()

        self.give_item(self.buyer)

        # Seller
        if not self.auction.is_buy_now or self.auction.buyer_id == 0:
            price = self.auction.current_price
            self.seller.user.profile.earn('cash', self.auction.current_price)
        else:
            price = self.auction.buy_it_now_price
            self.seller.user.profile.earn('cash', self.auction.buy_it_now_price)

        self.seller.notify.add(type='auction', key='income', value=price, date=None)
        self.buyer.notify.add(type='auction', key='outcome', value=price, date=None)
        self.seller.notify.add(type='auction', key='transaction', value=1, date=None)
        self.buyer.notify.add(type='auction', key='transaction', value=1, date=None)

        if len(self.bids) == 1: return True

        if not self.auction.is_buy_now or self.auction.buyer_id == 0:
            self.bids = self.bids[1:]

        for bid in self.bids:
            if bid.is_refunded == True: continue

            profile = UserProfile.objects.get_by_id(bid.buyer.id)
            profile.earn('cash', bid.max_price)
            bid.is_refunded = True
            bid.save()

    def give_item(self, engine):
        car = self.auction.car

        engine.user.get_garage()
        engine.user.garage.add_car(car.id)

        engine.user.profile.cars = len(engine.user.garage)
        engine.user.profile.save()
        return True


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        a = Auction()
        a.start()


if __name__ == '__main__':
    a = Auction()
    a.start()
