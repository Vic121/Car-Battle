# -*- coding: utf-8 -*-
from django.conf import settings

from annoying.decorators import render_to
from common.helpers.core import reverse


@render_to('battle/index.fbml')
def index(request):
    request.engine.register('battle')
    request.engine.module = 'battle'

    opponents = request.engine.user.profile.get_list_of_opponents()

    return {
        'opponents': opponents,
    }


@render_to('battle/details.fbml')
def details(request, user_id):
    request.engine.register('battle')
    request.engine.module = 'battle'

    return {

    }


@render_to('battle/fight.fbml')
def battle(request, user_id=None, param=None):
    request.engine.module = 'battle'

    if user_id == str(request.engine.user.user.id): return request.engine.redirect(reverse('battle'))

    request.engine.user.get_garage()
    if request.engine.user.garage.count() < settings.REQ_CARDS_IN_BATTLE:
        request.engine.log.message(
            message="You need at least %d cars to fight against other players." % settings.REQ_CARDS_IN_BATTLE)
        return request.engine.redirect(reverse('battle'))

    request.engine.register('battle')
    summary = None

    if user_id is not None:
        profile = request.engine.user.get_by_id(user_id=user_id)
        battle = request.engine.battle.start_or_resume(profile.user)

        if isinstance(battle, basestring):  # validation
            request.engine.log.message(message=battle)
            return request.engine.redirect(reverse('battle'))

        if battle.step == 4 and battle.card < 3 and request.GET.has_key('next'):
            battle.next_card()
        # elif battle.step == 4 and battle.card == 3 and request.GET.has_key('next'):
        # 	return request.engine.redirect(reverse('battle'))

        if battle.step == 4 and battle.card == 3:
            summary = request.engine.battle.get_summary(True)
        elif battle.step == 4 and battle.card < 3:
            summary = request.engine.battle.get_summary()

    else:
        battle = request.engine.battle.resume_current(3)
        if battle is None:
            request.engine.log.message(
                message="Error occured during battle, our staff were informed. Really sorry, we'll fix it soon.")
            return request.engine.redirect(reverse('battle'))

        battle.next_step(param)
        return request.engine.redirect(reverse('battle_user', args=[battle.defender.id]))

    try:
        attacker, defender, shown = request.engine.battle.get_current_cards()
    except TypeError:
        request.engine.log.message(
            message="Error occured during battle, our staff were informed. Really sorry, we'll fix it soon.")
        return request.engine.redirect(reverse('battle'))

    return {
        'attacker': attacker,
        'defender': defender,
        'shown': shown,
        'battle': battle,
        'last_step': battle.step > 3,
        'last_card': battle.card == 3 and battle.step == 4,
        'user_id': user_id,
        'defender_profile': profile,
        'tier_battle': False,
        'summary': summary,
    }


@render_to('battle/fight.fbml')
def tier_battle(request, param=None):
    request.engine.module = 'battle'

    request.engine.user.get_garage()
    if not request.engine.user.garage.count() >= settings.REQ_CARDS_IN_BATTLE:
        request.engine.log.message(
            message="You need at least %d cars to fight against other players." % settings.REQ_CARDS_IN_BATTLE)
        return request.engine.redirect(reverse('jobs'))

    request.engine.register('battle')
    summary = None

    if not param:
        defender = request.engine.user.get_by_id(
            user_id=settings.TIER_BATTLE_PLAYERS[str(request.engine.user.profile.job_tier + 1)]).user
        battle = request.engine.battle.start_or_resume(defender, 1)

        if isinstance(battle, basestring):  # validation
            request.engine.log.message(message=battle)
            return request.engine.redirect(reverse('jobs'))

        if battle.step == 4:
            summary = request.engine.battle.get_summary(True)

    else:
        battle = request.engine.battle.resume_current(1)
        battle.next_step(param)
        return request.engine.redirect(reverse('tier_battle'))

    attacker, defender, shown = request.engine.battle.get_current_cards()

    return {
        'attacker': attacker,
        'defender': defender,
        'shown': shown,
        'battle': battle,
        'last_step': battle.step > 3,
        'last_card': battle.card == 1 and battle.step == 4,
        'defender_profile': 'random player',
        'tier_battle': True,
        'summary': summary,
    }
