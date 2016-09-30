from django import forms
from django.conf import settings
from django.core import exceptions, checks
from django.db import models
from django.utils.functional import Promise
from django.utils.translation import ugettext_lazy as _
from hashids import Hashids

from .hashid import Hashid


class HashidsFieldMixin(object):
    default_error_messages = {
        'invalid': _("'%(value)s' value must be a positive integer or a valid Hashids string."),
    }

    def __init__(self, min_length=7, alphabet=Hashids.ALPHABET, *args, **kwargs):
        self.min_length = min_length
        self.alphabet = alphabet
        super(HashidsFieldMixin, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(HashidsFieldMixin, self).deconstruct()
        kwargs['min_length'] = self.min_length
        kwargs['alphabet'] = self.alphabet
        return name, path, args, kwargs

    def check(self, **kwargs):
        errors = super(HashidsFieldMixin, self).check(**kwargs)
        errors.extend(self._check_alphabet_min_length())
        return errors

    def _check_alphabet_min_length(self):
        if len(self.alphabet) < 16:
            return [
                checks.Error(
                    "'alphabet' must contain a minimum of 16 characters",
                    hint="Add more characters to custom 'alphabet'",
                    obj=self,
                    id='HashidsField.E001',
                )
            ]
        return []

    def encode_id(self, id):
        return Hashid(id, salt=settings.SECRET_KEY, min_length=self.min_length, alphabet=self.alphabet)

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
                    params={'value': id},
                )
        return value

    def get_prep_value(self, value):
        if value is None:
            return None
        if not isinstance(value, Hashid):
            try:
                value = self.encode_id(value)
            except ValueError:
                raise TypeError(self.error_messages['invalid'] % {'value': value})
        return value.id

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        try:
            hashid = self.to_python(value)
            setattr(model_instance, self.attname, hashid)
            return hashid
        except exceptions.ValidationError:
            return value


class HashidsField(HashidsFieldMixin, models.IntegerField):
    description = "A Hashids obscured IntegerField"

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        return super(HashidsField, self).formfield(**defaults)


class HashidsAutoField(HashidsFieldMixin, models.AutoField):
    description = "A Hashids obscured AutoField"
