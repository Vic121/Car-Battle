# -*- coding: utf-8 -*-
import logging

import datetime
from auction.models import Auction as AuctionModel, AuctionOffer


class Auction(object):
    def __init__(self, engine, tab='auction'):
        self.engine = engine

        if tab == 'auction':
            self.items = AuctionModel.objects.filter(end_at__gte=str(datetime.datetime.now())[0:19])
            if engine.request.GET.has_key('tier') and engine.request.GET['tier'] in engine.settings.TIERS:
                self.items = self.items.filter(tier__iexact=engine.request.GET['tier'])
            order = 'end_at'
        elif tab == 'bidding':
            self.items = AuctionOffer.objects.filter(buyer=self.engine.user.user, is_refunded=False)
            if engine.request.GET.has_key('tier') and engine.request.GET['tier'] in engine.settings.TIERS:
                self.items = self.items.filter(auction__tier__iexact=engine.request.GET['tier'])
            order = 'auction_end_at'
        elif tab == 'bidded':
            self.items = AuctionOffer.objects.filter(buyer=self.engine.user.user, is_refunded=True)
            if engine.request.GET.has_key('tier') and engine.request.GET['tier'] in engine.settings.TIERS:
                self.items = self.items.filter(auction__tier__iexact=engine.request.GET['tier'])
            order = '-auction_end_at'

        self.items = self.items.order_by(order)

    def set_auction(self, auction_id):
        try:
            item = AuctionModel.objects.get(pk=auction_id)
        except AuctionModel.DoesNotExist:
            return None

        self.auction = item
        self.details = item.get_details()
        self.seller_name = item.seller

        self.bids = AuctionOffer.objects.get_by_auction(auction=item)

        return True

    def bid(self, item_id, amount):
        # Validation
        try:
            auction_id = int(item_id)
            amount = int(amount)
        except KeyError:
            return None
        except ValueError:
            return None
        except TypeError:
            return None

        if self.set_auction(auction_id) is None:
            return None

        # Too old auction?
        if datetime.datetime.now() > self.auction.end_at:
            self.engine.log.message(message="Auction already ended")
            return False

        # Your auction?
        if self.auction.seller == self.engine.user.user:
            self.engine.log.message(message="Can't bid on your auction of course :)")
            return False

        # Less then curren_price?
        if amount <= self.auction.current_price:
            self.engine.log.message(message="Offer more than $%(amount)d" % {'amount': int(self.auction.current_price)})
            return None

        # Highest offer?
        if len(self.bids) == 0:
            if self.get_bid(self.auction.start_price, amount) is not False:
                self._outbid(self.auction.start_price)
                return True
            return False

        highest_bid = self.bids[0]

        # Podnies wlasny udzial
        if highest_bid.buyer == self.engine.user.user:
            if self.block_money(amount - highest_bid.max_price) is not False:
                highest_bid.max_price = amount
                highest_bid.save()

                self.engine.log.message(
                    message="Your current maximum offer is %(max)d" % {'max': highest_bid.max_price})
                return True
            return False

        # Automatycznie podbicie
        if amount > highest_bid.price and amount <= highest_bid.max_price:
            if self.get_bid(amount, amount) is False: return False

            if amount == highest_bid.max_price:
                highest_bid.price = highest_bid.max_price
                highest_bid.save()
            else:
                highest_bid.price = amount + 1
                highest_bid.save()

            self.my_offer.price = amount
            self.my_offer.max_price = amount
            self.my_offer.save()

            self.auction.current_price = highest_bid.price
            self.auction.save()

            self.engine.log.message(message="You have been outbidded")
            return True

        # Przebijam
        if amount > highest_bid.max_price:
            if self.get_bid(amount, amount) is False: return False

            highest_bid.price = highest_bid.max_price
            highest_bid.save()

            self.my_offer.price = highest_bid.max_price + 1
            self.my_offer.max_price = amount
            self.my_offer.save()

            self.auction.current_price = self.my_offer.price
            self.auction.save()

            self.engine.log.message(message="Your offer is currently the highest")
            return True

        logging.warning("Unknown bid option")
        return False

    def buy_now(self, item_id):
        # Validation
        try:
            auction_id = int(item_id)
        except KeyError:
            return None
        except ValueError:
            return None
        except TypeError:
            return None

        if self.set_auction(auction_id) is None:
            return None

        # Too old auction?
        if datetime.datetime.now() > self.auction.end_at:
            self.engine.log.message(message="Auction already ended")
            return False

        # Your auction?
        if self.auction.seller == self.engine.user.user:
            self.engine.log.message(message="Can't bid on your auction of course :)")
            return False

        if self.block_money(self.auction.buy_it_now_price) is not False:
            self.buyer = self.engine.user.user
            self.auction.end_at = datetime.datetime.now()
            self.auction.is_buy_now = True
            self.auction.save()

            self.engine.log.message(message="Car bought. I'll appear in your garage within few minutes.")
            return True

    def get_bid(self, amount, max_amount):
        self.my_offer = AuctionOffer.objects.get_by_user_auction(self.engine.user.user, auction=self.auction)
        if self.my_offer is not None:
            if not self.block_money(max_amount - self.my_offer.max_price): return False
            return self.my_offer

        if not self.block_money(max_amount): return False

        ao = AuctionOffer()
        ao.buyer = self.engine.user.user
        ao.auction = self.auction
        ao.price = amount
        ao.max_price = max_amount
        ao.save()

        self.my_offer = ao
        return self.my_offer

    def _outbid(self, amount):
        self.auction.current_price = amount
        self.auction.save()

    def block_money(self, amount):
        if amount <= 0:
            logging.warning("%s: tried to block <= 0 amount" % (self.engine.user.user))
            self.engine.log.message(message="You highest offer is higher")
            return False

        if self.engine.user.profile.has_enough('cash', amount):
            self.engine.user.profile.cash -= amount
            self.engine.user.profile.save()

            logging.debug("%s: blocked $%d for auction" % (self.engine.user.user, amount))
            return True
        self.engine.log.message(message="Not enough cash")
        return False
