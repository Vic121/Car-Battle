import random
from decimal import *

from django.conf import settings


def __calc(max_shift, tend):
    # getcontext().prec = 3
    # getcontext().rounding = ROUND_UP

    direct = Decimal(str(random.randint(1, max_shift * 1000))) / Decimal(1000)
    if tend != 0 and -1 <= tend <= 1:
        direct = direct * tend
    return direct


def calc(start_val, max_shift=0.05, elements=120, tendency=None, hard_tendency=None):
    # getcontext().prec = 3
    # getcontext().rounding = ROUND_UP

    max_shift = max_shift or settings.CHART_MAX_SHIFT

    min = 3
    max = 300

    arr = []
    i = 0
    tend = None
    last_val = Decimal(str(start_val))

    for e in xrange(0, elements):
        if hard_tendency:
            tend = hard_tendency

        elif last_val <= min:
            tend = 1

        elif last_val >= max:
            tend = -1

        elif not hard_tendency and tendency and (i % 3 == 0):
            tend = tendency

        else:
            tend = random.choice([-1, 0, 1])

        v = __calc(max_shift, tend)

        last_val = (v * last_val) + last_val
        arr.append(last_val)

        i += 1

    return arr


if __name__ == '__main__':
    s = 100

    for x in xrange(1, 25):
        if x % 2 == 0 or x % 3 == 0:
            tendency = -1
        else:
            tendency = None

        s = calc(s, tendency=tendency, elements=60)[-1]
        print s
