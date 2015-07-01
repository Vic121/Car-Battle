# -*- coding: utf-8 -*-
import simplejson as json
from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User

import cPickle as pickle
from userprofile.models import UserProfile
from common.models import Car


class BattleManager(models.Manager):
    def get_by_user(self, user, rounds):
        try:
            return self.get(attacker=user, rounds=rounds, is_active=True)
        except Battle.DoesNotExist:
            return None
        except Battle.MultipleObjectsReturned:
            battles = self.filter(attacker=user, rounds=rounds, is_active=True).order_by('created_at')
            for battle in battles[1:]:
                battle.is_active = False
                battle.save()
            return battles[0]
            logging.error('Multiple battle for %s, rounds %s' % (user, rounds))


class Battle(models.Model):
    attacker = models.ForeignKey(User, related_name='attacker')
    defender = models.ForeignKey(User, related_name='defender')

    card = models.PositiveSmallIntegerField(default=0)  # ktora karta z koleji
    rounds = models.PositiveSmallIntegerField(default=0)  # ile kart w sumie
    step = models.PositiveSmallIntegerField(default=0)  # ktory krok z koleji
    result = models.CharField(max_length=3)  # np. WLW - win lost win

    left_card = models.CharField(max_length=35)
    right_card = models.CharField(max_length=35)
    state = models.CharField(max_length=255, default='')

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BattleManager()

    class Meta:
        db_table = 'battle'
        verbose_name = 'Battle'

    def __unicode__(self):
        return 'Battle between %s and %s' % (self.attacker, self.defender)

    def __getattr__(self, name):
        if name == 'cards':
            if not self.card: return {}
            return json.loads(self.card)
        if name == 'states':
            if not self.state: return {}
            return json.loads(self.state)
        if name == 'left_cards':
            if not self.left_card: return []
            return [Car.objects.get_by_id(id) for id in self.left_card.split(',')]
        if name == 'right_cards':
            if not self.left_card: return []
            return [Car.objects.get_by_id(id) for id in self.right_card.split(',')]
        else:
            return self.__getattribute__(name)

    def save(self):
        super(Battle, self).save()
        key = 'battle_%s' % (self.pk)
        cache.set(key, pickle.dumps(self))

    def delete(self):
        k = int(self.pk)
        super(Battle, self).delete()
        cache.delete('battle_%s' % (k))

    def new_session(self, att, opp, att_cards, opp_cards):
        cards = {}
        for c in opp_cards:
            cards[str(c.id)] = ()

        self.attacker = att
        self.defender = opp
        self.card = 1
        self.step = 1
        self.left_card = ','.join([str(c.id) for c in att_cards])
        self.right_card = ','.join([str(c.id) for c in opp_cards])
        self.state = json.dumps(cards)
        self.is_active = True
        self.save()

    def next_step(self, attr):
        state = self.states
        if len(state[str(self.right_cards[self.card - 1].id)]) == 0:
            state[str(self.right_cards[self.card - 1].id)] = (attr,)
        else:
            if attr in state[str(self.right_cards[self.card - 1].id)]: return None
            state[str(self.right_cards[self.card - 1].id)].append(attr)

        self.state = json.dumps(state)

        if self.step == 3:
            self.result += self._get_result()

        self.step += 1
        self.save()

    def _get_result(self):
        result = self.left_cards[self.card - 1].if_won(self.right_cards[self.card - 1],
                                                       self.states[str(self.right_cards[self.card - 1].id)])
        if result > 0:
            return 'W'
        elif result < 0:
            return 'L'
        else:
            return 'D'

    def next_card(self):
        self.step = 1
        self.card += 1
        self.save()

    def end_session(self, engine=None):
        from common.helpers.core import exp_mod
        from common.models import DummyRequest
        from engine.engine import Engine

        self.is_active = False
        self.save()

        attacker, defender = UserProfile.objects.get_by_id(self.attacker.id), UserProfile.objects.get_by_id(
            self.defender.id)
        attacker_mod, defender_mod = exp_mod(attacker.level, defender.level), exp_mod(defender.level, attacker.level)
        attacker_engine = engine
        defender_engine = Engine(DummyRequest(self.defender.id))
        defender_engine.start()

        for r in self.result:
            if r == 'W':
                v1 = settings.EXP['attacker_win'] + (settings.EXP['attacker_win'] * attacker_mod)
                v2 = settings.EXP['defender_lost'] + (settings.EXP['defender_lost'] * defender_mod)

                attacker_engine.notify.add(user=attacker.user, type='fight', key='win', date='today')
                attacker_engine.notify.add(user=attacker.user, type='fight', key='win', date=None)
                defender_engine.notify.add(user=defender.user, type='fight', key='lost', date='today')
                defender_engine.notify.add(user=defender.user, type='fight', key='lost', date=None)
            elif r == 'D':
                v1 = settings.EXP['attacker_draw'] + (settings.EXP['attacker_draw'] * attacker_mod)
                v2 = settings.EXP['defender_draw'] + (settings.EXP['defender_draw'] * defender_mod)

                attacker_engine.notify.add(user=attacker.user, type='fight', key='draw', date='today')
                attacker_engine.notify.add(user=attacker.user, type='fight', key='draw', date=None)
                defender_engine.notify.add(user=defender.user, type='fight', key='draw', date='today')
                defender_engine.notify.add(user=defender.user, type='fight', key='draw', date=None)
            elif r == 'L':
                v1 = settings.EXP['attacker_lost'] + (settings.EXP['attacker_lost'] * attacker_mod)
                v2 = settings.EXP['defender_win'] + (settings.EXP['defender_win'] * defender_mod)

                attacker_engine.notify.add(user=attacker.user, type='fight', key='lost', date='today')
                attacker_engine.notify.add(user=attacker.user, type='fight', key='lost', date=None)
                defender_engine.notify.add(user=defender.user, type='fight', key='win', date='today')
                defender_engine.notify.add(user=defender.user, type='fight', key='win', date=None)

            attacker.earn('exp', int(v1), False, engine=attacker_engine)
            defender.earn('exp', int(v2), False, engine=defender_engine)

        attacker.job_id = 0
        attacker.save()
        defender.save()
