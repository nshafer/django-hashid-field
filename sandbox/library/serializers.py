from rest_framework import serializers

from hashid_field.rest import HashidSerializerIntegerField, HashidSerializerCharField
from library.models import Author, Book


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Author
        fields = ('url', 'id', 'name', 'uid')


class BookSerializer(serializers.HyperlinkedModelSerializer):
    reference_id = HashidSerializerCharField(salt="alternative salt")
    key = HashidSerializerIntegerField(source_field="library.Book.key")

    class Meta:
        model = Book
        fields = ('url', 'id', 'name', 'author', 'reference_id', 'key', 'some_number')
