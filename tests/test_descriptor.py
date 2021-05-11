from django.test import TestCase
from hashids import Hashids

from hashid_field import Hashid
from hashid_field.descriptor import HashidDescriptor

salt = "abcd"
min_length = 1
alphabet = "0123456789abcdef"
hashids = Hashids(salt=salt, min_length=min_length, alphabet=alphabet)


class TestClass(object):
    a = HashidDescriptor(field_name='a', salt=salt, min_length=min_length, alphabet=alphabet, hashids=hashids)
    b = HashidDescriptor(field_name='b', salt=salt, min_length=min_length, alphabet=alphabet, hashids=hashids,
                         enable_hashid_object=False)


class DescriptorTests(TestCase):
    def test_no_value(self):
        t = TestClass()
        self.assertIsNone(t.a)

    def test_set_none(self):
        t = TestClass()
        t.a = None
        self.assertIsNone(t.a)

    def test_set_int(self):
        t = TestClass()
        t.a = 123
        self.assertIsInstance(t.a, Hashid)
        self.assertEqual(t.a.id, 123)
        t.b = 123
        self.assertIsInstance(t.b, str)
        self.assertEqual(t.b, hashids.encode(123))

    def test_set_hashid(self):
        t = TestClass()
        h = Hashid(234)
        t.a = h
        self.assertIsInstance(t.a, Hashid)
        self.assertEqual(t.a.id, 234)
        t.b = h
        self.assertIsInstance(t.b, str)
        self.assertEqual(t.b, h.hashid)

    def test_set_invalid_int(self):
        t = TestClass()
        t.a = -345
        self.assertNotIsInstance(t.a, Hashid)
        self.assertEqual(t.a, -345)
        t.b = -345
        self.assertIsInstance(t.b, int)
        self.assertEqual(t.b, -345)

    def test_set_invalid_hashid(self):
        t = TestClass()
        t.a = "asdfqwer"
        self.assertNotIsInstance(t.a, Hashid)
        self.assertEqual(t.a, "asdfqwer")
        t.b = "asdfqwer"
        self.assertIsInstance(t.a, str)
        self.assertEqual(t.b, "asdfqwer")

    def test_set_valid_hashid_string(self):
        t = TestClass()
        h = Hashid(456, salt=salt, min_length=min_length, alphabet=alphabet)
        t.a = h.hashid
        self.assertIsInstance(t.a, Hashid)
        self.assertEqual(t.a.id, 456)
        t.b = h.hashid
        self.assertIsInstance(t.b, str)
        self.assertEqual(t.b, h.hashid)

    def test_reset_after_invalid_set(self):
        t = TestClass()
        t.a = "asdf"  # First set it to something invalid, so the descriptor will just set it to this string
        self.assertIsInstance(t.a, str)
        self.assertEqual(t.a, "asdf")
        t.a = 123  # Now set it to a valid value for a Hashid, so it should create a new Hashid()
        self.assertIsInstance(t.a, Hashid)
        self.assertEqual(t.a.id, 123)
        t.b = "asdf"  # First set it to something invalid, so the descriptor will just set it to this string
        self.assertIsInstance(t.b, str)
        self.assertEqual(t.b, "asdf")
        t.b = 123  # Now set it to a valid value for a Hashid, so it should create a new Hashid()
        self.assertIsInstance(t.b, str)
        self.assertEqual(t.b, hashids.encode(123))
