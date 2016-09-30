from django.test import TestCase

from hashids_field import Hashid
from tests.forms import RecordForm
from tests.models import Record, Artist


class HashidsTests(TestCase):
    def setUp(self):
        self.record = Record.objects.create(name="Test Book", reference_id=123, key=456)
        self.hashids = self.record.reference_id.hashids

    def test_book_create(self):
        self.assertIsInstance(self.record, Record)

    def test_record_reference_is_hashid(self):
        self.assertIsInstance(self.record.reference_id, Hashid)
        self.assertEqual(str(self.record.reference_id), self.hashids.encode(123))

    def test_record_load_from_db(self):
        record = Record.objects.get(pk=self.record.pk)
        self.assertIsInstance(record, Record)

    def test_record_reference_from_db_is_hashid(self):
        record = Record.objects.get(pk=self.record.pk)
        self.assertIsInstance(self.record.reference_id, Hashid)
        self.assertEqual(record.reference_id.hashid, self.hashids.encode(123))

    def test_set_int(self):
        self.record.reference_id = 456
        self.record.save()
        self.assertEqual(self.record.reference_id.hashid, self.hashids.encode(456))

    def test_set_hashid(self):
        self.record.reference_id = self.hashids.encode(789)
        self.record.save()
        self.assertEqual(str(self.record.reference_id), self.hashids.encode(789))

    def test_filter_by_int(self):
        self.assertTrue(Record.objects.filter(reference_id=123).exists())

    def test_filter_by_hashid(self):
        self.assertTrue(Record.objects.filter(reference_id=self.hashids.encode(123)).exists())

    def test_invalid_int(self):
        with self.assertRaises(TypeError):
            self.record.reference_id = -5
            self.record.save()

    def test_invalid_string(self):
        with self.assertRaises(TypeError):
            self.record.reference_id = "asdfqwer"
            self.record.save()

    def test_min_length(self):
        self.assertGreaterEqual(len(self.record.key), 10)

    def test_alphabet(self):
        for char in "efghijkpqrs4560":
            self.assertNotIn(char, self.record.key.hashid)

    def test_record_form(self):
        form = RecordForm(instance=self.record)
        self.assertEqual(form.initial['reference_id'].hashid, self.hashids.encode(123))
        form = RecordForm({'name': "A new name", 'reference_id': 987}, instance=self.record)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(self.record, instance)
        self.assertEqual(str(self.record.reference_id), self.hashids.encode(987))

    def test_invalid_id_in_form(self):
        form = RecordForm({'name': "A new name", 'reference_id': "asdfqwer"})
        self.assertFalse(form.is_valid())
        self.assertIn('reference_id', form.errors)

    def test_autofield(self):
        a = Artist.objects.create(name="John Doe")
        b = Artist.objects.create(name="Jane Doe")
        a.refresh_from_db()
        b.refresh_from_db()
        self.assertIsInstance(a.id, Hashid)
        self.assertIsInstance(b.id, Hashid)
        self.assertListEqual(list(Artist.objects.order_by('id')), [a, b])
