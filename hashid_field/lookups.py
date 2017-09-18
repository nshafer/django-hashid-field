from django.db.models import lookups
from hashid_field.hashid import Hashid


def get_id_for_hashid_field(field, value):
    if isinstance(value, Hashid):
        return value.id
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
    return hashid.id


class HashidLookupMixin(object):
    def get_db_prep_lookup(self, value, connection):
        # There are two modes this method can be called in... a single value or an iterable of values (usually a set)
        # For a single value, just try to process it, then return the value
        # For multiple values, process each one in turn.
        # For relational fields, use the 'field' attribute of the output_field
        field = getattr(self.lhs.output_field, 'field', self.lhs.output_field)
        if self.get_db_prep_lookup_value_is_iterable:
            return ('%s', [get_id_for_hashid_field(field, val) for val in value])
        else:
            return ('%s', [get_id_for_hashid_field(field, value)])


class HashidLookup(HashidLookupMixin, lookups.Exact):
    prepare_rhs = False


class HashidIterableLookup(HashidLookupMixin, lookups.In):
    prepare_rhs = False


