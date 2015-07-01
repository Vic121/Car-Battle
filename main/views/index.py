# -*- coding: utf-8 -*-
import logging
import urllib2

import simplejson as json

import datetime


# import flickrapi
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from annoying.decorators import render_to
from common.helpers.core import reverse
from django.conf import settings
from django.contrib.auth.models import User
from main.forms import RegistrationForm
from common.helpers.slughifi import slughifi

from common.models import Car, Task
from album.models import Album
from main.models import News, UserStream
from friend.models import Friend
from achievement.models import UserAchievement
from userprofile.models import UserProfile
from common.helpers._gta import get_help_me_cookie, get_gift_cookie, get_invite_cookie

# @render_to('index.html')
def index(request):
    if not hasattr(request.engine, 'user'):
        if request.engine.IS_PARTNER:
            if request.engine.IS_FB and not request.GET.has_key('fb_sig_user'):
                return render_to_response('main/register_partner_fb.html', {}, context_instance=RequestContext(request))
            return index_partner(request)
        if request.engine.IS_FBC and request.GET.has_key('reg_fbc') and request.fbc_uid:
            return index_fbc(request)
        return index_anon(request)

    request.engine.module = 'home'

    if len(request.GET.keys()) > 0:
        for k, v in request.GET.iteritems():
            request.engine.log.add_log(k, 0, v)

    from wishlist.models import WishList
    from gift.models import UserGift

    wishlist = WishList.objects.get_by_user(user=request.engine.user.user)
    friend = Friend.objects.get_by_user(user=request.engine.user.user)
    gift = UserGift.objects.get_by_user(user=request.engine.user.user)
    news = News.objects.get_latest(limit=5)
    achievement = UserAchievement.objects.get_by_user(user=request.engine.user.user)
    wall = UserStream.objects.get_friend_wall(user=request.engine.user.user, limit=30)

    request.engine.register('album')
    albums = request.engine.album.group(request.engine.album.list)

    # response = request.engine.redirect(reverse('jobs'))
    if request.engine.IS_PARTNER:
        template = 'index_partner.html'
    elif hasattr(request, 'facebook'):
        template = 'index.fbml'
    else:
        template = 'index.html'

    response = render_to_response(
        template, {
            'wish_list': Car.objects.get_list(wishlist.items),
            'friends': UserProfile.objects.get_many_by_user_ids(friend.friends[:12]),
            'friends_pending': UserProfile.objects.get_many_by_user_ids(friend.pendings[:12]),
            'friends_count': len(friend.friends),
            'friends_pending_count': len(friend.pendings),
            'gifts_pending': UserGift.objects.expand(gift.pendings[:12]),
            'gifts_pending_count': len(gift.pendings),
            'albums': albums['Buy more'],
            'news': news,
            'achievements': achievement,
            'wall': wall,
        }, context_instance=RequestContext(request)
    )

    # Check
    if request.engine.user.profile.is_premium:
        request.engine.user.check_premium()
    if request.engine.user.profile.status == 'new':
        request.engine.user.profile.status = 'user'
        request.engine.user.buy_cars(3, 'starter', 'Here you have a few cars for a good start. Have fun!')

    get_help_me_cookie(request, response)
    get_gift_cookie(request, response)
    get_invite_cookie(request, response)

    return response


# @render_to('index.html')
def index_anon(request):
    if hasattr(request, 'facebook'):
        template = 'index_anon.fbml'
    else:
        template = 'index_anon.html'

    response = render_to_response(
        template, {
            'news': News.objects.get_latest(limit=10),
            'albums': Album.objects.get_latest(limit=5),
        }, context_instance=RequestContext(request)
    )

    get_help_me_cookie(request, response)
    get_gift_cookie(request, response)
    get_invite_cookie(request, response)

    return response


def index_fb(request):
    return HttpResponseRedirect(reverse('jobs'))


