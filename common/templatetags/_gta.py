# -*- coding: utf-8 -*-
import simplejson as json
from django.template import Library
from django.conf import settings

from ..helpers.core import reverse
from ..models import Car

register = Library()


@register.simple_tag
def help_left(help_has, tier):
    return settings.JOB_HELPERS_NEEDED_CUMM[int(tier) - 1] - help_has


@register.simple_tag
def collect_link(car):
    if settings.LOCAL:
        return '<a href="%s" class="readmore_140">COLLECT CAR</a>' % (reverse('job_collect', args=[car.id]))
    else:
        return '<a href="%s" class="readmore_140">COLLECT CAR</a>' % (reverse('job_collect', args=[car.id]))


@register.simple_tag
def ask_for_help_link(user_job, profile, car_no=None, only_link=False):
    if not settings.IS_FB:
        return """
			<p style="font-size: 11px;">Copy link below and send over to your friends via IM or email. Every click makes you closer to the best cars.<br/>
				<input type="text" value="%shelp_me/?link=%s" size="66"/>
			</p>""" % (settings.SITE_URL, user_job.link)

    elif settings.IS_FB:

        if car_no:
            car = user_job.jobs[int(car_no)]
        else:
            car = user_job.jobs[-1]

        # if profile.is_premium:
        # car = user_job.jobs[-1]
        # else:
        # car = user_job.jobs[-2]

        feed_story = {
            'name': car.name,
            'href': '%shelp_me/?link=%s' % (settings.SITE_URL, user_job.link),
            'description': car.desc,
            'media': [{
                'type': 'image',
                'src': '%s%s' % (settings.BASE_MEDIA_URL, car.img.replace('.jpg', '_s.jpg')),
                'href': settings.SITE_URL
            }]
        }
        action_links = [{'text': 'Help me', 'href': '%shelp_me/?link=%s' % (settings.SITE_URL, user_job.link)}]

        ret = """
		<fb:dialog id="help_dialog">
			<fb:dialog-title>Ask for help</fb:dialog-title>	
			<fb:dialog-content>
				<p>
					Post information on your profile and let your friends know you need their help.<br/>
					<span class="readmore" onclick="Facebook.streamPublish(userMsg, feedStory, actionLinks, null, headlineMsg, null, true, null);">PUBLISH</span>
				</p>
				<p>&nbsp;</p>
				<p>
					Alternatively, copy link below and send over to your friends via IM or email. Every click makes you closer to the best cars.<br/>
					<input type="text" value="%shelp_me/?link=%s" size="59"/>
				</p>
			</fb:dialog-content>
			<fb:dialog-button type="button" value="Close" close_dialog=1 />
		</fb:dialog>
		
		<script type="text/javascript"><!--
		var feedStory = %s;
		var actionLinks = %s;
		var userMsg = 'Help me getting this one!';
		var headlineMsg = 'Ask for help';
		//--></script>
		""" % (settings.SITE_URL, user_job.link, json.dumps(feed_story), json.dumps(action_links))

        if not only_link:
            ret += """<span class="readmore_140" clicktoshowdialog="help_dialog">ASK FOR HELP</span>"""
        return ret


