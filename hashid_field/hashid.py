import sys
from functools import total_ordering

from django.utils import six
from hashids import Hashids, _is_uint


class lazy_property(object):
    '''
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    '''

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value

@total_ordering
class Hashid(object):
    def __init__(self, id, salt='', min_length=0, alphabet=Hashids.ALPHABET):
        self._salt = salt
        self._min_length = min_length
        self._alphabet = alphabet

        # If integer, just move on, no need to decode!
        if (isinstance(id, int) or isinstance(id, long)) and id >= 0:
            self._id = id
            return

        # First see if we were given an already-encoded and valid Hashids string
        value = self.decode(id)
        if value:
            self._id = value
        else:
            # Next see if it's a positive integer
            try:
                id = int(id)
            except (TypeError, ValueError):
                raise ValueError("id must be a positive integer or valid Hashid value")
            if not _is_uint(id):
                raise ValueError("id must be a positive integer")

            # Finally, set our internal values
            self._id = id

    @lazy_property
    def _hashids(self):
        return Hashids(salt=self._salt, min_length=self._min_length, alphabet=self._alphabet)

    @lazy_property
    def _hashid(self):
        return self.encode(self._id)

    @property
    def id(self):
        return self._id

    @property
    def hashid(self):
        return self._hashid

    @property
    def hashids(self):
        return self._hashids

    def encode(self, id):
        return self._hashids.encode(id)

    def decode(self, hashid):
        id = self._hashids.decode(hashid)
        if len(id) == 1:
            return id[0]
        else:
            return None

    def __repr__(self):
        return "Hashid({}): {}".format(self._id, self._hashid)

    def __str__(self):
        return self._hashid

    def __int__(self):
        return self._id

    def __long__(self):
        if sys.version_info < (3,):
            return long(self._id)
        else:
            return int(self._id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._id == other._id and self._hashid == other._hashid
        if isinstance(other, six.string_types):
            return self._hashid == other
        if isinstance(other, six.integer_types):
            return self._id == other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self._id < other._id
        if isinstance(other, type(self._id)):
            return self._id < other
        return NotImplemented

    def __len__(self):
        return len(self._hashid)

    def __hash__(self):
        return hash(self._hashid)

    def __reduce__(self):
        return (self.__class__, (self._id, self._salt, self._min_length, self._alphabet))