@render_to('main/register_fbc.html')
def index_fbc(request):
    from django.contrib.auth import login, get_backends
    from django.contrib.auth.models import User
    from userprofile.models import UserProfile

    try:
        details = json.loads(
            urllib2.urlopen('https://graph.facebook.com/me?access_token=%s' % request.fbc_token).read())
    except Exception, e:
        logging.error('Error fetching details, fb_uid: %s, token: %s' % (request.fbc_uid, request.fbc_token))

    # if not details.has_key('email'):
    # logging.error('No email in %s' % json.dumps(details))

    form = RegistrationForm()
    if request.method == 'POST':

        username = request.POST['username']

        form = RegistrationForm(request.POST)
        if form.is_valid():

            try:
                profile = UserProfile.objects.get(partner='fbc', partner_login=request.fbc_uid)
                user = profile.user

                profile.username = profile.username_color = username
                profile.partner = 'fb'
                profile.partner_login = request.fbc_uid
                profile.domain = 'http://www.car-battle.com/'
                profile.save()

                user.username = username
                user.first_name = details.get('first_name')
                user.last_name = details.get('last_name')
                user.email = details.get('email') or request.POST['email']
                user.save()

            except UserProfile.DoesNotExist:
                # rejestracja
                profile = UserProfile()
                profile.user = User.objects.create_user(username, details.get('email') or request.POST['email'],
                                                        request.POST['password1'])
                profile.username = profile.username_color = username
                profile.partner = 'fb'
                profile.partner_login = request.fbc_uid
                profile.domain = 'http://www.car-battle.com/'
                profile.add_log(log_type='register', log_type_id=profile.user.id, log='from www via fb',
                                ip=request.META.get('REMOTE_ADDR'))
                profile.save()

                profile.user.is_active = True
                profile.user.save()

                user = profile.user

            import Image, os

            try:
                path = settings.MEDIA_ROOT + 'avatars/' + str(user.id / 1000)
                if not os.path.isdir(path):
                    os.makedirs(path)
                image = '%s/%s.jpg' % (path, str(user.id))
                img = urllib2.urlopen('http://graph.facebook.com/%s/picture?type=large' % request.fbc_uid).read()
                tmp = open('%s/%s.jpg' % (path, str(user.id)), 'wb')
                tmp.write(img)
                tmp.close()
                i = Image.open(image)
                i.thumbnail((480, 480), Image.ANTIALIAS)
                i.convert("RGB").save(image, "JPEG")
            except Exception, e:
                logging.error("Could not save avatar from Facebook")
                logging.error(e)

            backend = get_backends()[0]
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, user)

            # wysylamy powiadomienie mailem
            Task(user=user, task='mail', source='registered', comment=json.dumps({'recipient': profile.user_id})).save()

            return HttpResponseRedirect('/')

    else:
        username = ''

    return {
        'username': username,
        'email': details.get('email') or '%s@madfb.com' % details['id'],
        'password': User.objects.make_random_password(length=10,
                                                      allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'),
        'form': form,
    }


@render_to('main/register_partner.html')
def index_partner(request):
    import hashlib
    from django.contrib.auth import login, get_backends
    from django.contrib.auth.models import User
    from userprofile.models import UserProfile
    from partner.models import Partner

    # double-login version
    if not request.engine.IS_FB and ( \
                                not request.GET.has_key('username') and \
                                    not request.GET.has_key('password') and \
                                not request.GET.has_key('email') and \
                            request.GET.has_key('partner') and \
                            len(request.GET['partner']) > 0 and \
                        len(request.GET['partner']) <= 20):
        try:
            partner = Partner.objects.get(name=request.GET['partner'], is_active=True)
        except Partner.DoesNotExist:
            return HttpResponse('Partner inactive')
        return HttpResponseRedirect(reverse('auth_login') + '?partner=' + partner.name)

    # single-login version
    if not request.engine.IS_FB and ( \
                                                not request.GET.has_key('username') or \
                                                    not request.GET.has_key('password') or \
                                                not request.GET.has_key('email') or \
                                            not request.GET.has_key('partner') or \
                                            len(request.GET['partner']) == 0 or \
                                        len(request.GET['partner']) > 20 or \
                                    len(request.GET['email']) == 0 or \
                                len(request.GET['email']) > 75 or \
                            len(request.GET['username']) < 4 or \
                        len(request.GET['username']) > 20):
        return HttpResponse('Parameters missing')

    if request.engine.IS_FB and ( \
                        not request.GET.has_key('fb_sig_user') or \
                            not request.GET.has_key('fb_sig_api_key') or \
                            len(request.GET['fb_sig_user']) == 0 or \
                        request.GET['fb_sig_api_key'] != settings.FACEBOOK_API_KEY):
        return HttpResponse('Parameters missing')

    if request.engine.IS_FB:
        username = request.GET['fb_sig_user']

        try:
            details = json.loads(urllib2.urlopen(
                'https://graph.facebook.com/%s?access_token=%s' % (request.fbc_uid, request.fbc_token)).read())
        except Exception, e:
            logging.error('Error fetching details, fb_id: %s | %s | https://graph.facebook.com/%s?access_token=%s' % (
                request.fbc_uid, e, request.fbc_uid, request.fbc_token))
    else:
        username = request.GET['username']
        email = request.GET['email']
        password = request.GET['password']

    if request.engine.IS_FB:
        partner_name = 'fb'
        domain = 'http://apps.facebook.com/car_battle/'
    else:
        partner_name = request.GET['partner']
        domain = 'http://www.car-battle.com/'

    try:
        partner = Partner.objects.get(name=partner_name, is_active=True)
    except Partner.DoesNotExist:
        return HttpResponse('Partner inactive')

    h = hashlib.md5()
    h.update(username + partner.secret_code)
    if not request.engine.IS_FB and password != h.hexdigest():
        return HttpResponse('Authentication failed')

    try:
        profile = UserProfile.objects.get(partner=partner.name, partner_login=username)
        if profile is not None:
            user = profile.user
            backend = get_backends()[0]
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, user)
            return HttpResponseRedirect('/')
    except UserProfile.DoesNotExist:
        pass

    form = RegistrationForm()
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email')

        form = RegistrationForm(request.POST)
        if form.is_valid():

            # Register on FB
            if request.engine.IS_FB:
                try:
                    profile = UserProfile.objects.get(fb_id=request.GET['fb_sig_user'])
                    user = profile.user

                    profile.username = profile.username_color = username
                    profile.partner = partner_name
                    profile.partner_login = request.GET['fb_sig_user']
                    profile.domain = domain
                    profile.save()

                    user.username = username
                    user.email = details['email']
                    user.save()

                except UserProfile.DoesNotExist:
                    # rejestracja
                    profile = UserProfile()
                    profile.user = User.objects.create_user(username, details['email'], request.POST['password1'])
                    profile.username = profile.username_color = username
                    profile.partner = partner_name
                    profile.partner_login = request.GET['fb_sig_user']
                    profile.domain = domain
                    profile.add_log(log_type='register', log_type_id=profile.user.id,
                                    log='from partner %s' % partner.name, ip=request.META.get('REMOTE_ADDR'))
                    profile.save()

                    profile.user.is_active = True
                    profile.user.save()

                    user = profile.user

            # Register on Web
            else:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    # rejestracja
                    profile = UserProfile()
                    profile.user = User.objects.create_user(username, email, request.POST['password1'])
                    profile.username = profile.username_color = username
                    profile.partner = request.GET['partner']
                    profile.partner_login = request.GET['username']
                    profile.add_log(log_type='register', log_type_id=profile.user.id,
                                    log='from partner %s' % partner.name, ip=request.META.get('REMOTE_ADDR'))
                    profile.save()

                    profile.user.is_active = True
                    profile.user.save()

                    user = profile.user

            backend = get_backends()[0]
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, user)

            # wysylamy powiadomienie mailem
            Task(user=request.engine.user.user, task='mail', source='registered',
                 comment=json.dumps({'recipient': profile.user_id})).save()

            return HttpResponseRedirect('/')

    else:
        username = email = ''

    return {
        'username': username,
        'email': email,
        'password': User.objects.make_random_password(length=10,
                                                      allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'),
        'form': form,
    }


@render_to('main/register.html')
def register(request):
    message = None
    form = RegistrationForm()

    from partner.models import Partner

    partner = ''
    if request.GET.has_key('partner'):
        try:
            partner = Partner.objects.get(name=request.GET['partner'], is_active=True).name
        except Partner.DoesNotExist:
            pass

    if request.method == 'POST' and request.POST['action_type'] == 'login':
        username = slughifi(request.POST['username'])
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                response = HttpResponseRedirect(reverse('home'))
                # get_invite_cookie(request, response, user)
                return response
            else:
                message = "Account inactive."
        else:
            message = "Entered nickname and password combination is not correct"

    if request.method == 'POST' and request.POST['action_type'] == 'register':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            profile = UserProfile()
            profile.user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'],
                                                    form.cleaned_data['password1'])
            profile.username = profile.username_color = form.cleaned_data['username']
            profile.partner = partner
            profile.domain = 'http://www.car-battle.com/'
            profile.save()

            if len(partner) > 0:
                log_type = 'from partner %s' % partner
            else:
                log_type = 'from web'
            profile.add_log(log_type='register', log_type_id=profile.user.id, log=log_type,
                            ip=request.META.get('REMOTE_ADDR'))

            profile.user.is_active = True
            profile.user.save()

            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)

            if len(partner) > 0:
                logging.info("%s registered from partner %s" % (form.cleaned_data['username'], partner))
            else:
                logging.info("%s registered on the web" % form.cleaned_data['username'])

            # wysylamy powiadomienie mailem
            Task(user=user, task='mail', source='registered', comment=json.dumps({'recipient': profile.user_id})).save()

            response = HttpResponseRedirect(reverse('home'))
            # get_invite_cookie(request, response, profile)
            return response

            # extra actions
            # message="Account created. Check your email and wait for link to activate your account."

    # if not settings.LOCAL:
    # 	flickr = flickrapi.FlickrAPI(settings.FLICKR_API_KEY, settings.FLICKR_API_SECRET, format='etree')
    # 	sets = flickr.favorites_getPublicList(user_id=settings.FLICKR_USER_ID, per_page='20', extras='url_o,url_t')
    # 	for photo in sets.find('photos').findall('photo'):
    # 		photos.append({'title': photo.attrib['title'], 'url': photo.attrib['url_t']})

    return {
        'form': form,
        'message': message,
    }


