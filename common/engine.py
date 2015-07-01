# -*- coding: utf-8 -*-
from hashlib import md5

from django.conf import settings
from django.http import HttpResponseRedirect
from django import template

# from common.models import Task
from common.helpers.slughifi import slughifi


class Engine(object):
    def __init__(self, request, source='default'):
        self.request = request
        self.source = source
        self.settings = settings
        self.module = None
        self.summary = request.session.get('summary') or {}
        self.IS_FB = None  # Facebook
        self.IS_FBC = False  # Facebook Connect
        self.IS_TW = False  # Twitter
        self.IS_PARTNER = False  # White Label
        self.IS_TAB = False  # Facebook Tab

        # default modules
        self.register('log')

    # if request.session.has_key('summary'): del request.session['summary']

    def start(self):

        if self.request.user.is_authenticated():
            self.register('user')
            self.register('msg')
            self.register('stream')

        # self.register('achieve')
        self.register('notify')

    def register(self, name, *args, **argv):
        if hasattr(self, name): return

        try:
            plug = __import__('modules.%s' % name, globals(), locals(), [name.capitalize(), ], -1)
            self.__dict__[name] = plug.__dict__[name.capitalize()](self, *args, **argv)
        except ImportError, e:
            raise e
        except KeyError, e:
            raise e

    def unregister(self, name):
        try:
            del self.__dict__[name]
        except KeyError, e:
            raise e

    def redirect(self, page):
        # if self.IS_FB:
        # return self.request.facebook.redirect(page)
        # else:
        return HttpResponseRedirect(page)

    def slughifi(self, value):
        return slughifi(value)

    def md5(self, value):
        h = md5()
        h.update(value)
        return h.hexdigest()

    def query(self, query, param=None):
        from django.db import connection

        cursor = connection.cursor()
        if param is None:
            return cursor.execute(query)
        else:
            return cursor.execute(query, param)

    # def add_task(self, source='engine', task='', comment=''):
    # 	t = Task()
    # 	t.user_id = self.user.user.id
    # 	t.source = source
    # 	t.task = task
    # 	t.comment = comment
    # 	t.save()

    def add_summary(self, module, item, value):
        if not self.summary.has_key(module):
            self.summary[module] = {}
        if not self.summary[module].has_key(item):
            self.summary[module][item] = []
        self.summary[module][item].append(value)

        self.request.session['summary'] = self.summary

    def get_summary(self):
        if len(self.summary.keys()) == 0: return ''

        data = {}
        for k, v in self.summary.iteritems():
            data_item = []
            for key, value in v.iteritems():
                s = template.loader.render_to_string('partials/summary/%s,%s.html' % (k, key), {
                    'items': value,
                })
                data_item.append('<p>%s</p>' % s)
            data[k] = ''.join(data_item)

        del self.request.session['summary']
        return data

    def send_mail(self, recipients, subject, message='', mime='text'):
        if isinstance(recipients, basestring):
            recipients = [recipients]

        if mime == 'html':
            from django.core.mail import EmailMessage

            msg = EmailMessage(subject, message, 'Car Battle <noreply@car-battle.com>', recipients)
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        else:
            from django.core.mail import send_mail

            send_mail(subject, message, 'Car Battle <noreply@car-battle.com>', recipients, fail_silently=True)


template.add_to_builtins('django.contrib.humanize.templatetags.humanize')
template.add_to_builtins('common.templatetags.common')
template.add_to_builtins('common.templatetags._gta')
