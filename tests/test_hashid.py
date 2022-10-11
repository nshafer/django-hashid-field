import pickle

import hashids
from django.test import TestCase
from django.utils.encoding import force_str

from hashid_field import Hashid


class HashidTests(TestCase):
    def test_integer(self):
        h = Hashid(5)
        self.assertIsInstance(h, Hashid)
        self.assertEqual(h.id, 5)
        self.assertEqual(h.hashid, h.hashids.encode(5))

    def test_integer_with_prefix(self):
        h = Hashid(10, prefix="num_")
        self.assertIsInstance(h, Hashid)
        self.assertEqual(h.id, 10)
        self.assertEqual(h.hashid, h.hashids.encode(10))
        self.assertEqual(str(h), "num_" + h.hashids.encode(10))

    def test_hashid(self):
        h = Hashid(123)
        b = Hashid(h.hashid)
        self.assertEqual(h, b)
        self.assertEqual(h.id, b.id)
        self.assertEqual(h.hashid, b.hashid)

    def test_hashid_with_prefix(self):
        h = Hashid(123, prefix="hid_")
        b = Hashid(str(h), prefix="hid_")
        self.assertEqual(h, b)
        self.assertEqual(h.id, b.id)
        self.assertEqual(h.hashid, b.hashid)
        self.assertEqual(h.prefix, b.prefix)

    def test_hashid_with_only_numbers(self):
        # Make sure that the hashids representation of an integer that happens to be a string of all numbers
        # is still properly interpreted as a hashid, not an integer
        a = Hashid(5, salt="salt", alphabet="0123456789abcdef")
        b = Hashid(a.hashid, salt="salt", alphabet="0123456789abcdef")
        self.assertEqual(a.id, b.id)

    def test_negative_integer(self):
        with self.assertRaises(Exception):
            h = Hashid(-5)

    def test_none_value(self):
        with self.assertRaises(Exception):
            h = Hashid(None)

    def test_hashid_encoded_zero_integer(self):
        h = Hashid(0)
        z = Hashid(h.hashid)
        self.assertEqual(h, z)

    def test_hashid_encoded_zero_integer_with_prefix(self):
        h = Hashid(0, prefix="zero_")
        z = Hashid(str(h), prefix="zero_")
        self.assertEqual(h, z)

    def test_invalid_hashid(self):
        with self.assertRaises(Exception):
            h = Hashid('asdfqwer')

    def test_invalid_prefix(self):
        h = Hashid(678, prefix="inv_")
        with self.assertRaises(ValueError):
            Hashid("wrong_" + h.hashid, prefix="inv_")

    def test_min_length(self):
        h = Hashid(456, min_length=10)
        self.assertEqual(len(h.hashid), 10)
        self.assertEqual(len(h), 10)

    def test_hashable(self):
        h = Hashid(987)
        d = {h: "some value"}
        self.assertEqual(d[h], "some value")
        self.assertTrue(h in d)
        self.assertTrue(str(h) in d)
        self.assertTrue(hash(h) == hash(str(h)))
        self.assertFalse(hash(int(h) == hash(h)))

    def test_force_text(self):
        h = Hashid(2923)
        t = force_str(h)
        self.assertEqual(t, h.hashid)

    def test_force_text_with_prefix(self):
        h = Hashid(2923, prefix="prefix_")
        t = force_str(h)
        self.assertEqual(t, "prefix_" + h.hashid)

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

    def test_typecast_to_str_with_prefix(self):
        a = Hashid(2, prefix="a_")
        self.assertEqual(str(a), "a_" + a.hashid)

    def test_str_compare(self):
        a = Hashid(1)
        self.assertTrue(str(a) == a)

    def test_str_compare_with_prefix(self):
        a = Hashid(2, prefix="b_")
        self.assertTrue(str(a) == a)

    def test_int_compare(self):
        a = Hashid(1)
        self.assertTrue(int(a) == a)

    def test_int_compare_with_prefix(self):
        a = Hashid(100, prefix='int_compare_')
        self.assertTrue(int(a) == a)

    def test_hashid_equality(self):
        a = Hashid(123)
        b = Hashid(123)
        c = Hashid(123, salt="asdfqwer")
        d = Hashid(123, prefix="eq_")
        self.assertTrue(a == b)
        self.assertTrue(hash(a) == hash(b))
        self.assertTrue(hash(a) == hash(str(b)))
        self.assertFalse(a == c)
        self.assertFalse(hash(a) == hash(c))
        self.assertFalse(a == d)
        self.assertFalse(hash(a) == hash(d))

    def test_hashid_override_with_minimum_alphabet(self):
        alphabet = "0123456789abcdef"
        h = hashids.Hashids(alphabet=alphabet)
        a = Hashid(5, alphabet=alphabet, hashids=h)
        self.assertIsInstance(a, Hashid)
        self.assertEqual(a.id, 5)
        self.assertEqual(a.hashid, h.encode(5))
        self.assertEqual(a._alphabet, alphabet)

    def test_pickle(self):
        a = Hashid(123)
        pickled = pickle.loads(pickle.dumps(a))
        self.assertTrue(a == pickled)

    def test_pickle_with_minimum_alphabet(self):
        alphabet = "0123456789abcdef"
        h = hashids.Hashids(alphabet=alphabet)
        a = Hashid(123, alphabet=alphabet, hashids=h)
        pickled = pickle.loads(pickle.dumps(a))
        self.assertTrue(a == pickled)

    def test_pickle_with_prefix(self):
        a = Hashid(125, prefix="pickle_")
        pickled = pickle.loads(pickle.dumps(a))
        self.assertTrue(a == pickled)

    def test_unpickle_old_reduce_value(self):
        # This test is to make sure that we can still unpickle values that were pickled with the old reduce
        # value.  This is to ensure backwards compatibility.
        pickled_a = b'\x80\x04\x95r\x00\x00\x00\x00\x00\x00\x00\x8c\x13hashid_field.hashid\x94\x8c\x06Hashid\x94\x93\x94(K{\x8c\x00\x94K\x00\x8c>abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890\x94h\x03Nt\x94R\x94.'
        a1 = Hashid(123)
        a2 = pickle.loads(pickled_a)
        self.assertTrue(a1 == a2)