@register.simple_tag
def post_car_to_profile(car, profile, txt="POST TO PROFILE", friend=None):
    if len(txt) > 6:
        btn_class = 'readmore_140'
    else:
        btn_class = 'readmore'

    if settings.LOCAL:
        return '<a href="%s" class="%s">%s</a>' % (reverse('post_car_link', args=[car.id]), btn_class, txt)
    else:

        if friend:
            uid = friend['uid']

            from job.models import Garage
            from gift.models import Gift

            garage = Garage.objects.get_by_user(user=profile.user)
            if not garage.has_car(car.id):
                url = settings.SITE_URL
            else:
                item = Gift()
                item.sender = profile.user
                item.car = car
                item.limit_left = 10
                item.is_amount_limited = True
                item.is_active = True
                item.save()
                url = settings.SITE_URL + 'gift/?link=' + item.link

            action_links = [{'text': 'Add it to your own garage', 'href': '%s' % url}]
            user_msg = 'Take it my friend!'
            caption = 'GIVE IT TO %s' % friend['first_name']
            callback = "document.setLocation('http://apps.facebook.com/car_battle/?sent_gift=%s_%s');" % (car.id, uid)
            headline = 'Free Gift'

        else:
            uid = None
            url = settings.SITE_URL
            action_links = [{'text': 'Build your own garage', 'href': '%s' % url}]
            user_msg = 'I own it!'
            caption = txt
            callback = "document.setLocation('http://apps.facebook.com/car_battle/?post_to_profile=%s');" % (car.id)
            headline = 'Show everyone your collection'

        feed_story = {
            'name': car.name,
            'href': url,
            'description': car.desc,
            'media': [{
                'type': 'image',
                'src': '%s%s' % (settings.BASE_MEDIA_URL, car.img.replace('.jpg', '_s.jpg')),
                'href': url
            }]
        }

        return """
		<script type="text/javascript"><!--
		var feedStory_%s = %s;
		var actionLinks_%s = %s;
		var userMsg_%s = '%s';
		var headlineMsg_%s = '%s';
		
		var publish_callback = function(){ %s };
		//--></script>
		<span class="%s" onclick="Facebook.streamPublish(userMsg_%s, feedStory_%s, actionLinks_%s, %s, headlineMsg_%s, publish_callback, true, null);">%s</span>""" % (
            car.id, json.dumps(feed_story), car.id, json.dumps(action_links), car.id, user_msg, car.id, headline,
            callback,
            btn_class, car.id, car.id, car.id, uid or 'null', car.id, caption)


@register.simple_tag
def show_card(car, size='full', w_social=False, counter=False):
    if isinstance(car, (basestring, int, long)):
        car = Car.objects.get_by_id(car)

    social = ''
    if w_social == 'True':
        social = """<tr><td colspan="2" class="social">
		<span style="float: left;"><a href="#" class="readmore">SHARE</a></span>
		<span style="float: left;"><a href="%s" class="readmore">SELL</a></span></td></tr>""" % (
            reverse('auction_sell', args=['car', car.id]))

    if counter:
        car.amnt = "%dx&nbsp;" % int(counter)
    else:
        car.amnt = ''

    if len(car.img):
        car_img = settings.BASE_MEDIA_URL + car.img
    else:
        car_img = settings.BASE_MEDIA_URL + 'cars/0.jpg'

    if size == 'full':
        ret = """<table class="card"><tbody>
			<tr><td colspan="2"><div class="card_title"><div class="card_manuf">%s</div><div class="card_tier card_tier_%s">%s</div></div></td></tr>
			<tr><td colspan="2"><div class="card_subtitle">%s</div></td></tr>
			<tr><td colspan="2" class="card_img"><img src="%s" alt="%s %s %s %s BHP"/></td></tr>""" % (
            car.manuf, car.tier, car.tier, car.name, car_img.replace('.jpg', '_m.jpg'), car.manuf, car.year, car.name,
            car.power_bhp)

        for param in ('year', 'engine', 'power_bhp', 'top_speed', 'sprint_0_100', 'weight', 'power_to_weight'):
            ret += """<tr><th>%s</th><td class="content">%s</td>""" % (
                translate_attr(car, param, 'left'), translate_attr(car, param, 'right'))

        return ret + social + "</tbody></table>"

    if size == 'small':
        return """<table class="card card_tier_%s" style="height: 220px;"><tbody>
			<tr><td colspan="2"><div class="card_title"><div class="card_manuf">%s</div><div class="card_tier card_tier_%s">%s</div></div></td></tr>
			<tr><td colspan="2"><div class="card_subtitle">%s</div></td></tr>
			<tr><td colspan="2"><img src="%s" alt="%s %s %s %s BHP"/></td></tr>
			%s
		</tbody></table>""" % (
            car.tier, car.manuf, car.tier, car.tier, car.name, car_img.replace('.jpg', '_m.jpg'), car.manuf, car.year,
            car.name, car.power_bhp, social)


@register.simple_tag
def show_small_card(car):
    return show_card(car, size='small')


