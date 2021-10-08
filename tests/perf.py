#!/usr/bin/env python
import os
import sys
from textwrap import dedent
from timeit import Timer

import django


def no_cache():
    setup = dedent('''
        from hashid_field.hashid import Hashid
    ''')
    stmt = dedent('''
        Hashid(123, salt="asdf", min_length=7)
    ''')
    timer = Timer(stmt, setup)
    time = timer.timeit(100_000)
    print("No pre-generated Hashids instance: {}".format(time))


def with_cache():
    setup = dedent('''
        from hashid_field.hashid import Hashid
        from hashids import Hashids
        hashids=Hashids(salt="asdf", min_length=7)
    ''')
    stmt = dedent('''
        Hashid(123, salt="asdf", min_length=7, hashids=hashids)
    ''')
    timer = Timer(stmt, setup)
    time = timer.timeit(100_000)
    print("With pre-generated Hashids instance: {}".format(time))


def hashid_decode():
    # Test the encode/decode performance of Hashid between different commits.
    setup = dedent('''
        from hashid_field.hashid import Hashid
        from hashids import Hashids
        hashids=Hashids(salt="asdf", min_length=7)
    ''')
    stmt = dedent('''
        a = Hashid(123, salt="asdf", min_length=7, hashids=hashids)
        b = Hashid(a.hashid, salt="asdf", min_length=7, hashids=hashids)
    ''')
    timer = Timer(stmt, setup)
    time = timer.timeit(100_000)
    print("Hashid decode: {}".format(time))


if __name__ == "__main__":
    print("Python:", sys.version)
    print("Django:", django.get_version(django.VERSION))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()

    # no_cache()
    # with_cache()
    hashid_decode()
