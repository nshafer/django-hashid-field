import sys
from django import forms
from django.core import exceptions, checks
from django.db import models
from django.db.models.lookups import FieldGetDbPrepValueMixin, FieldGetDbPrepValueIterableMixin, BuiltinLookup
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import widgets as admin_widgets
from django.db.models import lookups, Lookup
from hashids import Hashids

from .descriptor import HashidDescriptor
from .hashid import Hashid
from .conf import settings


def check_for_int(field, value):
    try:
        hashid = field.encode_id(value)
    except ValueError:
        raise TypeError(field.error_messages['invalid'] % {'value': value})
    if not field.allow_int:
        # Check the given value to see if it's an integer lookup, and disallow it.
        # It is possible for real Hashids to resemble integers, especially if the alphabet == "0123456789", so we
        # can't just check if `int(value)` succeeds.
        # Instead, we'll encode the value with the given Hashid*Field, and if resulting Hashids string
        # doesn't match the given value, then we know that something fishy is going on (an integer lookup)
        if value != hashid.hashid:
            raise TypeError(field.error_messages['invalid_hashid'] % {'value': value})
    return hashid


class ExactHashidLookup(lookups.Exact):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)
        try:
            check_for_int(lhs.output_field, rhs)
        except TypeError:
            self.rhs = -1


class ExactHashidIterableLookup(lookups.In):
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)
        for value in rhs:
            check_for_int(lhs.output_field, value)


class HashidLookupMixin(object):
    def process_hashid_lookup(self, value):
        try:
            hashid = self.lhs.output_field.encode_id(value)
        except ValueError:
            raise TypeError(self.lhs.output_field.error_messages['invalid'] % {'value': value})
        if not self.lhs.output_field.allow_int:
            # Check the given value to see if it's an integer lookup, and disallow it.
            # It is possible for real Hashids to resemble integers, especially if the alphabet == "0123456789", so we
            # can't just check if `int(value)` succeeds.
            # Instead, we'll encode the value with the given Hashid*Field, and if resulting Hashids string
            # doesn't match the given value, then we know that something fishy is going on (an integer lookup)
            if value != hashid.hashid:
                raise TypeError(self.lhs.output_field.error_messages['invalid_hashid'] % {'value': value})
        return hashid

    # def process_rhs(self, compiler, connection):
    #     class InvalidHashid(object):
    #         pass
    #     print("process_rhs", self.rhs)
    #     sql, params = super().process_rhs(compiler, connection)
    #     sql = list(sql)
    #     params = list(params)
    #     print("  got", sql, params)
    #     new_params = []
    #     for param in params:
    #         try:
    #             hashid = check_for_int(self.lhs.output_field, param)
    #             print("param to hashid", param, hashid.id)
    #             param = hashid.id
    #         except TypeError:
    #             param = InvalidHashid
    #         new_params.append(param)
    #     print("new_params", new_params)
    #     final_params = [a for a in new_params if a != InvalidHashid]
    #     print("final_params", final_params)
    #     if len(final_params) <= 0:
    #         raise exceptions.EmptyResultSet
    #     return sql, final_params

    # def as_sql(self, compiler, connection):
    #     lhs, params = self.process_lhs(compiler, connection)
    #     print("lhs", lhs, params)
    #     rhs, rhs_params = self.process_rhs(compiler, connection)
    #     print("rhs", rhs, rhs_params)
    #     params.extend(rhs_params)
    #
    #     new_params = []
    #     for param in params:
    #         try:
    #             hashid = check_for_int(self.lhs.output_field, param)
    #             print("param to hashid", param, hashid.id)
    #             param = hashid.id
    #         except TypeError:
    #             raise exceptions.EmptyResultSet
    #         new_params.append(param)
    #     print("new_params", new_params)
    #
    #     return "{} = {}".format(lhs, rhs), new_params


class HashidLookup(HashidLookupMixin, lookups.Exact):
    prepare_rhs = False

    def get_prep_lookup(self):
        print("get_prep_lookup", self.lhs, self.rhs)
        value = super().get_prep_lookup()
        print("  got", value)
        try:
            hashid = self.process_hashid_lookup(value)
        except TypeError:
            raise exceptions.EmptyResultSet
        return hashid.id


