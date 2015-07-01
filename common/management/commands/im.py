# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from common.im.blip import Blip
from common.im.twitter import Twitter


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--long', '-l', dest='long',
                    help='Help for the long options'),
    )
    help = 'nazwa_kanalu wiadomosc'

    def handle(self, *args, **options):
        if len(args) != 2:
            print 'Wrong argument list'
            return

        if args[0].lower() == 'blip':
            m = Blip()
        elif args[0].lower() in ('tw', 'twitter'):
            m = Twitter()
        m.send(args[1].strip())
