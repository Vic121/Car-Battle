# -*- coding: utf-8 -*-
import logging
# from engine.engine import Engine
# from common.models import DummyRequest
from django.conf import settings
import simplejson as json
from common.models import Task
from job.models import UserJob
from gift.models import Gift
from friend.models import Friend
from userprofile.models import UserProfile


def get_help_me_cookie(request, response):
    if not request.COOKIES.get('help_me_link') or len(request.COOKIES.get('help_me_link').strip()) != 16: return

    link = request.COOKIES.get('help_me_link').strip()

    try:
        user_job = UserJob.objects.get(link=link, is_active=True)
    except UserJob.DoesNotExist:
        response.set_cookie('help_me_link', 0)
        request.engine.log.message(message="This link is not valid anymore.")
        request.engine.log.add_log('help link invalid')
        return

    # zapraszanie siebie?
    if user_job.user == request.engine.user.user and not request.engine.user.user.is_superuser:
        response.set_cookie('help_me_link', 0)
        request.engine.log.message(message="Link is fine, trust me :)")
        return

    ret = user_job.new_helper(request.engine.user.user.id)

    if ret == 'duplicate':
        response.set_cookie('help_me_link', 0)
        request.engine.log.message(message="This link is not valid anymore.")
        request.engine.log.add_log('help link duplicate')
        logging.info('%s helped %s before. DUPLICATE.' % (request.engine.user.user, user_job.user))
        return

    response.set_cookie('help_me_link', 0)
    logging.info('%s helped %s' % (request.engine.user.user, user_job.user))
    request.engine.log.add_log('used help me link', user_job.user.id)


def get_gift_cookie(request, response):
    if not request.COOKIES.get('gift_link') or len(request.COOKIES.get('gift_link').strip()) != 16: return

    link = request.COOKIES.get('gift_link').strip()

    gift = Gift.objects.get_by_link(link=link)
    if not user_gift:
        response.set_cookie('gift_link', 0)
        request.engine.log.message(message="This link is not valid anymore.")
        request.engine.log.add_log('invalid link')
        return

    if str(request.engine.user.user.id) in gift.used:
        response.set_cookie('gift_link', 0)
        request.engine.log.message(message="You've claimed this gift already.")
        return

    gift.engine = request.engine
    gift.use_gift(request.engine.user.user)

    response.set_cookie('gift_link', 0)
    request.engine.log.add_log('used gift link', request.engine.user.user)
    request.engine.log.message(message='Your gift:<br/>' + print_car(gift.car, request.engine.IS_FB))


def get_invite_cookie(request, response):
    if request.COOKIES.get('add_me_link') is not None and request.COOKIES.get('add_me_link') != '0':

        try:
            invite_code = request.COOKIES.get('add_me_link')
        except ValueError:
            logging.info('Wrong add_me link')
            response.set_cookie('add_me_link', 0)
            return

        profile = UserProfile.objects.get_by_invite_key(invite_code)
        if profile is None:
            logging.info('No profile associated with code:%s' % invite_code)
            response.set_cookie('add_me_link', 0)
            return
        if profile.user == request.engine.user:
            logging.info('Self-invite')
            response.set_cookie('add_me_link', 0)
            return

        f = Friend.objects.get_by_user(user=request.engine.user.user)
        f.engine = request.engine
        f.add_pending(str(profile.user.id))
        response.set_cookie('add_me_link', 0)

        # wysylamy powiadomienie mailem
        Task(user=request.engine.user.user, task='mail', source='friend_request',
             comment=json.dumps({'receiver': profile.user_id, 'sender': request.engine.user.user_id})).save()


def print_car(car, is_fb=True):
    feed_story = {
        'name': car.name,
        'href': settings.SITE_URL,
        'description': "%s %s BHP, %s" % (car.engine_up, car.power_bhp, car.drive),
        'media': [{
            'type': 'image',
            'src': '%s%s' % (settings.BASE_MEDIA_URL, car.img.replace('.jpg', '_s.jpg')),
            'href': settings.SITE_URL
        }]
    }
    action_links = [{'text': 'Build your own garage', 'href': '%s' % settings.SITE_URL}]

    if is_fb:
        return """
		<script type="text/javascript"><!--
		var feedStory_%s = %s;
		var actionLinks_%s = %s;
		var userMsg_%s = 'I own it!';
		var headlineMsg_%s = 'Show everyone your collection';
		//--></script>
		<div class="body_textarea" style="margin-bottom: 5px; margin-left: 5px;">
			<div style="float: left; width: 250px;">
				<img src="%s%s"/>
			</div>
			<div style="float: left; margin-left: 10px;">
				<p class="title">%s</p>
				<p class="content">Engine %s</p>
				<span class="readmore_140" onclick="Facebook.streamPublish(userMsg_%s, feedStory_%s, actionLinks_%s, null, headlineMsg_%s, null, true, null);">POST TO PROFILE</span>
			</div>
		</div>""" % (
            car.id, json.dumps(feed_story), car.id, json.dumps(action_links), car.id, car.id, settings.BASE_MEDIA_URL,
            car.img.replace('.jpg', '_m.jpg'), car.name, feed_story['description'], car.id, car.id, car.id, car.id)

    return """
	<div class="body_textarea" style="margin-bottom: 5px; margin-left: 5px;">
		<div style="float: left; width: 250px;">
			<img src="%s%s"/>
		</div>
		<div style="float: left; margin-left: 10px;">
			<p class="title">%s</p>
			<p class="content">Engine %s</p>
		</div>
	</div>""" % (settings.BASE_MEDIA_URL, car.img.replace('.jpg', '_m.jpg'), car.name, feed_story['description'])
