# -*- coding: utf-8 -*-
from django.http import Http404
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User

from common.helpers.core import reverse
from annoying.decorators import render_to
from common.models import Car
from main.models import UserStream
from userprofile.models import UserProfile, UserDetail


@render_to('userprofile/edit.html')
def edit(request, invite_code, secret_code):
    import Image
    import os

    if invite_code is not None and secret_code is not None:
        profile = UserProfile.objects.get_by_invite_key(invite_code)
        if profile is None: return request.engine.redirect('/')
        if request.engine.md5(invite_code + settings.SECRET_KEY)[:16] != secret_code:  return request.engine.redirect(
            reverse('/'))

        from django.contrib.auth import login, get_backends

        backend = get_backends()[0]
        profile.user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, profile.user)
        return request.engine.redirect(reverse('profile_edit'))

    if not hasattr(request.engine, 'user'):
        return request.engine.redirect('/')

    # TODO: naprawić to
    def check_passwords(old_pass, new_pass1, new_pass2, user):
        if old_pass and user.check_password(old_pass):

            if new_pass1 == new_pass2:
                user.set_password(new_pass1)
                return True
            else:
                return False
        else:
            return False

    def check_avatar(value):
        if 'content-type' in value:
            main, sub = value.content - type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png']):
                request.engine.log.message(message='JPEG, PNG, GIF only.', is_error=True)
                return None

        if value.size > (2 * 1024 * 1024):
            request.engine.log.message(message='Upload only files smaller than 2MB.', is_error=True)
            return None

        # try:
        path = '%savatars/%s/' % (settings.MEDIA_ROOT, str(request.engine.user.profile.user_id / 1000))
        if not os.path.isdir(path):
            os.makedirs(path, 0777)
        path = path + "%s.jpg" % request.engine.user.user.id
        destination = open(path, 'wb+')
        for chunk in value.chunks():
            destination.write(chunk)
        destination.close()

        try:
            img = Image.open(path)
            x, y = img.size
        except Exception, e:
            request.engine.log.message(
                message='Upload a valid image. The file you uploaded was either not an image or a corrupted image.',
                is_error=True)
            return None

        if x > 800 or y > 800:
            request.engine.log.message(message='Upload a valid image. This one is too big in size.', is_error=True)
            return {}
        if x > 50 and y > 50:
            if img.mode not in ('L', 'RGB'):
                img = img.convert('RGB')
            img = img.resize((50, 50), Image.ANTIALIAS)
            img.save(path, "JPEG")

        return path

    p = request.engine.user.profile

    # CHANGE PASSWORD
    post = request.POST.copy()
    if request.method == 'POST' and "change_pass" in post:
        if check_passwords(post['old_pass'], post['pass1'], post['pass2'], request.user):
            request.engine.log.message(message="Password changed", is_success=True)
        else:
            request.engine.log.message(message="Given passwords are incorrect", is_error=True)

        return request.engine.redirect(request.META['PATH_INFO'])

    # CHANGE AVATAR
    if request.method == 'POST' and "avatar" in request.FILES:
        image = check_avatar(request.FILES['avatar'])
        if image:
            request.engine.user.profile.avatar = "%s/%s.jpg" % (str(request.engine.user.profile.user_id / 1000), str(p))
            request.engine.user.profile.save()
            request.engine.log.message(message="Avatar updated", is_success=True)

        return request.engine.redirect(request.META['PATH_INFO'])

    # CHANGE NOTIFICATIONS
    if request.method == 'POST' and 'notify' in post:
        n = list(request.engine.user.profile.notify)
        for i in xrange(1, 4):
            if len(n) < i: n.append('0')
            if post.has_key('n%s' % i):
                n[i - 1] = '1'
            else:
                n[i - 1] = '0'
        request.engine.user.profile.notify = ''.join(n)
        request.engine.user.profile.save()

        return request.engine.redirect(request.META['PATH_INFO'])

    # EDIT PROFILE DATA
    ud, c = UserDetail.objects.get_or_create(user=request.engine.user.user, defaults={'username': p.username,
                                                                                      'first_name': request.engine.user.user.first_name,
                                                                                      'last_name': request.engine.user.user.last_name})
    if request.method == 'POST' and 'change_profile' in post:
        post = request.POST.copy()

        ud.msn = post['im_msn']
        ud.skype = post['im_skype']
        ud.jabber = post['im_jabber']
        ud.yahoo = post['im_yahoo']
        try:
            ud.gg = int(post['im_gg'])
        except ValueError:
            ud.gg = 0
        try:
            ud.icq = int(post['im_icq'])
        except ValueError:
            ud.icq = 0
        ud.about = post['about_me']
        ud.website = post['www']
        ud.save()

        request.engine.log.message(message="Profile updated", is_success=True)
        return request.engine.redirect(request.META['PATH_INFO'])

    return {
        'profile': p,
        'details': ud,
    }


