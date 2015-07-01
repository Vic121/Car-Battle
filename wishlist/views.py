# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

from annoying.decorators import render_to
from common.helpers.core import reverse
from common.models import Car
from userprofile.models import UserProfile

# from common.paginator import DiggPaginator as Paginator
from wishlist.models import WishList


@render_to('wishlist/index.html')
def index(request, user_id=None):
    if user_id is None:
        user = request.engine.user.user
    else:
        user = UserProfile.objects.get_by_id(user_id=user_id).user
        request.engine.user.get_garage()

    wishlist = WishList.objects.get_by_user(user=user)

    return {
        'wishlist': wishlist,
        'items': Car.objects.get_list(wishlist.items),
    }


def gift(request, user_id, car_id):
    return HttpResponseRedirect(reverse('wishlist', args=[user_id]))


def add_car(request, car_id):
    car = Car.objects.get_by_id(car_id)
    if car is None: return HttpResponseRedirect(reverse('home'))

    wishlist = WishList.objects.get_by_user(user=request.engine.user.user)
    wishlist.engine = request.engine
    wishlist.add_item(car.id)

    return HttpResponseRedirect(reverse('home'))


def remove_car(request, car_id):
    car = Car.objects.get_by_id(car_id)
    if car is None: return HttpResponseRedirect(reverse('home'))

    wishlist = WishList.objects.get_by_user(user=request.engine.user.user)
    wishlist.engine = request.engine
    wishlist.remove_item(car.id)

    return HttpResponseRedirect(reverse('home'))
