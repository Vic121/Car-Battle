# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand


# from django.db import connection
# from urllib2 import Request, urlopen, URLError, HTTPError
# from BeautifulSoup import BeautifulSoup


class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        from userprofile.models import UserProfile
        from common.models import Car
        from album.models import Album
        from engine.engine import Engine
        from common.models import DummyRequest
        from django.core.urlresolvers import reverse
        from common.helpers.slughifi import slughifi

        profile = UserProfile.objects.get_by_id('1')
        engine = Engine(DummyRequest('1'))
        engine.start()

        # --- Save Achievements

        for key, achieves in engine.achieve.achievements.iteritems():
            type, key = key.split(',')

            for achieve in achieves:
                print type, key, achieve
                achieve.save(type, key)

        # --- Save avatars

        # from shutil import copyfile
        # for p in UserProfile.objects.all():
        # 	path = settings.MEDIA_ROOT + 'avatars/' + str(p.user.id / 1000)
        # 	if not os.path.isdir(path):
        # 		  os.makedirs(path)
        # 	copyfile(settings.MEDIA_ROOT + 'avatars/0.jpg', path + '/' + str(p.user.id) + '.jpg')

        # --- Set up domain

        for p in UserProfile.objects.all():
            if p.domain != '': continue

            if p.partner == 'fb':
                p.domain = 'http://apps.facebook.com/car_battle/'
            else:
                p.domain = 'http://www.car-battle.com/'

            p.save()

        # ---

        # MSG all

        from msg.models import Msg

        txt = "hi, just want to let you know that we rolled out few new features like, if you need assistance just msg me"

        for p in UserProfile.objects.all()[1:]:
            Msg.send.send_to(profile.user, p.user, '@%s %s' % (p.username, txt))

        return

        # ---

        album = Album.objects.get(pk=1)
        car = Car.objects.get_by_id(16333)

        # engine.notify.add(user=profile.user, type='album', key='buy', date=None, stream='Nazwa albumu')
        engine.notify.add(user=profile.user, type='album', key='stick', date=None, stream='%s|%s|%s|%s' % (
            reverse('encyclopedia_car', args=[slughifi(car.manuf), slughifi(car.name), str(car.id)]),
            car.display_short_name(),
            reverse('encyclopedia_album', args=[slughifi(album.name), album.id]),
            album.name
        ))
        # engine.notify.add(user=profile.user, type='album', key='completed', date=None, stream='Nazwa albumu')
