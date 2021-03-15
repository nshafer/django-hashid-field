from django.apps import apps
from django.core import exceptions

from hashids import Hashids
from rest_framework import fields, serializers

from hashid_field.conf import settings
from hashid_field.hashid import Hashid


class UnconfiguredHashidSerialField(fields.Field):
    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        raise exceptions.ImproperlyConfigured(
            "The field '{field_name}' on {parent} must be explicitly declared when used with a ModelSerializer".format(
                field_name=field_name, parent=parent.__class__.__name__))


class HashidSerializerMixin(object):
    usage_text = "Must pass a HashidField, HashidAutoField or 'app_label.model.field'"

    def __init__(self, **kwargs):
        self.hashid_salt = kwargs.pop('salt', settings.HASHID_FIELD_SALT)
        self.hashid_min_length = kwargs.pop('min_length', 7)
        self.hashid_alphabet = kwargs.pop('alphabet', Hashids.ALPHABET)
        self.prefix = kwargs.pop('alphabet', "")

        source_field = kwargs.pop('source_field', None)
        if source_field:
            from hashid_field import HashidField, BigHashidField, HashidAutoField, BigHashidAutoField
            if isinstance(source_field, str):
                try:
                    app_label, model_name, field_name = source_field.split(".")
                except ValueError:
                    raise ValueError(self.usage_text)
                model = apps.get_model(app_label, model_name)
                source_field = model._meta.get_field(field_name)
            elif not isinstance(source_field, (HashidField, BigHashidField, HashidAutoField, BigHashidAutoField)):
                raise TypeError(self.usage_text)
            self.hashid_salt, self.hashid_min_length, self.hashid_alphabet, self.prefix = \
                source_field.salt, source_field.min_length, source_field.alphabet, source_field.prefix
        self._hashids = Hashids(salt=self.hashid_salt, min_length=self.hashid_min_length, alphabet=self.hashid_alphabet)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            value = super().to_internal_value(data)
            return Hashid(value, prefix=self.prefix, hashids=self._hashids)
        except ValueError:
            raise serializers.ValidationError("Invalid int or Hashid string")


class HashidSerializerCharField(HashidSerializerMixin, fields.CharField):
    def to_representation(self, value):
        return str(value)


class HashidSerializerIntegerField(HashidSerializerMixin, fields.IntegerField):
    def to_representation(self, value):
        return int(value)

