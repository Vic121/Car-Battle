# -*- coding: utf-8 -*-
import simplejson as json
from django.http import HttpResponseRedirect
from django.conf import settings

from annoying.decorators import render_to
from common.helpers.core import reverse
from common.models import Car, Task
from common.paginator import DiggPaginator as Paginator
from friend.models import Friend
from gift.models import UserGift
from userprofile.models import UserProfile
from job.models import Garage


@render_to('gift/friend_send.html')
def friend_send(request, car_id):
    car = Car.objects.get_by_id(car_id)

    if request.method == 'POST':
        if not request.POST.has_key('friend'):
            request.engine.log.message(message="You forgot to select a friend")
            return HttpResponseRedirect(reverse('friend_send', args=[car.id]))

        try:
            receiver = UserProfile.objects.get_by_id(request.POST['friend'])
        except UserProfile.DoesNotExist:
            request.engine.log.message(message="Incorrect friend selected")
            return HttpResponseRedirect(reverse('friend_send', args=[car.id]))

        garage = Garage.objects.get_by_user(user=request.engine.user.user)
        if not garage.has_car(car.id):
            request.engine.log.message(message="Incorrect car selected")
            return HttpResponseRedirect(reverse('friend_send', args=[car.id]))

        # dodajemy gift do pending
        g = UserGift.objects.get_by_user(user=receiver.user)
        g.engine = request.engine
        g.add_pending(car.id, request.engine.user.user.id)

        # usuwamy z garazu
        garage.engine = request.engine
        garage.remove_car(car.id)

        # wysylamy powiadomienie mailem
        Task(user=request.engine.user.user, task='mail', source='gift_received', comment=json.dumps(
            {'sender': request.engine.user.profile.user_id, 'recipient': receiver.user_id, 'car': car_id})).save()

        request.engine.log.message(message="Car sent to %s" % receiver)
        return HttpResponseRedirect(reverse('garage'))

    friend = Friend.objects.get_by_user(user=request.engine.user.user)
    page_no = request.GET.get('page_no') or 1

    selected = friend.friends[
               (int(page_no) - 1) * settings.DEFAULT_FRIENDS_PER_GIFT_PAGE:int(
                   page_no) * settings.DEFAULT_FRIENDS_PER_GIFT_PAGE
               ]
    paginator = Paginator(friend.friends, settings.DEFAULT_FRIENDS_PER_GIFT_PAGE, body=8, padding=2)

    try:
        current_page = paginator.page(page_no)
    except:
        return HttpResponseRedirect(reverse('friend_send', args=[car_id]))

    return {
        'car': car,
        'friends': UserProfile.objects.get_many_by_user_ids(selected),
        'page_no': int(page_no),
        'page': current_page,
        'total': len(friend.friends),
    }


def accept(request, car_id, user_id):
    g = UserGift.objects.get_by_user(user=request.engine.user.user)
    g.engine = request.engine
    g.confirm(car_id, user_id)

    return request.engine.redirect(reverse('home'))


def decline(request, car_id, user_id):
    g = UserGift.objects.get_by_user(user=request.engine.user.user)
    g.engine = request.engine
    g.decline(car_id, user_id)
    return request.engine.redirect(reverse('home'))
