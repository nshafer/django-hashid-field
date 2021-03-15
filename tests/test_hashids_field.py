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
        self.record = Record.objects.create(name="Test Record", reference_id=123, prefixed_id=234,
                                            string_id=345, plain_hashid=456, plain_id=567, key=234)
        self.record.refresh_from_db()
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

    def test_record_fields_are_correct_type_and_value(self):
        self.assertIsInstance(self.record.reference_id, Hashid)
        self.assertEqual(str(self.record.reference_id), self.hashids.encode(123))
        self.assertIsInstance(self.record.prefixed_id, Hashid)
        self.assertEqual(str(self.record.prefixed_id), "prefix_" + self.hashids.encode(234))
        self.assertIsInstance(self.record.string_id, str)
        self.assertEqual(self.record.string_id, self.hashids.encode(345))
        self.assertIsInstance(self.record.plain_hashid, Hashid)
        self.assertEqual(str(self.record.plain_hashid), self.hashids.encode(456))
        self.assertIsInstance(self.record.plain_id, str)
        self.assertEqual(str(self.record.plain_id), self.hashids.encode(567))

    def test_record_load_from_db(self):
        record = Record.objects.get(pk=self.record.pk)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.id, self.record.id)
        record = Record.objects.get(reference_id=self.record.reference_id)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.id, self.record.id)
        record = Record.objects.get(prefixed_id=self.record.prefixed_id)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.id, self.record.id)
        record = Record.objects.get(string_id=self.record.string_id)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.id, self.record.id)
        record = Record.objects.get(plain_hashid=self.record.plain_hashid)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.id, self.record.id)
        record = Record.objects.get(plain_id=self.record.plain_id)
        self.assertIsInstance(record, Record)
        self.assertEqual(record.id, self.record.id)

    def test_set_int(self):
        self.record.reference_id = 51
        self.record.prefixed_id = 52
        self.record.string_id = 53
        self.record.plain_hashid = 54
        self.record.plain_id = 55
        self.record.save()
        # No descriptor, so they should be set to exactly what I set them to
        self.assertIsInstance(self.record.plain_hashid, int)
        self.assertIsInstance(self.record.plain_id, int)
        self.assertEqual(self.record.plain_hashid, 54)
        self.assertEqual(self.record.plain_id, 55)
        # Refreshing from database will transform them based on settings due to from_db_value()
        self.record.refresh_from_db()
        self.assertIsInstance(self.record.reference_id, Hashid)
        self.assertEqual(str(self.record.reference_id), self.hashids.encode(51))
        self.assertIsInstance(self.record.prefixed_id, Hashid)
        self.assertEqual(str(self.record.prefixed_id), "prefix_" + self.hashids.encode(52))
        self.assertIsInstance(self.record.string_id, str)
        self.assertEqual(self.record.string_id, self.hashids.encode(53))
        self.assertIsInstance(self.record.plain_hashid, Hashid)
        self.assertEqual(str(self.record.plain_hashid), self.hashids.encode(54))
        self.assertIsInstance(self.record.plain_id, str)
        self.assertEqual(self.record.plain_id, self.hashids.encode(55))

    def test_set_hashid(self):
        self.record.reference_id = self.hashids.encode(61)
        self.record.prefixed_id = "prefix_" + self.hashids.encode(62)
        self.record.string_id = self.hashids.encode(63)
        self.record.plain_hashid = self.hashids.encode(64)
        self.record.plain_id = self.hashids.encode(65)
        self.record.save()
        # No descriptor, so they should be set to exactly what I set them to
        self.assertIsInstance(self.record.plain_hashid, str)
        self.assertIsInstance(self.record.plain_id, str)
        self.assertEqual(self.record.plain_hashid, self.hashids.encode(64))
        self.assertEqual(self.record.plain_id, self.hashids.encode(65))
        # Refreshing from database will transform them based on settings due to from_db_value()
        self.record.refresh_from_db()
        self.assertIsInstance(self.record.reference_id, Hashid)
        self.assertEqual(str(self.record.reference_id), self.hashids.encode(61))
        self.assertIsInstance(self.record.prefixed_id, Hashid)
        self.assertEqual(str(self.record.prefixed_id), "prefix_" + self.hashids.encode(62))
        self.assertIsInstance(self.record.string_id, str)
        self.assertEqual(self.record.string_id, self.hashids.encode(63))
        self.assertIsInstance(self.record.plain_hashid, Hashid)
        self.assertEqual(str(self.record.plain_hashid), self.hashids.encode(64))
        self.assertIsInstance(self.record.plain_id, str)
        self.assertEqual(self.record.plain_id, self.hashids.encode(65))

    def assert_lookups_match(self, field_name, value, expected, allow_int_lookup=False):
        original_allow_int_lookup_setting = Record._meta.get_field(field_name).allow_int_lookup
        if allow_int_lookup:
            Record._meta.get_field(field_name).allow_int_lookup = True
        self.assertEqual(Record.objects.filter(**{field_name: value}).exists(), expected)
        self.assertEqual(Record.objects.filter(**{field_name + "__exact": value}).exists(), expected)
        self.assertEqual(Record.objects.filter(**{field_name + "__iexact": value}).exists(), expected)
        self.assertEqual(Record.objects.filter(**{field_name + "__contains": value}).exists(), expected)
        self.assertEqual(Record.objects.filter(**{field_name + "__icontains": value}).exists(), expected)
        self.assertEqual(Record.objects.filter(**{field_name + "__in": [value]}).exists(), expected)
        if original_allow_int_lookup_setting is not True:
            Record._meta.get_field(field_name).allow_int_lookup = False

    def test_filter_by_int(self):
        # These should not return anything when integer lookups are not allowed
        self.assert_lookups_match("reference_id", 123, False, allow_int_lookup=False)
        self.assert_lookups_match("prefixed_id", 234, False, allow_int_lookup=False)
        self.assert_lookups_match("string_id", 345, False, allow_int_lookup=False)
        self.assert_lookups_match("plain_hashid", 456, False, allow_int_lookup=False)
        self.assert_lookups_match("plain_id", 567, False, allow_int_lookup=False)

        # Tests when integer lookups are allowed
        self.assert_lookups_match("reference_id", 123, True, allow_int_lookup=True)
        self.assert_lookups_match("prefixed_id", 234, True, allow_int_lookup=True)
        self.assert_lookups_match("string_id", 345, True, allow_int_lookup=True)
        self.assert_lookups_match("plain_hashid", 456, True, allow_int_lookup=True)
        self.assert_lookups_match("plain_id", 567, True, allow_int_lookup=True)

    def test_filter_by_string(self):
        self.assert_lookups_match("reference_id", str(self.record.reference_id), True)
        self.assert_lookups_match("prefixed_id", str(self.record.prefixed_id), True)
        self.assert_lookups_match("string_id", str(self.record.string_id), True)
        self.assert_lookups_match("plain_hashid", str(self.record.plain_hashid), True)
        self.assert_lookups_match("plain_id", str(self.record.plain_id), True)

    def test_filter_by_hashid(self):
        self.assert_lookups_match("reference_id", self.hashids.encode(123), True)
        self.assert_lookups_match("prefixed_id", "prefix_" + self.hashids.encode(234), True)
        self.assert_lookups_match("string_id", self.hashids.encode(345), True)
        self.assert_lookups_match("plain_hashid", self.hashids.encode(456), True)
        self.assert_lookups_match("plain_id", self.hashids.encode(567), True)

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
        self.assertEqual(Record.objects.filter(reference_id__gte=str(r1.reference_id)).count(), 3)
        self.assertEqual(Record.objects.filter(prefixed_id__gte=str(r1.prefixed_id)).count(), 1)
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
        form = RecordForm({'name': "A new name", 'reference_id': 987, 'prefixed_id': 987}, instance=self.record)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(self.record, instance)
        self.assertEqual(str(self.record.reference_id), self.hashids.encode(987))
        self.assertEqual(str(self.record.prefixed_id), "prefix_" + self.hashids.encode(987))

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
        # print("dumpdata out", out.getvalue())
        self.assertJSONEqual(out.getvalue(), """
            [
                {
                    "model": "tests.record",    
                    "pk": "Yd3axGx",
                    "fields": {
                        "name": "Test Record",
                        "artist": null,
                        "reference_id": "M3Ka6wW",
                        "prefixed_id": "prefix_2PEK0G5",
                        "string_id": "d3aqj3x",
                        "plain_hashid": "9wXZ03N",
                        "plain_id": "M3K9XwW",
                        "alternate_id": null,
                        "key": "8wx9yyv39o"
                    }
                },
                {
                    "model": "tests.record",
                    "pk": "gVGO031",
                    "fields": {
                        "name": "Blue Album",
                        "artist": "bMrZ5lYd3axGxpW72Vo0",
                        "reference_id": "9wXZ03N",
                        "prefixed_id": null,
                        "string_id": null,
                        "plain_hashid": null,
                        "plain_id": null,
                        "alternate_id": null,
                        "key": null
                    }
                }
            ]
        """)

    def test_loaddata(self):
        out = StringIO()
        call_command("loaddata", "artists", stdout=out)
        self.assertEqual(out.getvalue().strip(), "Installed 2 object(s) from 1 fixture(s)")
        self.assertEqual(Artist.objects.get(pk='bMrZ5lYd3axGxpW72Vo0').name, "John Doe")
        self.assertEqual(Artist.objects.get(pk="Ka0MzjgVGO031r5ybWkJ").name, "Jane Doe")

    @override_settings(HASHID_FIELD_LOOKUP_EXCEPTION=True)
    def test_exceptions(self):
        a = Artist.objects.create(name="John Doe")
        r = Record.objects.create(name="Blue Album", reference_id=123, artist=a, key=456)
        self.assertTrue(Record.objects.filter(key=str(r.key)).exists())
        self.assertTrue(Record.objects.filter(key__in=[str(r.key)]).exists())
        with self.assertRaises(ValueError):
            self.assertFalse(Record.objects.filter(key=404).exists())
        with self.assertRaises(ValueError):
            self.assertFalse(Record.objects.filter(key="invalid").exists())
        with self.assertRaises(ValueError):
            self.assertFalse(Record.objects.filter(key__in=[404]).exists())
        self.assertTrue(Record.objects.filter(artist=a).exists())
        self.assertTrue(Record.objects.filter(artist_id=a.id).exists())
        self.assertTrue(Record.objects.filter(artist__in=[a]).exists())
        self.assertTrue(Record.objects.filter(artist_id__in=[a.id]).exists())
        self.assertFalse(Record.objects.filter(artist_id=404).exists())
        with self.assertRaises(ValueError):
            self.assertFalse(Record.objects.filter(artist_id="invalid").exists())
        self.assertFalse(Record.objects.filter(artist_id__in=[404]).exists())

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
        field_without_prefix = HashidField(min_length=5)
        field_with_prefix = HashidField(min_length=5, prefix=1)

        hashed_id_without_prefix = field_without_prefix.encode_id(1)
        hashed_id_with_prefix = field_with_prefix.encode_id(1)

        self.assertNotEqual(str(hashed_id_with_prefix), str(hashed_id_without_prefix))
        self.assertNotEqual(hashed_id_without_prefix, hashed_id_with_prefix)

    def test_decode_with_prefix(self):
        instance = Track.objects.create()
        self.assertEqual(1, Track.objects.filter(id=1).count())

    # def test_dynamic_prefix(self):
    #     instance = RecordLabel.objects.create()
    #     self.assertEqual(instance.id, "record_label/" + instance.id.hashids.encode(instance.id.id))
