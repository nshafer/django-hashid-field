#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    print("Python:", sys.version)
    print("Django:", django.get_version(django.VERSION))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(sys.argv[1:] or ["tests"])
    sys.exit(bool(failures))
