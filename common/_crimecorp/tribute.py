# -*- coding: utf-8 -*-
import random

from django.conf import settings

import crimecorp.common.logger as logging
import math
from crimecorp.job.models import JobTribute
from crimecorp.city.models import CityBuilding


def calc_tribute(profile):
    tribute_groups = {}
    for job in JobTribute.objects.all():
        if not tribute_groups.has_key(job.type): tribute_groups[job.type] = []
        tribute_groups[job.type].append(job.id)

    user_t = CityBuilding.objects.get_by_city_id(profile.default_city_id)
    logging.debug("%s tributes being recalculated" % (str(profile.user)))

    user_tribute_groups = {}
    for group_type, group_items in tribute_groups.iteritems():
        user_tribute_groups[group_type] = {}
        user_tribute_groups[group_type]['todo'] = []
        user_tribute_groups[group_type]['done'] = []
        for item in group_items:
            if str(item) in user_t.dones: user_tribute_groups[group_type]['done'].append(str(item))
            if str(item) in user_t.todos: user_tribute_groups[group_type]['todo'].append(str(item))

    for group_type, group_items in user_tribute_groups.iteritems():
        total = len(group_items['done']) + len(group_items['todo'])

        if total >= len(tribute_groups[group_type]): continue

        try:
            ratio = float(profile.city_population) / (total * settings.BIZ_PER_CAPITA[group_type])
        except ZeroDivisionError:
            ratio = float(profile.city_population) / (1 * settings.BIZ_PER_CAPITA[group_type])

        if ratio < 0.8:  # remove tributes
            to_out = int(total - math.floor(float(profile.city_population) / settings.BIZ_PER_CAPITA[group_type]))
            all_list = group_items['done'] + group_items['todo']
            if to_out <= 0:
                user_t.remove(all_list)
                continue

            out_list = []
            for i in xrange(0, to_out):
                choice = random.choice(all_list)
                if choice not in out_list: out_list.append(choice)
            # specjalnie nie ponawiamy randoma
            user_t.remove(out_list)

        elif ratio > 1.0:  # add tributes
            to_in = int(math.floor(float(profile.city_population) / settings.BIZ_PER_CAPITA[group_type]) - total)

            all_list = group_items['done'] + group_items['todo']
            if len(all_list) == len(tribute_groups[group_type]):
                continue
            elif len(all_list) >= len(tribute_groups[group_type]):
                logging.error('%s got more tributes than could' % profile)

            if to_in >= len(tribute_groups[group_type]):
                user_t.add([str(x) for x in tribute_groups[group_type]])
                continue

            in_list = []
            for i in xrange(0, to_in):
                choice = str(random.choice(tribute_groups[group_type]))
                if choice not in in_list: in_list.append(choice)
                # specjalnie nie ponawiamy randoma
                if len(all_list) + len(in_list) >= len(tribute_groups[group_type]): break
            user_t.add(in_list)

            return len(in_list)
        else:
            continue
