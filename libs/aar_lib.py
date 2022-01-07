import logging
import re
from copy import copy

from flask import g
from pymongo import MongoClient

import libs.lib
import mongo_client


def amend_aar(route: str, aar: dict) -> dict:
    """

    :param route:
    :param aar: adr dictionary as it is returned from the database
    :return:
    """
    aar_route = aar['route']
    remaining_route = copy(route)
    triggered_tfix = None
    # expanded_aar = aar['route_fixes']
    tfixes = aar['transition_fixes']
    tfix_info_dict = {e['tfix']: e['info'] for e in aar['transition_fixes_details']}
    for tfix in tfixes:
        # find first tfix which triggered the AAR
        tfix_info = tfix_info_dict[tfix]
        if tfix in route and not route[route.index(tfix)+len(tfix)].isdigit():
            if 'Prepend' in tfix_info:
                triggered_tfix = tfix
                remaining_route = remaining_route[:route.index(tfix)+len(tfix)]
                break
            elif 'Explicit' in tfix_info:
                triggered_tfix = tfix
                dot_counter = int(tfix_info.split('-')[-1])
                aar_route = '.' + re.split(r'\.', aar_route, dot_counter)[-1]
                remaining_route = remaining_route[:route.index(tfix)+len(tfix)]
                break
        if 'Implicit' in tfix_info:
            dot_counter, implicit_trigger = tfix_info.split('-')[1:]
            if implicit_trigger in route:
                aar_route = re.split(r'\.', aar_route, int(dot_counter))[-1]
                index = route.index(implicit_trigger)
                if index:
                    triggered_tfix = tfix
                    remaining_route = remaining_route[:index+len(tfix)]
                    aar_route = aar_route
                    break
    # add dots after tfix in the filed route
    if match := re.search(r'\.+', route[len(remaining_route):]):
        remaining_route += match.group()
    return {
        'aar_amendment': aar_route,
        'tfix': triggered_tfix,
        'route': remaining_route,
        'order': aar['order'],
        'route_groups': aar['route_groups']
    }


def get_eligible_aar(edst_entry, requesting_artcc) -> list:
    aircraft = edst_entry['flightplan']['aircraft_short']
    client: MongoClient = g.mongo_reader_client if g else mongo_client.reader_client
    nat_list = libs.lib.get_nat_types(aircraft) + ['NATALL']
    aar_list = client.flightdata.aar.find(
        {"airports": edst_entry['dest'],
         "applicable_artcc": requesting_artcc.upper(),
         "aircraft_class": {"$elemMatch": {"$in": nat_list}}
         }, {'_id': False})
    eligible_aar = []
    alt = int(edst_entry['altitude'])*100
    route = edst_entry['route']
    expanded_route = libs.lib.expand_route(route)
    for aar in aar_list:
        if (int(aar['min_alt']) <= alt <= int(aar['top_alt'])) or alt == 0:
            for tfix_details in aar['transition_fixes_details']:
                tfix = tfix_details['tfix']
                tfix_info = tfix_details['info']
                if (('Explicit' in tfix_info and
                     tfix in route and
                     not route[route.index(tfix)+len(tfix)].isdigit()) or
                        ('Implicit' in tfix_info and
                         tfix in expanded_route) or
                        (tfix in expanded_route and
                         tfix_info == 'Prepend')):
                    eligible_aar.append(aar)
                    break
    return eligible_aar