# -*- coding: utf-8 -*-
from common.helpers.core import reverse

# from common.models import Car
# from common.paginator import DiggPaginator as Paginator
from friend.models import Friend


def add(request, username):
    u = request.engine.user.get_by_user(username=username)

    f = Friend.objects.get_by_user(username=username)
    f.engine = engine
    f.add_pending(str(u.id))


def accept(request, uid):
    f = Friend.objects.get_by_user(user=request.engine.user.user)
    f.engine = request.engine
    f.confirm(uid)

    request.engine.user.profile.friends = len(f.friends)
    request.engine.user.profile.save()

    return request.engine.redirect(reverse('home'))


def decline(request, uid):
    f = Friend.objects.get_by_user(user=request.engine.user.user)
    f.engine = request.engine
    f.decline(uid)

    if request.engine.user.profile.friends != len(f.friends):
        request.engine.user.profile.friends = len(f.friends)
        request.engine.user.profile.save()

    return request.engine.redirect(reverse('home'))


def remove(request, uid):
    f = Friend.objects.get_by_user(user=request.engine.user.user)
    f.engine = request.engine
    f.remove_friend(uid)

    request.engine.user.profile.friends = len(f.friends)
    request.engine.user.profile.save()

    return request.engine.redirect(reverse('home'))
