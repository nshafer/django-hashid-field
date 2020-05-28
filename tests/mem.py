#!/usr/bin/env python
import os
import sys

import django
from memory_profiler import profile


@profile(precision=8)
def no_cache():
    from hashid_field.hashid import Hashid
    instances = [Hashid(i, salt="asdf", min_length=7) for i in range(1, 10_000)]
    return instances


@profile(precision=8)
def with_cache():
    from hashid_field.hashid import Hashid
    from hashids import Hashids
    hashids = Hashids(salt="asdf", min_length=7)
    instances = [Hashid(i, hashids=hashids) for i in range(1, 10_000)]
    return instances


if __name__ == "__main__":
    print("Python:", sys.version)
    print("Django:", django.get_version(django.VERSION))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()

    no_cache()
    with_cache()
