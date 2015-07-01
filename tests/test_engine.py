#!/usr/bin/python
import os

import sys

sys.path.append(os.path.dirname(__file__) + "../../")
os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'

import unittest

if __name__ == '__main__':
    suites = unittest.TestSuite([])
