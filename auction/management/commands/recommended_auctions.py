#!/usr/bin/python
from django.core.management.base import NoArgsCommand
import simplejson as json

import datetime
from auction.models import Auction as AuctionModel
from userprofile.models import UserProfile
from wishlist.models import WishList
from common.models import Task


class Auction(object):
    def __init__(self):
        pass

    def start(self):
        yd = datetime.datetime.now() - datetime.timedelta(days=71)
        auctions = AuctionModel.objects.filter(start_at__year=yd.year, start_at__month=yd.month, start_at__day=yd.day)

        for profile in UserProfile.objects.filter(is_active=True):
            interesting = []
            wishlist = WishList.objects.get_by_user(user=profile.user)
            for auction in auctions:
                if str(auction.car_id) in wishlist.items:
                    interesting.append(auction.id)

            if len(interesting) == 0: continue

            # send email
            Task(user=profile.user, task='mail', source='new_auction',
                 comment=json.dumps({'recipient': profile.user_id, 'auctions': interesting})).save()


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        a = Auction()
        a.start()


if __name__ == '__main__':
    a = Auction()
    a.start()
