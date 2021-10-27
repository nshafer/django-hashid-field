from unittest import skipUnless

from django.core import exceptions
from django.test import TestCase
from rest_framework.exceptions import ErrorDetail

from tests.models import Artist, Record, Track
import hashids

try:
    from rest_framework import serializers
    from rest_framework.renderers import JSONRenderer
    from hashid_field.rest import UnconfiguredHashidSerialField, HashidSerializerCharField, HashidSerializerIntegerField

    have_drf = True
except ImportError:
    have_drf = False


@skipUnless(have_drf, "Requires Django REST Framework to be installed")
class TestRestFramework(TestCase):
    def assertSerializerError(self, serializer, field, code):
        serializer_name = serializer.__class__.__name__
        self.assertFalse(serializer.is_valid(),
                         msg="The serializer {} does not contain any errors".format(serializer_name))

        def assertCodeInErrors(errors):
            found_error = False
            for error_detail in errors:
                if error_detail.code == code:
                    found_error = True
            self.assertTrue(found_error,
                            msg="The field '{} in serializer '{}' does not contain the error code {}".format(
                                field, serializer_name, code))

        if field:
            if field in serializer.errors:
                assertCodeInErrors(serializer.errors[field])
            else:
                self.fail("The field '{}' in serializer '{}' contains no errors".format(field, serializer_name))
        else:
            if 'non_field_errors' in serializer.errors:
                assertCodeInErrors(serializer.errors['non_field_errors'])
            else:
                self.fail("The serializer '{}' does not contain the non-field error {}".format(serializer_name, code))

    def test_default_modelserializer_field(self):
        class ArtistSerializer(serializers.ModelSerializer):
            class Meta:
                model = Artist
                fields = ('id', 'name')

        with self.assertRaises(exceptions.ImproperlyConfigured):
            ArtistSerializer().fields()  # Fields aren't built until first accessed

    def test_modelserializer_charfield(self):
        class ArtistSerializer(serializers.ModelSerializer):
            id = HashidSerializerCharField(source_field='tests.Artist.id')

            class Meta:
                model = Artist
                fields = ('id', 'name')

        artist = Artist.objects.create(id=128, name="Test Artist")
        orig_id = artist.id
        s = ArtistSerializer(artist)
        self.assertEqual(Artist._meta.get_field('id').salt, s.fields['id'].hashid_salt)
        self.assertTrue(isinstance(s.data['id'], str))
        self.assertEqual(artist.id.hashid, s.data['id'])
        s2 = ArtistSerializer(artist, data={'id': artist.id.hashid, 'name': "Test Artist Changed"})
        self.assertTrue(s2.is_valid())
        artist = s2.save()
        self.assertEqual(artist.id, orig_id)
        self.assertEqual(artist.name, "Test Artist Changed")

    def test_modelserializer_integerfield(self):
        class ArtistSerializer(serializers.ModelSerializer):
            id = HashidSerializerIntegerField(source_field=Artist._meta.get_field('id'))

            class Meta:
                model = Artist
                fields = ('id', 'name')

        artist = Artist.objects.create(id=256, name="Test Artist")
        orig_id = artist.id
        s = ArtistSerializer(artist)
        self.assertTrue(isinstance(s.data['id'], int))
        self.assertEqual(artist.id.id, s.data['id'])
        s2 = ArtistSerializer(artist, data={'id': 256, 'name': "Test Artist Changed"})
        self.assertTrue(s2.is_valid())
        artist = s2.save()
        self.assertEqual(artist.id, orig_id)
        self.assertEqual(artist.name, "Test Artist Changed")

    def test_int_lookups_on_char_field(self):
        class RecordSerializer(serializers.ModelSerializer):
            id = HashidSerializerCharField(source_field='tests.Record.id')
            artist = serializers.PrimaryKeyRelatedField(
                pk_field=HashidSerializerCharField(source_field='tests.Artist.id'),
                queryset=Artist.objects.all(),
                required=False)
            reference_id = HashidSerializerCharField(source_field='tests.Record.reference_id')

            class Meta:
                model = Record
                fields = ('id', 'name', 'artist', 'reference_id')

        artist = Artist.objects.create(id=512, name="Test Artist 512")
        reference_id = Record._meta.get_field('reference_id').get_hashid(1111111)

        # Make sure int lookups of a related field are not allowed on HashidSerializerCharField
        record_id = Record._meta.get_field('id').get_hashid(512)
        data = {
            'id': record_id.hashid,
            'name': "Test Record 512",
            'artist': 512,
            'reference_id': reference_id.hashid,
        }
        s = RecordSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertSerializerError(s, 'artist', 'invalid_hashid')

        # Make sure lookups of a related field are allowed with hashid string and saving a new instance works
        data = {
            'id': record_id.hashid,
            'name': "Test Record 512",
            'artist': artist.id.hashid,
            'reference_id': reference_id.hashid,
        }
        s = RecordSerializer(data=data)
        self.assertTrue(s.is_valid())
        r512 = s.save()
        self.assertEqual(r512.id.hashid, record_id.hashid)
        self.assertEqual(r512.name, "Test Record 512")
        self.assertEqual(r512.artist, artist)

        # Make sure lookups of a related field are allowed even if the hashid looks like an integer
        # With the id 161051 on Artist.id, we get the hashid "6966666" which is all numerics
        artist = Artist.objects.create(id=161051, name="Test Artist 161051")
        self.assertEqual(artist.id.hashid, "6966666")
        record_id = Record._meta.get_field('id').get_hashid(768)
        data = {
            'id': record_id.hashid,
            'name': "Test Record 768",
            'artist': "6966666",
            'reference_id': reference_id.hashid,
        }
        s = RecordSerializer(data=data)
        s.is_valid()
        self.assertTrue(s.is_valid())
        r768 = s.save()
        self.assertEqual(r768.id.hashid, record_id.hashid)
        self.assertEqual(r768.name, "Test Record 768")
        self.assertEqual(r768.artist, artist)

    def test_int_lookups_on_int_field(self):
        class RecordSerializer(serializers.ModelSerializer):
            id = HashidSerializerIntegerField(source_field='tests.Record.id')
            artist = serializers.PrimaryKeyRelatedField(
                pk_field=HashidSerializerIntegerField(source_field='tests.Artist.id'),
                queryset=Artist.objects.all(),
                required=False)
            reference_id = HashidSerializerIntegerField(source_field='tests.Record.reference_id')

            class Meta:
                model = Record
                fields = ('id', 'name', 'artist', 'reference_id')

        artist = Artist.objects.create(id=1024, name="Test Artist 1024")

        # HashidSerializerIntegerField allows int lookups regardless of allow_int_lookup settings
        data = {
            'id': 1024,
            'name': "Test Record 1024",
            'artist': 1024,
            'reference_id': 2222222222,
        }
        s = RecordSerializer(data=data)
        self.assertTrue(s.is_valid())
        r512 = s.save()
        self.assertEqual(r512.id, 1024)
        self.assertEqual(r512.name, "Test Record 1024")
        self.assertEqual(r512.artist, artist)

    def test_invalid_source_field_strings(self):
        with self.assertRaises(ValueError):
            id = HashidSerializerIntegerField(source_field="tests")
        with self.assertRaises(ValueError):
            id = HashidSerializerIntegerField(source_field="tests.Artist")
        with self.assertRaises(ValueError):
            id = HashidSerializerIntegerField(source_field="Artist.id")
        with self.assertRaises(LookupError):
            id = HashidSerializerIntegerField(source_field="foo.Bar.baz")
        with self.assertRaises(LookupError):
            id = HashidSerializerIntegerField(source_field="tests.Bar.baz")
        with self.assertRaises(exceptions.FieldDoesNotExist):
            id = HashidSerializerIntegerField(source_field="tests.Artist.baz")

    def test_modelserializer_with_prefix(self):
        class TrackSerializer(serializers.ModelSerializer):
            id = HashidSerializerCharField(source_field="tests.Track.id")

            class Meta:
                model = Track
                fields = ("id",)

        salt = Track._meta.get_field("id").salt
        alphabet = Track._meta.get_field("id").alphabet
        min_length = Track._meta.get_field("id").min_length
        reference = hashids.Hashids(salt=salt, min_length=min_length, alphabet=alphabet)

        track = Track.objects.create()
        expected = 'albumtrack:' + reference.encode(1)
        self.assertEqual(track.id, expected)

        serializer = TrackSerializer(track)
        self.assertEqual(serializer.data["id"], expected)
