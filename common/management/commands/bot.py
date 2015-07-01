# -*- coding: utf-8 -*-
import datetime
# from optparse import make_option
import MySQLdb as _mysql
from django.conf import settings
# from django.db import connection
from django.core.management.base import BaseCommand
from common.others.jabberbot import JabberBot, botcmd


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.bot = Bot(settings.IM['jabber_bot']['username'], settings.IM['jabber_bot']['password'])
        self.bot.serve_forever()


class Bot(JabberBot):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self.db = None
        self.games = ('crimecorp', 'garage')

    def query(self, query):
        # cursor = connection.cursor()
        # c = cursor.execute(query)
        try:
            c = self.db.cursor()
            c.execute(query)
            f = c.fetchall()
            if len(f) == 1:
                if (len(f[0]) == 1):
                    return f[0][0]
                return f[0]
            return f
        except Exception, e:
            self.send('marek@madfb.com', 'Blad MySQL (%s) / %s' % (query, e))
            return ()

    # --- Basic server stats

    @botcmd
    def load(self, mess, args):
        """Displays information about the server"""
        loadavg = open('/proc/loadavg').read().strip()

        return 'Load: %s' % (loadavg,)

    @botcmd
    def time(self, mess, args):
        """Displays current server time"""
        return str(datetime.datetime.now())

    # --- Game

    @botcmd
    def game(self, mess, args):
        "Switch current game. Possible options: crimecorp and garage"
        args = args.strip()

        if args in self.games:
            self.game = args
            self.db = _mysql.connect('localhost', settings.DATABASE_USER, settings.DATABASE_PASSWORD,
                                     settings.DATABASE_NAME)
            return 'game switched to %s' % self.game
        else:
            return 'unknown game'

    @botcmd
    def summary(self, mess, args):
        """Short summary for all games"""
        if not self.db: self.game('', 'crimecorp')

        ret = ''
        for game in self.games:
            q = self.query(
                'SELECT FROM_DAYS(TO_DAYS(created_at)) as day, COUNT(*) as sum FROM %s.user GROUP BY day ORDER BY created_at DESC LIMIT 1' % game)
            ret += 'game: %s / %s - %s of %s\n' % (
                game, q[0], q[1], self.query('SELECT COUNT(*) as sum FROM %s.user' % game))
        return ret

    @botcmd
    def stats(self, mess, args):
        """Basic stats for current game"""
        if not self.db: return 'Select game first!'

        ret = ''
        for day in self.query(
                        'SELECT FROM_DAYS(TO_DAYS(created_at)) as day, COUNT(*) as sum FROM %s.user GROUP BY day ORDER BY created_at DESC LIMIT 7' % self.game):
            if args == 'more' and self.game != 'crimecorp':
                users = []
                for user in self.query(
                                'SELECT first_name, last_name FROM %s.user WHERE created_at BETWEEN "%s 00:00:00" AND "%s 23:59:59" ORDER BY created_at DESC LIMIT 100' % (
                                self.game, day[0], day[0])):
                    users.append('%s %s' % (user[0], user[1]))
                ret += "%s (%s)\n%s\n\n" % (str(day[0]), day[1], ', '.join(users))
            else:
                ret += "%s (%s)\n" % (str(day[0]), day[1])

        ret += "\nRazem: %d" % (self.query('SELECT COUNT(*) as sum FROM %s.user' % self.game))
        return ret
