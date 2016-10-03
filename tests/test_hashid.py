from django.test import TestCase
from django.utils.encoding import force_text

from hashids_field import Hashid


class HashidTests(TestCase):
    def test_integer(self):
        h = Hashid(5)
        self.assertIsInstance(h, Hashid)
        self.assertEqual(h.id, 5)
        self.assertEqual(h.hashid, h.hashids.encode(5))

    def test_hashid(self):
        h = Hashid(123)
        b = Hashid(h.hashid)
        self.assertEqual(h, b)
        self.assertEqual(h.id, b.id)
        self.assertEqual(h.hashid, b.hashid)

    def test_negative_integer(self):
        with self.assertRaises(Exception):
            h = Hashid(-5)

    def test_invalid_hashid(self):
        with self.assertRaises(Exception):
            h = Hashid('asdfqwer')

    def test_min_length(self):
        h = Hashid(456, min_length=10)
        self.assertEqual(len(h.hashid), 10)
        self.assertEqual(len(h), 10)

    def test_hashable(self):
        h = Hashid(987)
        d = {h: "some value"}
        self.assertEqual(d[h], "some value")

    def test_force_text(self):
        h = Hashid(2923)
        t = force_text(h)
        self.assertEqual(t, h.hashid)
