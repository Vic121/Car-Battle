# -*- coding: UTF-8 -*-
# ==============================================================================================================
#									G A M E    S E T T I N G S
# ==============================================================================================================

DEFAULT_FRIEND = '1'
DEFAULT_STATS = {
    'energy': 100,
    'level': 1,
    'exp': 0,
    'cash': 0,
    'credits': 0,
    'energy': 100,
    'prev_level_exp': 0,
    'next_level_exp': 100,
}

DEFAULT_MEMBERS_PER_PAGE = 10
DEFAULT_AUCTIONS_PER_PAGE = 20
DEFAULT_OPPONENTS_PER_PAGE = 20
DEFAULT_MSGS_PER_PAGE = 20
DEFAULT_CARS_PER_ENCYCLOPEDIA_PAGE = 16
DEFAULT_FRIENDS_PER_GIFT_PAGE = 20
ACHIEVEMENTS_ON_DASH = 3
LOW_HEAT_EVERY_SECONDS = 240

REQ_CARDS_IN_BATTLE = 3
BATTLE_ROUNDS = 3
PARTNER_SHARE = '0.1'

MAX_ROUNDS_A_DAY = 3
MAX_WISHLIST_SIZE = 6

# exp per action
EXP = {
    'attacker_win': 20,
    'attacker_draw': 10,
    'attacker_lost': 5,
    'defender_win': 10,
    'defender_draw': 5,
    'defender_lost': 2,
    'collect_car_tier_1': 10,
    'collect_car_tier_2': 15,
    'collect_car_tier_3': 30,
    'collect_car_tier_4': 45,
    'collect_car_tier_5': 60,
    'collect_car_tier_6': 80,
    'collect_car_tier_u': 100,
    'collect_car_tier_x': 85,
    'collect_car_tier_p': 100,
    'collect_car_tier_n': 50,
    'helper': 1,
}

# percentage modifiers of exp based on differnce in players levels
EXP_MOD = {
    '+1': 10, '+2': 15, '+3': 25, '+x': 25,
    '0': 0,
    '-1': -10, '-2': -15, '-3': -25, '-x': -25,
}

ADD_ENERGY_EVERY_SECONDS = 180
MAX_ENERGY = 100
ENERGY = {
    'new_battle': 5,
}

TIERS = ('1', '2', '3', '4', '5', '6', 'U', 'P', 'X', 'N')
CAR_GROUPS = (
    ('1', 'Tier 1'), ('2', 'Tier 2'), ('3', 'Tier 3'), ('4', 'Tier 4'), ('5', 'Tier 5'), ('6', 'Tier 6'),
    ('U', 'Unique'),
    ('P', 'Prototype'), ('X', 'Modified'), ('N', 'Non-Playable'))

TIER_INCOME = {'1': 1000, '2': 2000, '3': 4000, '4': 8000, '5': 16000, '6': 20000}
TIER_BATTLE_PLAYERS = {'1': 65, '2': 66, '3': 67, '4': 68, '5': 69, '6': 70}

ALBUM_TABS = ['Incomplete', 'Full', 'Empty', 'Buy more']

JOB_HELPERS_NEEDED = (3, 3, 4, 5, 5, 2)
JOB_HELPERS_NEEDED_CUMM = (3, 6, 10, 15, 20, 22)

PRICING = {
    'premium': 30,
    'cars': {'starter': 0, '3': 20, '3+': 30, '5': 40, '5+': 50},
}

PRICING_CAR_CONFIG = {
    # 'nazwa' => (tier1, tier2, tier3) // szanse na dany tier
    'starter': (2, 3),
    '3': (4, 4, 4, 4, 4, 4, 5, 5, 5, 6),  # 4=.6, 5=.3, 6=.1
    '3+': (4, 4, 4, 4, 5, 5, 5, 5, 6, 6),  # 4=.4, 5=.4, 6=.2
    '5': (4, 4, 4, 4, 4, 4, 5, 5, 5, 6),  # 4=.6, 5=.3, 6=.1
    '5+': (4, 4, 4, 4, 5, 5, 5, 5, 6, 6),  # 4=.4, 5=.4, 6=.2
}

CHART_MAX_SHIFT = 0.05

CARD_PARAMS = {
    'year': ['Year', ''],
    'engine': ['Engine Cap.', 'cm<sup>3</sup>'],
    'power_bhp': ['Power', 'BHP'],
    'top_speed': ['Top Speed', 'km/h'],
    'sprint_0_100': ['0-100 km/h', 'sec'],
    'weight': ['Weight', 'kg'],
    'power_to_weight': ['BHP per ton', ''],
}

HINTS = {

}

HOW_TO_PLAY = ['jobs', 'garage', 'battle', 'store', 'album', 'auction', 'invite', 'free gift', 'fight']

ACHIEVEMENT_DESC = {
    'Celebrity': '',
    '60s': '',
    '70s': '',
    '80s': '',
    '90s': '',
    'Grandpa': '',
    # ...
}
