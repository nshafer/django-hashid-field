from django import forms
from django.conf import settings
from django.core import exceptions, checks
from django.db import models
from django.utils.translation import ugettext_lazy as _
from hashids import Hashids

from .descriptor import HashidDescriptor
from .hashid import Hashid


class HashidFieldMixin(object):
    default_error_messages = {
        'invalid': _("'%(value)s' value must be a positive integer or a valid Hashids string."),
    }

    def __init__(self, salt=settings.SECRET_KEY, min_length=7, alphabet=Hashids.ALPHABET, *args, **kwargs):
        self.salt = salt
        self.min_length = min_length
        self.alphabet = alphabet
        super(HashidFieldMixin, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(HashidFieldMixin, self).deconstruct()
        kwargs['min_length'] = self.min_length
        kwargs['alphabet'] = self.alphabet
        return name, path, args, kwargs

    def check(self, **kwargs):
        errors = super(HashidFieldMixin, self).check(**kwargs)
        errors.extend(self._check_alphabet_min_length())
        return errors

    def _check_alphabet_min_length(self):
        if len(self.alphabet) < 16:
            return [
                checks.Error(
                    "'alphabet' must contain a minimum of 16 characters",
                    hint="Add more characters to custom 'alphabet'",
                    obj=self,
                    id='HashidField.E001',
                )
            ]
        return []

    def encode_id(self, id):
        return Hashid(id, salt=self.salt, min_length=self.min_length, alphabet=self.alphabet)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return self.encode_id(value)

    def to_python(self, value):
        if value and not isinstance(value, Hashid):
            try:
                return self.encode_id(value)
            except ValueError:
                raise exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
        return value

    def get_prep_value(self, value):
        if value is None or value == '':
            return None
        if not isinstance(value, Hashid):
            try:
                value = self.encode_id(value)
            except ValueError:
                raise TypeError(self.error_messages['invalid'] % {'value': value})
        return value.id

    def contribute_to_class(self, cls, name, **kwargs):
        super(HashidFieldMixin, self).contribute_to_class(cls, name, **kwargs)
        # setattr(cls, "_" + self.attname, getattr(cls, self.attname))
        setattr(cls, self.attname, HashidDescriptor(self.attname, salt=self.salt, min_length=self.min_length, alphabet=self.alphabet))


class HashidField(HashidFieldMixin, models.IntegerField):
    description = "A Hashids obscured IntegerField"

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        return super(HashidField, self).formfield(**defaults)


class HashidAutoField(HashidFieldMixin, models.AutoField):
    description = "A Hashids obscured AutoField"
