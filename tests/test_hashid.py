from django.test import TestCase
from django.utils.encoding import force_text

from hashid_field import Hashid


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

    def test_sorting(self):
        a = Hashid(1)
        b = Hashid(2)
        c = Hashid(3)
        arr = [b, a, c]
        self.assertEqual(sorted(arr), [a, b, c])

    def test_typecast_to_int(self):
        a = Hashid(1)
        self.assertEqual(int(a), 1)

    def test_typecast_to_str(self):
        a = Hashid(1)
        self.assertEqual(str(a), a.hashid)

    def test_str_compare(self):
        a = Hashid(1)
        self.assertTrue(str(a) == a)

    def test_int_compare(self):
        a = Hashid(1)
        self.assertTrue(int(a) == a)

    def test_hashid_equality(self):
        a = Hashid(123)
        b = Hashid(123)
        self.assertTrue(a == b)
        self.assertTrue(hash(a) == hash(b))