@register.simple_tag
def card(car, shown=None, other_card=None, size='full', tier_battle=False):
    if tier_battle:
        url = 'tier_battle'
    else:
        url = 'battle_user'

    if shown is not None:
        if len(shown) < 3:
            ret = """<table class="card wide"><tbody>
				<tr><td colspan="2"><div class="card_title"><div class="card_manuf">unknown</div><div class="card_tier card_tier_%s">%s</div></div></td></tr>
				<tr><td colspan="2" class="card_img"><img src="%simages/unknown_car.png"/></td></tr>
				<tr><td colspan="2"><div class="card_subtitle">&nbsp;</div></td></tr>
				""" % (car.tier, car.tier, settings.MEDIA_URL)
        else:
            if len(car.img):
                car_img = settings.BASE_MEDIA_URL + car.img
            else:
                car_img = settings.BASE_MEDIA_URL + 'cars/0.jpg'

            ret = """<table class="card"><tbody>
				<tr><td colspan="2"><div class="card_title"><div class="card_manuf">%s</div><div class="card_tier card_tier_%s">%s</div></div></td></tr>
				<tr><td colspan="2"><div class="card_subtitle">%s</div></td></tr>
				<tr><td colspan="2" class="card_img"><img src="%s"/></td></tr>""" % (
                car.manuf, car.tier, car.tier, car.name, car_img.replace('.jpg', '_m.jpg'))

        for param in ('year', 'engine', 'power_bhp', 'top_speed', 'sprint_0_100', 'weight', 'power_to_weight'):
            if param in shown:
                ret += '<tr class="result_%s"><th>%s</th><td class="content">%s</td></tr>' % (
                    car.if_won(other_card, (param,)) + 1, translate_attr(car, param, 'left'),
                    translate_attr(car, param, 'right'))
            else:
                if len(shown) < 3:
                    ret += '<tr><th>%s</th><td class="content"><a href="%s" class="question">&nbsp;&nbsp;&nbsp;</a></td></tr>' % (
                        translate_attr(car, param, 'left'), reverse(url, args=[param]))
                else:
                    ret += '<tr><th>%s</th><td class="content">%s</td></tr>' % (
                        translate_attr(car, param, 'left'), translate_attr(car, param, 'right'))

        ret += '</tbody></table>'
        return ret

    return show_card(car)


@register.simple_tag
def feed_story_js(car, which=None):
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

    if which == 'feed_story':
        return json.dumps(feed_story)
    elif which == 'action_links':
        return json.dumps(action_links)
    return (feed_story, action_links)


@register.simple_tag
def exp_mod(my_lvl, other_lvl):
    if my_lvl > other_lvl:
        sign = '-'
    elif my_lvl == other_lvl:
        sign = ''
    else:
        sign = '+'

    try:
        val = settings.EXP_MOD[sign + str(abs(my_lvl - other_lvl))]
    except KeyError:
        val = settings.EXP_MOD[sign + 'x']

    if val == 0:
        return ''
    return '%s%d%% EXP' % (sign, abs(val))


@register.filter
def kph_to_mph(val):
    return float(val) * 0.62


@register.filter
def mph_to_kph(val):
    return float(val) * 1.61


@register.filter
def kg_to_lbs(val):
    return float(val) * 2.20


@register.filter
def lbs_to_kg(val):
    return float(val) * 0.45


def translate_attr(car, param, s='left'):
    if s == 'left':
        if param == 'sprint_0_100':
            return """<abbr title="0-62 mph">%s</abbr>""" % settings.CARD_PARAMS[param][0]
        else:
            return settings.CARD_PARAMS[param][0]

    else:
        if param == 'top_speed':
            return """<abbr title="%s mph">%s %s</abbr>""" % (
                kph_to_mph(car.__dict__[param]), car.__dict__[param], settings.CARD_PARAMS[param][1])
        elif param == 'weight':
            return """<abbr title="%s lbs">%s %s</abbr>""" % (
                kg_to_lbs(car.__dict__[param]), car.__dict__[param], settings.CARD_PARAMS[param][1])
        else:
            return "%s %s" % (car.__dict__[param], settings.CARD_PARAMS[param][1])


@register.filter
def price_by_tier(tier):
    if tier in ('1', '2', '3', '4', '5'):
        return int(tier) * 2500
    else:
        return 35000


@register.filter
def fb_img_from_url(url):
    try:
        return '%s_m.jpg' % url.split('/')[-2]
    except IndexError:
        return ''
