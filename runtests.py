#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import os
import sys
import warnings

import django
from django.conf import settings
from django.test.utils import get_runner

# Make deprecation warnings errors to ensure no usage of deprecated features.
warnings.simplefilter("error", DeprecationWarning)
# Make runtime warning errors to ensure no usage of error prone patterns.
warnings.simplefilter("error", RuntimeWarning)
# Ignore known warnings in test dependencies.
warnings.filterwarnings("ignore", "'U' mode is deprecated", DeprecationWarning, module='docutils.io')
warnings.filterwarnings("ignore", "Using or importing the ABCs from 'collections' instead of from 'collections.abc' is "
                        "deprecated, and in 3.8 it will stop working", module='rest_framework')
warnings.filterwarnings("ignore", "Using or importing the ABCs from 'collections' instead of from 'collections.abc' is "
                        "deprecated, and in 3.8 it will stop working", module='django')

if __name__ == "__main__":
    print("Python:", sys.version)
    print("Django:", django.get_version(django.VERSION))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(sys.argv[1:] or ["tests"])
    sys.exit(bool(failures))
