import sys
from functools import total_ordering

from hashids import Hashids, _is_uint


@total_ordering
class Hashid(object):
    def __init__(self, id, salt='', min_length=0, alphabet=Hashids.ALPHABET, hashids=None, prefix=None):
        if hashids is None:
            self._salt = salt
            self._min_length = min_length
            self._alphabet = alphabet
            self._hashids = Hashids(salt=self._salt, min_length=self._min_length, alphabet=self._alphabet)
            self._prefix = None
        else:
            self._hashids = hashids
            self._salt = hashids._salt
            self._min_length = hashids._min_length
            self._alphabet = hashids._alphabet
            self._prefix = prefix

        # First see if we were given an already-encoded and valid Hashids string
        value = self.decode(id)
        if value is not None:
            if self._prefix:
                prefix, value = value
                if prefix != self._prefix:
                    raise ValueError("Invalid id")
            self._id = value
            self._hashid = id
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
            self._hashid = self.encode(id)
            if self._prefix:
                self._hashid = self.encode(self._prefix, id)

    @property
    def id(self):
        return self._id

    @property
    def hashid(self):
        return self._hashid

    @property
    def hashids(self):
        return self._hashids

    def encode(self, *id):
        return self._hashids.encode(*id)

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
        return int(self._id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._id == other._id and self._hashid == other._hashid
        if isinstance(other, str):
            return self._hashid == other
        if isinstance(other, int):
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
