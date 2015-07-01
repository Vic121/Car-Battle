# -*- coding: utf-8 -*-
import math
import datetime
import time
# from decimal import *
# import re, datetime
# from time import strptime
# from django.utils.translation import ugettext as _
from django.template import Library, Node, TemplateSyntaxError
# from django.template import TOKEN_TEXT, TOKEN_VAR
from django.template.defaultfilters import timeuntil, timesince
from django.core.urlresolvers import reverse as old_reverse
from django.conf import settings
from ..helpers.core import reverse
from ..helpers.slughifi import slughifi

register = Library()


@register.filter
def truncate(value, arg):
    """
    Truncates a string after a given number of chars
    Argument: Number of chars to truncate after
    """
    try:
        length = int(arg)
    except ValueError:  # invalid literal for int()
        return value  # Fail silently.
    if not isinstance(value, basestring):
        value = str(value)
    if (len(value) > length):
        return value[:length] + "..."
    else:
        return value


@register.filter
def EQ(value, arg): return value == arg


@register.filter
def LT(value, arg): return value < arg


@register.filter
def GT(value, arg): return value > arg


@register.filter
def LTE(value, arg): return value <= arg


@register.filter
def GTE(value, arg): return value >= arg


@register.filter
def NE(value, arg): return value != arg


@register.filter
def IS(value, arg): return value is arg


@register.filter
def IS_POSITIVE(value): return value > 0


@register.filter
def IS_NEGATIVE(value): return value < 0


@register.filter
def IN(value, arg): return value in arg


@register.filter
def MINUS(value, arg): return value - arg


@register.filter
def PLUS(value, arg): return value + arg


@register.filter
def MOD(value, arg): return value % arg == 0


@register.filter
def TIMES(value, arg): return float(value) * float(arg)


@register.filter
def DIV(value, arg):
    try:
        return float(value) / float(arg)
    except ZeroDivisionError:
        return 0


@register.filter
def DIV_C(value, arg):
    try:
        return math.ceil(float(value) / float(arg))
    except ZeroDivisionError:
        return 0


@register.filter
def DIV_F(value, arg):
    try:
        return math.floor(float(value) / float(arg))
    except ZeroDivisionError:
        return 0


@register.filter
def INT(value):
    try:
        return int(value)
    except TypeError:
        return 0


@register.filter
def FLOAT(value): return float(value)


@register.filter
def STR(value): return str(value)


@register.filter
def ABS(value): return abs(value)


@register.filter
def REVERSE(value):
    value = list(value)
    value.reverse()
    return value


@register.filter
def HAS_KEY(value, arg): return value.has_key(arg)


@register.filter
def KEY(value, arg):
    try:
        return value[int(arg)]
    except KeyError:
        try:
            return value[str(arg)]
        except KeyError:
            return None
    except ValueError:
        try:
            return value[str(arg)]
        except KeyError:
            return None
        except TypeError:
            return None
    except:
        return None


@register.filter
def KEY_BY_LANG(value, arg):
    if arg in ('pl',):  # supported non-EN languages
        return value[arg]
    else:
        return value['en']


@register.filter
def RAND_KEY(value):
    import random

    return random.choice(value)


@register.filter
def PRITIFY(value):
    try:
        value = int(value)
    except ValueError:
        value = 0
    if value <= 999:
        return value
    elif value <= 9999:
        return "%s,%s" % (str(value)[:1], str(value)[1:])
    elif value <= 99999:
        return "%s,%s" % (str(value)[:2], str(value)[2:])
    elif value <= 999999:
        return "%d%s" % (value / 1000, 'k')
    elif value < 1000000000:
        new_value = value / 1000000.0
        return "%.2f %s" % (new_value, 'million')
    elif value < 1000000000000:
        new_value = value / 1000000000.0
        return "%.2f %s" % (new_value, 'billion')
    if value < 1000000000000000:
        new_value = value / 1000000000000.0
        return "%.2f %s" % (new_value, 'trillion')


@register.filter
def SUM_ITEMS(value, arg): return sum(int(x.__dict__[arg]) for x in value)


@register.filter
def TIME_PLUS_DAYS(value, arg): return value + datetime.timedelta(days=arg)


@register.filter
def TIME_PLUS_HOURS(value, arg): return value + datetime.timedelta(hours=arg)


@register.filter
def TIME_PLUS_MINUTES(value, arg): return value + datetime.timedelta(minutes=arg)


@register.filter
def slug(value): return slughifi(unicode(value))