def logout(request):
    from django.contrib.auth import logout

    logout(request)
    return HttpResponseRedirect(reverse('home'))


@render_to('main/registered.html')
def registered(request):
    return {}


@render_to('main/leaderboard.html')
def leaderboard(request):
    from userprofile.models import UserProfile

    return {'top_20': UserProfile.objects.get_leaderboard(20)}


@render_to('main/about.html')
def about(request):
    return {}


@render_to('main/contact.html')
def contact(request):
    return {}


@render_to('main/tutorial.html')
def tutorial(request):
    return {}


@render_to()
def partner(request, page=None):
    if page:
        template = 'main/partner/%s.html' % page
    else:
        template = 'main/partner/index.html'

    return {'TEMPLATE': template}


@render_to('partner/test.html')
def partner_test(request):
    return {}


@render_to('666.html')
def maintance(request):
    return {}


def ping_on_install(request):
    from django.db import connection

    try:
        ip = request.META['REMOTE_ADDR']
    except:
        ip = ''

    sql = """
		INSERT INTO
			archive.garage_user_log
		VALUES (
			'0', 'install', '0', '0', '%s', '%s'
		)
	""" % (datetime.datetime.now(), ip)

    cursor = connection.cursor()
    cursor.execute(sql)
    return HttpResponse("")


