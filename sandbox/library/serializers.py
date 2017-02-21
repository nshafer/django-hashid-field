from rest_framework import serializers

from hashid_field.rest import HashidSerializerIntegerField, HashidSerializerCharField
from library.models import Author, Book


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    id = HashidSerializerCharField(source_field='library.Author.id', read_only=True)

    class Meta:
        model = Author
        fields = ('url', 'id', 'name', 'uid', 'books')


class BookSerializer(serializers.HyperlinkedModelSerializer):
    reference_id = HashidSerializerCharField(salt="alternative salt")
    key = HashidSerializerIntegerField(source_field="library.Book.key")
    author_char = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field='library.Author.id'),
        read_only=True, source='author'
    )
    author_int = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerIntegerField(source_field='library.Author.id'),
        read_only=True, source='author')
    author_string = serializers.StringRelatedField(source='author')
    author_slug = serializers.SlugRelatedField(slug_field='uid', read_only=True, source='author')
    editors = serializers.PrimaryKeyRelatedField(
        pk_field=HashidSerializerCharField(source_field='library.Editor.id'),
        read_only=True, many=True
    )

    class Meta:
        model = Book
        fields = ('url', 'id', 'name', 'reference_id', 'key', 'some_number', 'editors',
                  'author', 'author_char', 'author_int', 'author_string', 'author_slug',)
