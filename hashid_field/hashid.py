import sys
from functools import total_ordering

from hashids import Hashids, _is_uint


@total_ordering
class Hashid(object):
    def __init__(self, value, salt='', min_length=0, alphabet=Hashids.ALPHABET, hashids=None, prefix=''):
        self._prefix = prefix
        if hashids is None:
            self._salt = salt
            self._min_length = min_length
            self._alphabet = alphabet
            self._hashids = Hashids(salt=self._salt, min_length=self._min_length, alphabet=self._alphabet)
        else:
            self._hashids = hashids
            self._salt = hashids._salt
            self._min_length = hashids._min_length
            self._alphabet = hashids._alphabet

        if value is None:
            return

        # Is this a positive integer?
        try:
            value = int(value)
        except (TypeError, ValueError):
            # Is it an already-encoded value?
            if not value.startswith(self._prefix):
                raise ValueError("Invalid id prefix")
            without_prefix = value[len(self._prefix):]
            _id = self.decode(without_prefix)
            if _id is None:
                raise ValueError("Invalid id")
            else:
                self._id = _id
                self._hashid = without_prefix
        else:
            if not _is_uint(value):
                raise ValueError("Underlying ids must be positive integers")

            # Finally, set our internal values
            self._id = value
            self._hashid = self.encode(value)


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
        return "Hashid({}): {}".format(self._id, str(self))

    def __str__(self):
        return self._prefix + self._hashid

    def __int__(self):
        return self._id

    def __long__(self):
        return int(self._id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self._id == other._id and
                self._hashid == other._hashid and
                self._prefix == other._prefix
            )
        if isinstance(other, str):
            return str(self) == other
        if isinstance(other, int):
            return int(self) == other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self._id < other._id
        if isinstance(other, type(self._id)):
            return self._id < other
        return NotImplemented

    def __len__(self):
        return len(str(self))

    def __hash__(self):
        return hash(str(self))

    def __reduce__(self):
        return (self.__class__, (self._id, self._salt, self._min_length, self._alphabet, None, self._prefix))