@render_to('userprofile/garage.fbml')
def garage(request):
    request.engine.module = 'garage'

    return {
        'items': request.engine.user.get_garage().cars,
    }


def sell(request, car_id):
    request.engine.module = 'garage'
    garage = request.engine.user.get_garage()

    if garage.remove_car(car_id) is True:
        request.engine.log.message(message="Car sold")
    else:
        request.engine.log.message(message="Faced problem with selling car")

    car = Car.objects.get_by_id(car_id)
    if car.tier in ('1', '2', '3', '4', '5'):
        request.engine.user.profile.earn('cash', 2500 * int(car.tier))
    else:
        request.engine.user.profile.earn('cash', 35000)

    return request.engine.redirect(reverse('garage'))


def confirm_close(request):
    if request.method == 'POST' and request.POST.get('page') in settings.HOW_TO_PLAY:
        request.engine.user.profile.how_to_play_status(settings.HOW_TO_PLAY.index(request.POST['page']), 1)
        return HttpResponse('done')
    return HttpResponse('failed')


@render_to('userprofile/profile.html')
def profile(request):
    profile = request.engine.user.profile

    request.engine.register('album')
    albums = request.engine.album.group(request.engine.album.list)

    del albums['Buy more']

    return {
        'profile': profile,
        'albums': albums,
        'wall': UserStream.objects.get_latest(user=profile.user),
        'achievements': request.engine.achieve.get_by_user(user=profile.user),
    }


@render_to('userprofile/public.html')
def public(request, username):
    from wishlist.models import WishList

    try:
        user = User.objects.get(username__iexact=username)
        profile = UserProfile.objects.get_by_id(user.id)
    except User.DoesNotExist:
        raise Http404
    except UserProfile.DoesNotExist:
        raise Http404

    request.engine.register('album')
    request.engine.album.list = user
    albums = request.engine.album.group(request.engine.album.list)

    del albums['Empty']
    del albums['Buy more']

    wishlist = WishList.objects.get_by_user(user=profile.user)

    return {
        'profile': profile,
        'albums': albums,
        'wall': UserStream.objects.get_latest_public(user=user),
        'achievements': request.engine.achieve.get_by_user(user=user),
        'has_albums': sum([len(x) for x in albums.values()]),
        'wish_list': Car.objects.get_list(wishlist.items)
    }


@render_to('userprofile/public_album.html')
def public_album(request, username, album_id, url=None):
    try:
        user = User.objects.get(username__iexact=username)
        profile = UserProfile.objects.get_by_id(user.id)
    except User.DoesNotExist:
        raise Http404
    except UserProfile.DoesNotExist:
        raise Http404

    from album.models import UserAlbum

    ua = UserAlbum.objects.get_by_id(album_id)

    if ua.user != user:
        raise Http404

    cars = []
    has_cars = ua.cars
    for car in ua.album.cars:
        if str(car) in has_cars:
            st = 1
        else:
            st = 0

        cars.append([Car.objects.get_by_id(car), st])

    ua.elements = cars

    return {
        'profile': profile,
        'achievements': request.engine.achieve.get_by_user(user=user),
        'album': ua,
    }
