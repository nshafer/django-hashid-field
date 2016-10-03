from django.test import TestCase

from hashids_field.field import Hashid
from hashids_field.descriptor import HashidDescriptor


class TestClass(object):
    hashid = HashidDescriptor('hashid')


class DescriptorTests(TestCase):
    def test_no_value(self):
        t = TestClass()
        self.assertIsNone(t.hashid)

    def test_set_none(self):
        t = TestClass()
        t.hashid = None
        self.assertIsNone(t.hashid)

    def test_set_int(self):
        t = TestClass()
        t.hashid = 123
        self.assertIsInstance(t.hashid, Hashid)
        self.assertEqual(t.hashid.id, 123)

    def test_set_hashid(self):
        t = TestClass()
        h = Hashid(234)
        t.hashid = h
        self.assertIsInstance(t.hashid, Hashid)
        self.assertEqual(t.hashid.id, 234)

    def test_set_invalid_int(self):
        t = TestClass()
        t.hashid = -345
        self.assertNotIsInstance(t.hashid, Hashid)
        self.assertEqual(t.hashid, -345)

    def test_set_invalid_hashid(self):
        t = TestClass()
        t.hashid = "asdfqwer"
        self.assertNotIsInstance(t.hashid, Hashid)
        self.assertEqual(t.hashid, "asdfqwer")

    def test_set_valid_hashid_string(self):
        t = TestClass()
        h = Hashid(456)
        t.hashid = h.hashid
        self.assertIsInstance(t.hashid, Hashid)
        self.assertEqual(t.hashid.id, 456)

    def test_custom_salt(self):
        class SaltTest(object):
            hashid = HashidDescriptor('_hashid', salt='a test salt')
        t = TestClass()
        t.hashid = 5
        s = SaltTest()
        s.hashid = 5
        self.assertEqual(t.hashid.id, s.hashid.id)
        self.assertNotEqual(t, s)
        self.assertNotEqual(t.hashid, s.hashid)

    def test_min_length(self):
        class LengthTest(object):
            hashid = HashidDescriptor('_hashid', min_length=10)
        l = LengthTest()
        l.hashid = 1
        self.assertGreaterEqual(len(l.hashid.hashid), 10)

    def test_alphabet(self):
        class AlphaTest(object):
            hashid = HashidDescriptor('_hashid', alphabet="0123456789abcdef")
        a = AlphaTest()
        a.hashid = 2489734928374923874
        for char in "ghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.assertNotIn(char, a.hashid.hashid)
