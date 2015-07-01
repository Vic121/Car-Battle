# -*- coding: utf-8 -*-
import os
import re
from PIL import Image

from django.core.management.base import BaseCommand
from django.conf import settings


def do_thumbnails(path):
    # path_dir = path[:path.rfind('.')]

    # im = Image.open(path)
    # im.thumbnail((250, 350), Image.ANTIALIAS)
    # im.save(path + '_l.jpg', "JPEG")
    #
    # im = Image.open(path)
    # im.thumbnail((200, 200), Image.ANTIALIAS)
    # im.save(path + '_m.jpg', "JPEG")
    #
    # im = Image.open(path)
    # im.thumbnail((150, 250), Image.ANTIALIAS)
    # im.save(path + '_s.jpg', "JPEG")

    im = Image.open(path)
    im.thumbnail((64, 64), Image.ANTIALIAS)
    im.save(path + '_x.jpg', "JPEG")

    print 'rebuilt %s' % path


def rethumbnail(filename=None):
    filename_match = re.compile('^.*\d+$')

    if filename is None:
        for filename in os.listdir(os.path.join(settings.MEDIA_ROOT, '..', 'base', 'cars')):
            # if not filename[filename.rfind('/')+1:filename.rfind('.')].isdigit(): continue
            if filename_match.match(filename) is None: continue

            try:
                do_thumbnails(os.path.join(settings.MEDIA_ROOT, '..', 'base', 'cars', filename))
            except IOError, e:
                print 'Error parsing %s. %s' % (filename, e)
    else:
        do_thumbnails(os.path.join(settings.MEDIA_ROOT, '..', 'base', 'cars', filename))


class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) > 0:
            for arg in args:
                rethumbnail(arg)
        else:
            rethumbnail()
