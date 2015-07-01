#!/usr/bin/python
import os

import sys

sys.path.append(os.path.dirname(__file__) + "../../")
os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'

import unittest
from engine.engine import Engine
from common.models import DummyRequest

TEST_UID = 1


class TestCityUnits(unittest.TestCase):
    def setUp(self):
        self.engine = Engine(DummyRequest(TEST_UID))
        self.engine.start()

    def testMoveUnits(self):
        post = {'city_id': 1, 'unit_1': 1, 'unit_2': '1', }
        self.assertTrue(self.engine.city.id)

        # Validate start_city_id
        post = {'city_id': '3dupa', 'unit_1': 1, 'unit_2': '1', }
        self.assertFalse(self.engine.city.move_units(post))

        # Validate units (POST)
        post = {'city_id': 1, 'unit_1': '3dupa', 'unit_2': '1', }
        self.assertFalse(self.engine.city.move_units(post))

        post = {'city_id': 1, 'unit_1': 0, 'unit_2': -10, }
        self.assertFalse(self.engine.city.move_units(post))

        post = {'city_id': 1, 'unit_1': 3, 'unit_2': 6, }
        self.assertFalse(self.engine.city.move_units(post))

        post = {'city_id': 1, 'unit_1': 1, 'unit_2': '1', 'unit_66': 2, }
        self.assertFalse(self.engine.city.move_units(post))

        post = {'city_id': 1, 'unit_1': 1, 'unit_2': '1', }
        self.assertTrue(self.engine.city.move_units(post))

    def testMoveRoute(self):
        from common.helpers import calc_route

        self.assertEqual(calc_route(2, 1, 2, 100), 19)
        self.assertEqual(calc_route(200, 55, 55, 1), 1460)
        self.assertEqual(calc_route(1, 1, 55, 100), 559)


if __name__ == '__main__':
    unittest.main()
