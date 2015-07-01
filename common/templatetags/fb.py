# -*- coding: utf-8 -*-
# import os, sys, datetime
# from django.template.loader import render_to_string
from django.template import Library
from django.conf import settings

register = Library()

userProfileView = 'UserProfile'


class FbNameNode(Node):
    def __init__(self, user, args, kwArgs):
        self.user = template.Variable(user)
        self.args = args
        self.kwArgs = kwArgs

    def getBoolArg(self, name, default=False):
        val = self.kwArgs.get(name, default)
        if type(val) is not bool:
            return (val.lower() == 'true')
        return val

    def render(self, context):
        user = self.user.resolve(context)
        fb = template.Variable('fb').resolve(context)
        loggedInUser = template.Variable('user').resolve(context)
        request = template.Variable('request').resolve(context)
        if fb:
            fbUserId = UserFbId(user)
            if fbUserId:
                # In Facebook
                internalLink = False
                ret = '<fb:name uid="%s" ' % fbUserId
                for item, val in self.kwArgs.items():
                    if item == 'linked' and val == 'internal':
                        internalLink = True
                        ret += 'linked="false" '
                    else:
                        if type(val) is bool:
                            if val:
                                val = 'true'
                            else:
                                val = 'false'
                        ret += '%s="%s" ' % (item, val)
                ret += '/>'
                if internalLink:
                    ret = '<a href="%s">%s</a>' % (fbReverse(userProfileView, [user.id]), ret)
                return mark_safe(ret)
        # Not in Facebook
        if self.getBoolArg('useyou', True) and user == loggedInUser:
            if self.getBoolArg('capitalize'):
                ret = 'You'
            else:
                ret = 'you'
            if self.getBoolArg('possessive'):
                ret += 'r'
            elif self.getBoolArg('reflexive'):
                ret += 'rself'
                # ES: How to handle subjectid?
        else:
            ret = UserDisplayName(user)
            if self.getBoolArg('firstnameonly'):
                ret = user.first_name or user.username
            if self.getBoolArg('lastnameonly'):
                ret = user.last_name or user.username
            if self.getBoolArg('possessive'):
                ret += "'s"
        if self.getBoolArg('linked', True) or self.kwArgs.get('linked', None) == 'internal':
            ret = '<a href="%s">%s</a>' % \
                  (makeReverse(request, userProfileView, args=[user.id]),
                   ret)
        return mark_safe(ret)


@register.tag
def fbName(parser, token):
    '''
    Returns the name for the given user, based on the parameters.

    Acts much like the fb:name FBML tag, except can work in or out of
    Facebook.
    '''
    try:
        bits = token.split_contents()[1:]
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires at least 1 argument: the user (%s)" % \
                                            (token.contents.split()[0], token.split_contents())
    args = []
    kwArgs = {}
    for b in bits:
        if '=' in b:
            name, val = b.split('=', 1)
            kwArgs[name.strip()] = val.strip()
        else:
            args.append(b.strip())
    if len(args) < 1:
        raise template.TemplateSyntaxError, "%r tag requires at least one argument: the user" % \
                                            token.contents.split()[0]

    return FbNameNode(args[0], args[1:], kwArgs)


def UserFbId(user):
    try:
        return UserProfile.objects.get(user=user).facebookId
    except UserProfile.DoesNotExist:
        return None


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
        re
    return (feed_story, action_links)
