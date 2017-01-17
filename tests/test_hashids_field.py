from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from hashid_field import Hashid
from tests.forms import RecordForm, AlternateRecordForm
from tests.models import Record, Artist


class HashidsTests(TestCase):
    def setUp(self):
        self.record = Record.objects.create(name="Test Record", reference_id=123, key=456)
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

    def test_custom_salt(self):
        r = Record.objects.create(reference_id=845, alternate_id=845)
        self.assertEqual(r.reference_id.id, r.alternate_id.id)
        self.assertNotEqual(r.reference_id, r.alternate_id)
        self.assertNotEqual(r.reference_id.hashid, r.alternate_id.hashid)

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

    def test_invalid_int_in_form(self):
        form = RecordForm({'name': "A new name", 'reference_id': -5})
        self.assertFalse(form.is_valid())
        self.assertIn('reference_id', form.errors)

    def test_blank_for_nullable_field(self):
        name = "Blue Album"
        reference_id = 42
        form = AlternateRecordForm({'name': name, 'reference_id': reference_id})
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.name, name)
        self.assertEqual(instance.reference_id.id, reference_id)
        self.assertEqual(instance.alternate_id, '')
        instance.refresh_from_db()
        self.assertIsNone(instance.alternate_id)

    def test_autofield(self):
        a = Artist.objects.create(name="John Doe")
        b = Artist.objects.create(name="Jane Doe")
        self.assertIsInstance(a.id, Hashid)
        self.assertIsInstance(b.id, Hashid)
        self.assertListEqual(list(Artist.objects.order_by('id')), [a, b])

    def test_foreign_key(self):
        a = Artist.objects.create(name="John Doe")
        r = Record.objects.create(name="Blue Album", reference_id=456, artist=a)
        self.assertIsInstance(r, Record)
        self.assertIsInstance(r.artist, Artist)
        self.assertEqual(r.artist, a)

    def test_dumpdata(self):
        a = Artist.objects.create(name="John Doe")
        r = Record.objects.create(name="Blue Album", reference_id=456, artist=a)
        out = StringIO()
        call_command("dumpdata", "tests.Artist", stdout=out)
        self.assertJSONEqual(out.getvalue(), '[{"pk": "bMrZ5lYd3axGxpW72Vo0", "fields": {"name": "John Doe"}, "model": "tests.artist"}]')
        out = StringIO()
        call_command("dumpdata", "tests.Record", stdout=out)
        self.assertJSONEqual(out.getvalue(), '[{"model": "tests.record", "pk": 1, "fields": {"name": "Test Record", "key": "82x1vxv21o", "alternate_id": null, "reference_id": "M3Ka6wW", "artist": null}}, {"model": "tests.record", "pk": 2, "fields": {"name": "Blue Album", "key": null, "alternate_id": null, "reference_id": "9wXZ03N", "artist": "bMrZ5lYd3axGxpW72Vo0"}}]')

    def test_loaddata(self):
        out = StringIO()
        call_command("loaddata", "artists", stdout=out)
        self.assertEqual(out.getvalue().strip(), "Installed 2 object(s) from 1 fixture(s)")
        self.assertEqual(Artist.objects.get(pk=1).name, "John Doe")
        self.assertEqual(Artist.objects.get(pk="Ka0MzjgVGO031r5ybWkJ").name, "Jane Doe")