class HashidIterableLookup(HashidLookupMixin, lookups.In):
    prepare_rhs = False


class HashidFieldMixin(object):
    default_error_messages = {
        'invalid': _("'%(value)s' value must be a positive integer or a valid Hashids string."),
        'invalid_hashid': _("'%(value)s' value must be a valid Hashids string."),
    }
    exact_lookups = ('exact', 'iexact', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith')
    iterable_lookups = ('in',)
    passthrough_lookups = ('isnull',)

    def __init__(self, salt=settings.HASHID_FIELD_SALT, min_length=7, alphabet=Hashids.ALPHABET,
                 allow_int=settings.HASHID_FIELD_ALLOW_INT, *args, **kwargs):
        self.salt = salt
        self.min_length = min_length
        self.alphabet = alphabet
        self.allow_int = allow_int
        super(HashidFieldMixin, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(HashidFieldMixin, self).deconstruct()
        kwargs['min_length'] = self.min_length
        kwargs['alphabet'] = self.alphabet
        return name, path, args, kwargs

    def check(self, **kwargs):
        errors = super(HashidFieldMixin, self).check(**kwargs)
        errors.extend(self._check_alphabet_min_length())
        errors.extend(self._check_salt_is_set())
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

    def _check_salt_is_set(self):
        if self.salt is None or self.salt == "":
            return [
                checks.Warning(
                    "'salt' is not set",
                    hint="Pass a salt value in your field or set settings.HASHID_FIELD_SALT",
                    obj=self,
                    id="HashidField.W001",
                )
            ]
        return []

    def encode_id(self, id):
        return Hashid(id, salt=self.salt, min_length=self.min_length, alphabet=self.alphabet)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return self.encode_id(value)

    def get_lookup(self, lookup_name):
        print("get_lookup", lookup_name)
        if lookup_name in self.exact_lookups:
            return HashidLookup
        if lookup_name in self.iterable_lookups:
            return HashidIterableLookup
        if lookup_name in self.passthrough_lookups:
            return super().get_lookup(lookup_name)
        return None  # Otherwise, we don't allow lookups of this type

    def to_python(self, value):
        if isinstance(value, Hashid):
            return value
        if value is None:
            return value
        try:
            hashid = self.encode_id(value)
        except ValueError:
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'value': value},
            )
        return hashid

    def get_prep_value(self, value):
        if value is None or value == '':
            return None
        if isinstance(value, Hashid):
            return value.id
        try:
            hashid = self.encode_id(value)
        except ValueError:
            raise TypeError(self.error_messages['invalid'] % {'value': value})
        return hashid.id

    def contribute_to_class(self, cls, name, **kwargs):
        super(HashidFieldMixin, self).contribute_to_class(cls, name, **kwargs)
        # setattr(cls, "_" + self.attname, getattr(cls, self.attname))
        setattr(cls, self.attname, HashidDescriptor(self.attname, salt=self.salt, min_length=self.min_length, alphabet=self.alphabet))


class HashidField(HashidFieldMixin, models.IntegerField):
    description = "A Hashids obscured IntegerField"

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        if defaults.get('widget') == admin_widgets.AdminIntegerFieldWidget:
            defaults['widget'] = admin_widgets.AdminTextInputWidget
        return super(HashidField, self).formfield(**defaults)


class HashidAutoField(HashidFieldMixin, models.AutoField):
    description = "A Hashids obscured AutoField"


# Monkey patch Django REST Framework, if it's installed, to throw exceptions if fields aren't explicitly defined in
# ModelSerializers. Not doing so can lead to hard-to-debug behavior.
try:
    from rest_framework.serializers import ModelSerializer
    from hashid_field.rest import UnconfiguredHashidSerialField

    ModelSerializer.serializer_field_mapping[HashidField] = UnconfiguredHashidSerialField
    ModelSerializer.serializer_field_mapping[HashidAutoField] = UnconfiguredHashidSerialField
except ImportError:
    pass
