# --- Robberies

# attack, respect, required attack, required respect, max respect, current heat, max heat, job's heat
def get_chance(a, r, ra, rr, mr, ch, mh, jh):
    a_point = get_score(a, ra)
    r_point = get_score(r, rr)

    rep = 0
    rep += a_point
    rep += r_point

    if rep < 0: return 0

    if ch + jh > mh:
        rest = (ch + jh) - mh
        rep -= rest * 10

    if ch >= mh:
        rep = 0

    if rep < 0: return 0
    if rep > 100: return 100
    return int(rep)


def get_score(x, rx):
    x = float(str(x))
    rx = float(str(rx))

    if x * 0.8 >= rx:               return 50
    if x * 0.8 < rx <= x * 0.9: return 48
    if x * 0.9 < rx <= x:       return 45
    if rx * 0.8 < x <= rx * 0.9: return -10
    if rx * 0.9 < x <= rx:       return -5
    return -45


# --- Fight

def get_fight_score(x, rx):
    x = float(str(x))
    rx = float(str(rx))

    if x * 0.8 >= rx:               return 50
    if x * 0.8 < rx <= x * 0.9: return 48
    if x * 0.9 < rx <= x:       return 45
    if rx * 0.8 < x <= rx * 0.9: return 20
    if rx * 0.9 < x <= rx:       return 30
    return 0


def fight(att1, def1, uts1, att2, def2, uts2, gatt1=0, gdef1=0, guts1=0, gatt2=0, gdef2=0, guts2=0):
    """ 1-attacker, 2-defender """
    import random, math

    # defending bonus +20%
    att2, def2 = int(float(att2) * 1.2), int(float(def2) * 1.2)

    att_score, def_score = get_fight_score(att1, att2), get_fight_score(def1, def2)
    chance = int(((float(att_score) + float(def_score) / 2.0) * 2.0))

    rand_chance = random.randint(1, 100)
    if chance < rand_chance:
        result = 2
    else:
        result = 1

    MAX_DIE = 10

    if uts1 == 0 or uts2 == 0:
        die = [0, 0]
    else:
        die = [random.randint(0, math.ceil(uts1 * 0.1)), random.randint(0, math.ceil(uts2 * 0.1))]
        if die[1] > 1 and die[0] > 1 and die[1] > die[0]: die[1] = die[0]
        if die[0] > MAX_DIE: die[0] = MAX_DIE
        if die[1] > MAX_DIE: die[1] = MAX_DIE

    return (result, die[0], die[1])

# --- Moving

import math


def calc_route(start_sect, start, end_sect, end):
    sx1, sy1 = _get_xy(start_sect, 1000)
    sx2, sy2 = _get_xy(end_sect, 1000)
    x1, y1 = _get_xy(start)
    x2, y2 = _get_xy(end)
    tx, ty, tsx, tsy = x1, y1, sx1, sy1

    out_route = []
    in_route = []

    # out sector
    while 1:
        out_route.append((tsx, tsy))

        if tsx == sx2 and tsy == sy2: break
        vx = tsx - sx2
        vy = tsy - sy2

        if vx > 0:
            tsx -= 1  # left
            continue
        elif vx < 0:
            tsx += 1  # right
            continue
        elif vx == 0:
            pass

        if vy > 0:
            tsy -= 1  # up
            continue
        elif vy < 0:
            tsy += 1  # down
            continue
        elif vy == 0:
            pass

    # in sector
    while 1:
        in_route.append((tx, ty))

        if tx == x2 and ty == y2: break
        vx = tx - x2
        vy = ty - y2

        if vx > 0:
            tx -= 1  # left
            continue
        elif vx < 0:
            tx += 1  # right
            continue
        elif vx == 0:
            pass

        if vy > 0:
            ty -= 1  # up
            continue
        elif vy < 0:
            ty += 1  # down
            continue
        elif vy == 0:
            pass

    return len(out_route[1:]) * 10 + len(in_route)


def _get_y(c, max=10):
    return int(math.ceil(float(c) / max))


def _get_x(c, max=10):
    return c - (_get_y(c, max) * max) + max


def _get_xy(c, max=10):
    return (_get_x(c, max), _get_y(c, max))


def _get_slot(x, y, max=10):
    return ((y * max) + x) - max