@register.filter
def timestr(value):
    # def distance_of_time(delta):
    #	if delta < 1:
    #		return 'less than a minute'
    # if delta == 1:
    #	return '1 minute'
    # if delta < 50:
    #	return '%s minutes' % delta
    # if delta < 90:
    #	return 'about one hour'
    # if delta < 1080:
    #	return '%s hours' % int(math.ceil(delta / 60))
    # if delta < 1440:
    #	return 'one day'
    # if delta < 2880:
    #	return 'about one day'

    # days = int(math.ceil(delta / 1440))
    # if days < 31:
    #	return '%s days' % days
    # return 'about %s months' % int(math.ceil(days / 30))

    if type(value) == type(""):
        value = datetime.datetime(*time.strptime(value, "%Y-%m-%d %H:%M:%S")[:6])
    try:
        r = value - datetime.datetime.now()
    except TypeError:
        value = datetime.datetime(*time.strptime(value, "%Y-%m-%d %H:%M:%S")[:6])
        r = value - datetime.datetime.now()

    delta = (r.days * 3600 * 24) + r.seconds

    # distance = distance_of_time(abs(int(delta / 60)))

    if delta > 0:
        return "in %s" % timeuntil(value)
    else:
        return "%s ago" % timesince(value)


@register.filter
def translate(txt, trans_part):
    if len(trans_part) == 0: return txt

    i = 0
    for text in trans_part.split('|'):
        txt = txt.replace('[[%d]]' % i, text)
        i = i + 1
    return txt


@register.filter
def time_h_or_m(time):
    if time > 60:
        return "%sh %s" % (str(time / 60), str(time - 60 * (time / 60)))
    else:
        return time


@register.filter
def to_time(time):
    if time < 60:
        return "00:%s" % time
    else:
        h = math.floor(time / 60)
        if h < 10:
            return "0%d:%d0" % (h, time - (h * 60))
        return "%d:%d" % (h, time - (h * 60))


@register.filter
def from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


@register.filter
def parse_msg_links(msg):
    new_msg = []
    for m in msg.split(' '):
        if m.startswith('@'):
            m = '@<a href="%s">%s</a>' % (reverse('profile', args=[m[1:], ]), m[1:])
        if m.startswith('http://'):
            m = '<a href="%s" target="_blank">%s</a>' % (m, m[7:])
        if m.startswith('www.'):
            m = '<a href="http://%s" target="_blank">%s</a>' % (m, m)

        new_msg.append(m)
    return ' '.join(new_msg)


class FBURLNode(Node):
    def __init__(self, view_name, args, kwargs):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        # fb = settings.IS_FB # or Variable('fb').resolve(context)
        # if settings.IS_FB:
        # reverseFunc = reverse
        # else:
        reverseFunc = old_reverse

        from django.core.urlresolvers import NoReverseMatch

        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        return reverseFunc(self.view_name, args=args, kwargs=kwargs)

        # is below correct?
        try:
            return reverseFunc(self.view_name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            print 'NoReverseMatch'
            try:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                return reverseFunc(project_name + '.' + self.view_name,
                                   args=args, kwargs=kwargs)
            except NoReverseMatch:
                return ''


def fb_url(parser, token):
    """
    Just like Django's url tag, except also works inside Facebook.
    """
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument (path to a view)" % bits[0])

    args = []
    kwargs = {}
    if len(bits) > 2:
        for arg in bits[2:]:
            # if '=' in arg:
            #	k, v = arg.split('=', 1)
            #	k = k.strip()
            #	kwargs[k] = parser.compile_filter(v)
            # else:
            args.append(parser.compile_filter(arg))

    return FBURLNode(bits[1], args, kwargs)


fb_url = register.tag(fb_url)


class AssignNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def render(self, context):
        context[self.name] = self.value.resolve(context, True)
        return ''


def do_assign(parser, token):
    """
    Assign an expression to a variable in the current context.

    Syntax::
        {% assign [name] [value] %}
    Example::
        {% assign list entry.get_related %}

    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    value = parser.compile_filter(bits[2])
    return AssignNode(bits[1], value)


register.tag('assign', do_assign)


@register.tag(name='captureas')
def do_captureas(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)


class CaptureasNode(Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''


@register.filter
def img_replace(arg, val):
    return arg.replace('.jpg', val)


@register.simple_tag
def percent_meter(start, current, end):
    return int(float(int(current) - int(start)) / float(int(end) - int(start)) * 100)


@register.simple_tag
def exp_meter(profile):
    return percent_meter(profile.prev_level_exp, profile.exp, profile.next_level_exp)


@register.filter
def avatar(arg):
    return 'avatars/%s/%s.jpg' % (str(int(arg) / 1000), arg)
