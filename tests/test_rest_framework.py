from unittest import skipUnless

from django.core import exceptions
from django.test import TestCase

from tests.models import Artist, Track
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
        s2 = ArtistSerializer(artist, data={'id': 128, 'name': "Test Artist Changed"})
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
        self.assertEqual(reference.encode(1, 1), track.id)

        serializer = TrackSerializer(track)
        self.assertEqual(serializer.data["id"], reference.encode(1, 1))
