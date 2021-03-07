from django.core import exceptions
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.test import TestCase, override_settings
from io import StringIO

from hashid_field import Hashid, HashidField
from tests.forms import RecordForm, AlternateRecordForm
from tests.models import Record, Artist, Track, RecordLabel


class HashidsTests(TestCase):
    def setUp(self):
        self.record = Record.objects.create(name="Test Record", reference_id=123, key=456)
        self.hashids = self.record.reference_id.hashids

    def test_record_create(self):
        self.assertIsInstance(self.record, Record)

    def test_get_or_create(self):
        new_artist, created = Artist.objects.get_or_create(name="Get or Created Artist")
        self.assertIsInstance(new_artist, Artist)
        self.assertIsNotNone(new_artist.id)
        Record._meta.get_field('reference_id').allow_int_lookup = True
        new_record, created = Record.objects.get_or_create(name="Get or Created Record", reference_id=667373)
        self.assertIsInstance(new_record, Record)
        self.assertEqual(new_record.reference_id.id, 667373)
        Record._meta.get_field('reference_id').allow_int_lookup = False

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
        # These should not return anything when integer lookups are not allowed
        self.assertFalse(Record.objects.filter(reference_id=123).exists())
        self.assertFalse(Record.objects.filter(reference_id__exact=123).exists())
        self.assertFalse(Record.objects.filter(reference_id__iexact=123).exists())
        self.assertFalse(Record.objects.filter(reference_id__contains=123).exists())
        self.assertFalse(Record.objects.filter(reference_id__icontains=123).exists())
        self.assertFalse(Record.objects.filter(reference_id__in=[123]).exists())

        # Tests when integer lookups are allowed
        Record._meta.get_field('reference_id').allow_int_lookup = True
        self.assertTrue(Record.objects.filter(reference_id=123).exists())
        self.assertTrue(Record.objects.filter(reference_id__exact=123).exists())
        self.assertTrue(Record.objects.filter(reference_id__iexact=123).exists())
        self.assertTrue(Record.objects.filter(reference_id__contains=123).exists())
        self.assertTrue(Record.objects.filter(reference_id__icontains=123).exists())
        self.assertTrue(Record.objects.filter(reference_id__in=[123]).exists())
        Record._meta.get_field('reference_id').allow_int_lookup = False

    def test_filter_by_string(self):
        self.assertTrue(Record.objects.filter(reference_id=str(self.record.reference_id)).exists())
        self.assertTrue(Record.objects.filter(reference_id__exact=str(self.record.reference_id)).exists())
        self.assertTrue(Record.objects.filter(reference_id__iexact=str(self.record.reference_id)).exists())
        self.assertTrue(Record.objects.filter(reference_id__contains=str(self.record.reference_id)).exists())
        self.assertTrue(Record.objects.filter(reference_id__icontains=str(self.record.reference_id)).exists())
        self.assertTrue(Record.objects.filter(reference_id__in=[str(self.record.reference_id)]).exists())

    def test_filter_by_hashid(self):
        self.assertTrue(Record.objects.filter(reference_id=self.hashids.encode(123)).exists())
        self.assertTrue(Record.objects.filter(reference_id__exact=self.hashids.encode(123)).exists())
        self.assertTrue(Record.objects.filter(reference_id__iexact=self.hashids.encode(123)).exists())
        self.assertTrue(Record.objects.filter(reference_id__contains=self.hashids.encode(123)).exists())
        self.assertTrue(Record.objects.filter(reference_id__icontains=self.hashids.encode(123)).exists())
        self.assertTrue(Record.objects.filter(reference_id__in=[self.hashids.encode(123)]).exists())

    def test_iterable_lookup(self):
        r1 = Record.objects.create(name="Red Album", reference_id=456)
        r2 = Record.objects.create(name="Blue Album", reference_id=789)
        # All 3 records exists (including record created in setUp())
        self.assertEqual(Record.objects.count(), 3)
        # Integers
        Record._meta.get_field('reference_id').allow_int_lookup = True
        self.assertEqual(Record.objects.filter(reference_id__in=[456, 789]).count(), 2)
        # Strings
        self.assertEqual(Record.objects.filter(reference_id__in=[456, str(r2.reference_id)]).count(), 2)
        self.assertEqual(Record.objects.filter(reference_id__in=[str(r1.reference_id), str(r2.reference_id)]).count(), 2)
        # Hashids
        self.assertEqual(Record.objects.filter(reference_id__in=[456, r2.reference_id]).count(), 2)
        self.assertEqual(Record.objects.filter(reference_id__in=[r1.reference_id, r2.reference_id]).count(), 2)
        # nonexistent integers
        self.assertEqual(Record.objects.filter(reference_id__in=[456, 1]).count(), 1)
        # nonexistent, but valid strings
        self.assertEqual(Record.objects.filter(reference_id__in=[456, self.hashids.encode(1)]).count(), 1)
        # nonexistent, but valid hashids
        self.assertEqual(Record.objects.filter(reference_id__in=[456, Record._meta.get_field('reference_id').encode_id(1)]).count(), 1)
        # Invalid integer
        self.assertFalse(Record.objects.filter(reference_id__in=[-1]).exists())
        # Invalid string
        self.assertFalse(Record.objects.filter(reference_id__in=["asdf"]).exists())
        Record._meta.get_field('reference_id').allow_int_lookup = False

    def test_subquery_lookup(self):
        a = Artist.objects.create(name="Artist A")
        b = Artist.objects.create(name="Artist B")
        c = Artist.objects.create(name="Artist C")
        queryset = Artist.objects.all()[:2]
        self.assertEqual(len(queryset), 2)
        self.assertEqual(len(Artist.objects.filter(id__in=queryset.values('id'))), 2)

    def test_passthrough_lookups(self):
        # Test null lookups
        self.assertTrue(Record.objects.filter(alternate_id__isnull=True).exists())
        self.assertFalse(Record.objects.filter(alternate_id__isnull=False).exists())

        # Create some new objects to test with
        a = Artist.objects.create(name="Artist A")
        b = Artist.objects.create(name="Artist B")
        c = Artist.objects.create(name="Artist C")
        r1 = self.record
        r2 = Record.objects.create(name="Red Album", reference_id=456)
        r3 = Record.objects.create(name="Blue Album", reference_id=789)

        # All 3 records exists (including record created in setUp())
        self.assertEqual(Record.objects.count(), 3)
        # greater than with hashid and integer values
        self.assertEqual(Artist.objects.filter(id__gt=a.id).count(), 2)
        self.assertEqual(Record.objects.filter(reference_id__gt=r1.reference_id).count(), 2)
        # great than or equal
        self.assertEqual(Artist.objects.filter(id__gte=a.id).count(), 3)
        self.assertEqual(Record.objects.filter(reference_id__gte=r1.reference_id.hashid).count(), 3)
        # less than
        self.assertEqual(Artist.objects.filter(id__lt=b.id).count(), 1)
        self.assertEqual(Record.objects.filter(reference_id__lt=r3.reference_id).count(), 2)
        # less than or equal
        self.assertEqual(Artist.objects.filter(id__lte=b.id.hashid).count(), 2)
        self.assertEqual(Record.objects.filter(reference_id__lte=r3.reference_id).count(), 3)
        # Make sure integer lookups are not allowed
        self.assertEqual(Artist.objects.filter(id__gt=a.id.id).count(), 0)
        self.assertEqual(Record.objects.filter(reference_id__gte=r1.reference_id.id).count(), 0)
        self.assertEqual(Artist.objects.filter(id__lt=999_999_999).count(), 0)
        self.assertEqual(Record.objects.filter(reference_id__lte=r3.reference_id.id).count(), 0)
        # Unless we turn them on
        Artist._meta.get_field('id').allow_int_lookup = True
        Record._meta.get_field('reference_id').allow_int_lookup = True
        self.assertEqual(Artist.objects.filter(id__gt=a.id.id).count(), 2)
        self.assertEqual(Record.objects.filter(reference_id__gte=r1.reference_id.id).count(), 3)
        self.assertEqual(Artist.objects.filter(id__lt=999_999_999).count(), 3)
        self.assertEqual(Record.objects.filter(reference_id__lte=r3.reference_id.id).count(), 3)
        Artist._meta.get_field('id').allow_int_lookup = False
        Record._meta.get_field('reference_id').allow_int_lookup = False

    def test_get_object_or_404(self):
        a = Artist.objects.create(name="Artist A")

        from django.http import Http404

        # Regular lookups should succeed
        self.assertEqual(get_object_or_404(Artist, pk=a.id), a)
        self.assertEqual(get_object_or_404(Artist, pk=str(a.id)), a)

        # Lookups for non-existant IDs should fail
        with self.assertRaises(Http404):
            get_object_or_404(Artist, pk=-1)
        with self.assertRaises(Http404):
            get_object_or_404(Artist, pk="asdf")

        # int lookups should fail
        with self.assertRaises(Http404):
            self.assertEqual(get_object_or_404(Artist, pk=int(a.id)), a)

    def test_invalid_int(self):
        with self.assertRaises(ValueError):
            self.record.reference_id = -5
            self.record.save()

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
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

    def test_negative_int_in_form(self):
        form = RecordForm({'name': "A new name", 'reference_id': -5})
        self.assertFalse(form.is_valid())
        self.assertIn('reference_id', form.errors)

    def test_int_in_form(self):
        form = RecordForm({'name': "A new name", 'reference_id': 42})
        self.assertTrue(form.is_valid())

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
        self.assertTrue(Record.objects.filter(artist__id=a.id))

    def test_spanning_relationships(self):
        a = Artist.objects.create(name="John Doe")
        r = Record.objects.create(name="Blue Album", reference_id=456, artist=a)
        self.assertEqual(Record.objects.filter(artist__name="John Doe").first(), r)
        Record._meta.get_field('reference_id').allow_int_lookup = True
        self.assertEqual(Artist.objects.filter(records__reference_id=456).first(), a)
        Record._meta.get_field('reference_id').allow_int_lookup = False

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
        self.assertEqual(Artist.objects.get(pk='bMrZ5lYd3axGxpW72Vo0').name, "John Doe")
        self.assertEqual(Artist.objects.get(pk="Ka0MzjgVGO031r5ybWkJ").name, "Jane Doe")

    @override_settings(HASHID_FIELD_LOOKUP_EXCEPTION=True)
    def test_exceptions(self):
        self.assertTrue(Record.objects.filter(key=str(self.record.key)).exists())
        self.assertTrue(Record.objects.filter(key__in=[str(self.record.key)]).exists())
        with self.assertRaises(ValueError):
            self.assertTrue(Record.objects.filter(key=456).exists())
        with self.assertRaises(ValueError):
            self.assertTrue(Record.objects.filter(key="asdf").exists())
        with self.assertRaises(ValueError):
            self.assertTrue(Record.objects.filter(key__in=[456]).exists())

    def test_custom_hashids_settings(self):
        SALT="abcd"
        ALPHABET="abcdefghijklmnop"
        MIN_LENGTH=10
        field = HashidField(salt=SALT, alphabet=ALPHABET, min_length=MIN_LENGTH)
        hashids = field._hashids
        self.assertEqual(hashids._salt, SALT)
        self.assertEqual(hashids._min_length, MIN_LENGTH)
        self.assertEqual("".join(sorted(hashids._alphabet + hashids._guards + hashids._separators)), ALPHABET)
        # Make sure all characters in 100 hashids are in the ALPHABET and are at least MIN_LENGTH
        for i in range(1, 100):
            hashid = str(field.to_python(i))
            self.assertGreaterEqual(len(hashid), MIN_LENGTH)
            for c in hashid:
                self.assertIn(c, ALPHABET)

    def test_invalid_alphabets(self):
        with self.assertRaises(exceptions.ImproperlyConfigured):
            HashidField(alphabet="")  # blank
        with self.assertRaises(exceptions.ImproperlyConfigured):
            HashidField(alphabet="abcdef")  # too short
        with self.assertRaises(exceptions.ImproperlyConfigured):
            HashidField(alphabet="abcdefghijklmno")  # too short by one
        with self.assertRaises(exceptions.ImproperlyConfigured):
            HashidField(alphabet="aaaaaaaaaaaaaaaaaaaaa")  # not unique
        with self.assertRaises(exceptions.ImproperlyConfigured):
            HashidField(alphabet="aabcdefghijklmno")  # not unique by one

    def test_encode_with_prefix(self):
        SALT = "abcd"
        ALPHABET = "abcdefghijklmnop"

        field_without_prefix = HashidField(min_length=5)
        field_with_prefix = HashidField(min_length=5, prefix=1)

        hashed_id_without_prefix = field_without_prefix.encode_id(1)
        hashed_id_with_prefix = field_with_prefix.encode_id(1)

        self.assertNotEqual(hashed_id_without_prefix, hashed_id_with_prefix)


    def test_decode_with_prefix(self):
        instance = Track.objects.create()
        self.assertEqual(1, Track.objects.filter(id=1).count())


    def test_dynamic_prefix(self):
        instance = RecordLabel.objects.create()
        self.assertEqual(instance.id, 'record_label/Yd3axGx')