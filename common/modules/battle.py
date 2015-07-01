# -*- coding: utf-8 -*-
import random
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from battle.models import Battle as BattleModel


class Battle(object):
    def __init__(self, engine):
        self.engine = engine
        self.battle = None
        self.cards_per_battle = settings.REQ_CARDS_IN_BATTLE

    def get_player(self, user=None):
        obj = {}
        obj['cards'] = self.engine.user.get_garage(user)
        del obj['cards'].cars['P']
        del obj['cards'].cars['U']
        del obj['cards'].cars['N']
        del obj['cards'].cars['X']
        obj['drawed'] = self.draw_cards(obj['cards'].cars)
        return obj

    def get_current_cards(self):
        try:
            return self.battle.left_cards[self.battle.card - 1], self.battle.right_cards[self.battle.card - 1], \
                   self.battle.states[str(self.battle.right_cards[self.battle.card - 1].id)]
        except:
            logging.critical("""Tried card: %d on battle_id: %d (left: %s; right: %s)""" % (
                self.battle.card, self.battle.id, self.battle.left_cards, self.battle.right_cards))
            self.battle.is_active = False
            self.battle.save()
            return

    def get_summary(self, full=False):

        def msg_by_result(res):
            if len(res) == 1:
                if res == 'W':
                    return "<p>Won this round<p>"
                elif res == 'D':
                    return "<p>Draw</p>"
                elif res == 'L':  # Lost
                    return "<p>Lost this round</p>"
            else:
                words = ['first', 'second', 'third']
                ret = ""
                i = 0
                score = 0
                for letter in res:
                    if letter == 'W':
                        score += 1
                        ret += "<p>Won %s round<p>" % words[i]
                    elif letter == 'D':
                        score += 0
                        ret += "<p>Draw in %s round</p>" % words[i]
                    elif letter == 'L':  # Lost
                        score -= 1
                        ret += "<p>Lost %s round</p>" % words[i]
                    i += 1

                if score >= 1:
                    result = 'WON'
                    self.engine.user.profile.earn('cash', score * 500)
                    self.engine.user.profile.save()
                elif score == 0:
                    result = 'DRAW'
                    self.engine.user.profile.earn('cash', 250)
                    self.engine.user.profile.save()
                elif score < 0:
                    result = 'LOST'

                ret += "<br/><p>Result: %s</p>" % result
                return ret

        if full:
            prev_exp, prev_lvl = self.engine.user.profile.exp, self.engine.user.profile.level
            self.battle.end_session(self.engine)
            self.engine.user.refresh_profile()

            # tier battle
            if len(self.battle.result) == 1 and self.battle.result == 'W':
                from job.models import UserJob

                self.engine.user.profile.job_tier += 1
                self.user_job = UserJob.objects.get_by_user(user=self.engine.user.user,
                                                            profile=self.engine.user.profile)
                if self.user_job is None:
                    return 'You hitted limit of daily jobs, patience!'

                self.user_job.last_tier += 1
                self.engine.user.profile.save()
                self.user_job.save()

            msg = "<p>%s</p>" % msg_by_result(self.battle.result)
            msg += "<p>EXP +%d</p>" % (int(self.engine.user.profile.exp) - prev_exp)
            if prev_lvl < self.engine.user.profile.level:
                msg += "<p>PROMOTED! You're now on level %d!</p>" % self.engine.user.profile.level

            return msg

        try:
            res = self.battle.result[self.battle.card - 1]
        except IndexError:
            return None

        return msg_by_result(res)

    def next_step(self, param):
        if self.battle is None: return None
        self.battle.next_step(param)

    def draw_cards(self, cards, force_tier=None):
        if self.cards_per_battle > len(cards): return

        i = 1
        cs = []
        while len(cs) < self.cards_per_battle:
            r = force_tier or random.choice(cards.keys())
            if len(cards[r]) > 0:
                s = random.randint(0, len(cards[r]) - 1)
                cs.append(cards[r][s][0])
                del cards[r][s]

            if force_tier:
                i += 1
                if i % 2 == 0: force_tier += 1
                force_tier *= -1

        return cs

    def start_or_resume(self, opp, rounds=settings.BATTLE_ROUNDS):
        self.battle = BattleModel.objects.get_by_user(user=self.engine.user.user, rounds=rounds)
        if self.battle is not None:
            return self.battle

        self.cards_per_battle = int(rounds)
        if self.engine.user.profile.energy < settings.ENERGY['new_battle']:
            return "Not enough energy. Wait until you have at least %d energy points or <span style='font-size: 13px'><a href='%s'>fill it</a> right away</span>" % (
                settings.ENERGY['new_battle'], reverse('store'))

        battle = BattleModel()
        battle.rounds = self.cards_per_battle

        if int(rounds) == 1:
            battle.new_session(self.engine.user.user, opp, [random.choice(self.get_player()['drawed'])],
                               [random.choice(self.get_player(opp)['drawed'])])
        elif int(rounds) == 3:
            battle.new_session(self.engine.user.user, opp, self.get_player()['drawed'], self.get_player(opp)['drawed'])
        else:
            logging.critical("Unknown rounds no. %d" % int(rounds))

        self.engine.user.profile.energy -= settings.ENERGY['new_battle']
        self.engine.user.profile.save()

        self.battle = battle
        return battle

    def resume_current(self, rounds):
        self.battle = BattleModel.objects.get_by_user(user=self.engine.user.user, rounds=rounds)
        return self.battle
