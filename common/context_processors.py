from django.conf import settings

import datetime

# from django.template.loader import render_to_string

# pyfacebook
def messages(request):
    """Returns messages similar to ``django.contrib.auth.context_processors.auth``."""
    if hasattr(request, 'facebook') and hasattr(request.engine, 'user'):
        from common.models import Message

        messages = Message.objects.get_and_delete_all(uid=request.facebook.uid)
        return {'messages': messages}
    return {}


def base(request):
    arr = {'base': 'base', 'settings': settings, 'base_page': 'base_page'}

    if settings.PROJECT_NAME == 'Car Battle':
        from userprofile.models import UserProfile
        from common.models import Car

        top_manufs = Car.objects.raw(
            'SELECT id, COUNT(*) AS rows, manuf FROM car WHERE is_active=1 AND in_battle=1 AND is_active_in_battle=1 GROUP BY manuf ORDER BY rows DESC LIMIT 7')
        all_cars = Car.objects.raw(
            'SELECT id, COUNT(*) AS rows FROM car WHERE is_active=1 AND in_battle=1 AND is_active_in_battle=1')[0].rows

        if hasattr(request.engine, 'user'):
            base_page = 'base'
        else:
            base_page = 'base_page'

        arr = {'base': 'base', 'settings': settings, 'base_page': base_page,
               'top_players': UserProfile.objects.get_leaderboard(7), 'top_manufs': top_manufs, 'all_cars': all_cars}

    elif settings.PROJECT_NAME == 'Scores':
        top_users_month = {
            'Premiership': request.engine.rank.top_users('month', 1),
            'Bundesliga': request.engine.rank.top_users('month', 6),
            'Ligue 1': request.engine.rank.top_users('month', 5),
            'Serie A': request.engine.rank.top_users('month', 3),
            'Primera Division': request.engine.rank.top_users('month', 4),
            'Champions League': request.engine.rank.top_users('month', 9),
            'UEFA Cup': request.engine.rank.top_users('month', 12),
        }

        arr = {'base': 'base_3k', 'settings': settings, 'base_2k': 'base_2k',
               'top_users_overall': request.engine.rank.top_users('overall'), 'top_users_month': top_users_month,
               'leagues': (
                   'Premiership', 'Bundesliga', 'Ligue 1', 'Serie A', 'Primera Division', 'Champions League',
                   'UEFA Cup')}

    elif settings.PROJECT_NAME in ('Crime Corp',):
        if hasattr(request.engine, 'user'):
            base_page = 'base'
        else:
            base_page = 'base_page'

        arr = {'base': 'base', 'settings': settings, 'base_page': base_page}

    for k, v in arr.iteritems():
        if not k.startswith('base'): continue
        if request.engine.IS_PARTNER:
            arr[k] = v + '_partner.html'
        elif not request.engine.IS_FB:
            arr[k] = v + '.html'
        else:
            arr[k] = v + '.fbml'

    arr['today'] = datetime.date.today()
    return arr