def ping_on_uninstall(request):
    from django.db import connection

    try:
        ip = request.META['REMOTE_ADDR']
    except:
        ip = ''

    sql = """
		INSERT INTO
			archive.garage_user_log
		VALUES (
			'0', 'uninstall', '0', '0', '%s', '%s'
		)
	""" % (datetime.datetime.now(), ip)

    cursor = connection.cursor()
    cursor.execute(sql)
    return HttpResponse("")


def auth_gowalla(request):
    return HttpResponse('Authorized:' + request.GET.get('code'))


def auth_foursquare(request):
    if request.GET.has_key('code'):

        import urllib
        import simplejson as json

        url = 'https://foursquare.com/oauth2/access_token?client_id=NGSS4JKP1QSG3FWQQPOBXITQP4UAU5NRQVVHTEKRORRIG4QG&client_secret=GKRO3G1RK0S14V340M5V2WCB051OYBQWSKEJSOOTSJPM0IDE&grant_type=authorization_code&redirect_uri=http://www.car-battle.com/auth-foursquare&code=' + \
              request.GET['code']

        f = urllib.urlopen(url)

        try:
            token = json.loads(f.read())
            f.close()
            return HttpResponse('Authorized:' + str(token['access_token']))
        except:
            return HttpResponse('Not Authorized / Wrong JSON / ' + response.read())

    return HttpResponse('Not Authorized')
