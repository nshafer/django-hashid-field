from functools import total_ordering

from hashids import Hashids


def _is_uint(number):
    """Returns whether a value is an unsigned integer."""
    try:
        return number == int(number) and number >= 0
    except ValueError:
        return False


def _is_str(candidate):
    """Returns whether a value is a string."""
    return isinstance(candidate, str)


@total_ordering
class Hashid(object):
    def __init__(self, value, salt="", min_length=0, alphabet=Hashids.ALPHABET, prefix="", hashids=None):
        self._salt = salt
        self._min_length = min_length
        self._alphabet = alphabet
        self._prefix = str(prefix)

        # If hashids is provided, it's for optimization only, and should be initialized with the same salt, min_length
        # and alphabet, or else we will run into problems
        self._hashids = hashids or Hashids(salt=self._salt, min_length=self._min_length, alphabet=self._alphabet)
        if not self._valid_hashids_object():
            raise Exception("Invalid hashids.Hashids object")

        if value is None:
            raise ValueError("id must be a positive integer or a valid Hashid string")

        # Check if `value` is an integer first as it is much faster than checking if a string is a valid hashid
        if _is_uint(value):
            self._id = value
            self._hashid = self.encode(value)
        elif _is_str(value):
            # `value` could be a string representation of an integer and not a hashid, but since the Hashids algorithm
            # requires a minimum of 16 characters in the alphabet, `int(value, base=10)` will always throw a ValueError
            # for a hashids string, as it's impossible to represent a hashids string with only chars [0-9].
            try:
                value = int(value, base=10)
            except (TypeError, ValueError):
                # We must assume that this string is a hashids representation.
                # Verify that it begins with the prefix, which could be the default ""
                if not value.startswith(self._prefix):
                    raise ValueError("value must begin with prefix {}".format(self._prefix))

                without_prefix = value[len(self._prefix):]
                _id = self.decode(without_prefix)
                if _id is None:
                    raise ValueError("id must be a positive integer or a valid Hashid string")
                else:
                    self._id = _id
                    self._hashid = without_prefix
            else:
                if not _is_uint(value):
                    raise ValueError("value must be a positive integer")

                # Finally, set our internal values
                self._id = value
                self._hashid = self.encode(value)
        elif isinstance(value, int) and value < 0:
            raise ValueError("value must be a positive integer")
        else:
            raise ValueError("value must be a positive integer or a valid Hashid string")

    @property
    def id(self):
        return self._id

    @property
    def hashid(self):
        return self._hashid

    @property
    def prefix(self):
        return self._prefix

    @property
    def hashids(self):
        return self._hashids

    def encode(self, id):
        return self._hashids.encode(id)

    def decode(self, hashid):
        ret = self._hashids.decode(hashid)
        if len(ret) == 1:
            return ret[0]
        else:
            return None

    def _valid_hashids_object(self):
        # The hashids.Hashids class randomizes the alphabet and pulls out separators and guards, thus not being
        # reversible. So all we can test is that the length of the alphabet, separators and guards are equal to the
        # original alphabet we gave it. We could also check that all of the characters we gave it are present, but that
        # seems excessive... this test will catch most errors.
        return self._salt == self._hashids._salt \
            and self._min_length == self._hashids._min_length \
            and len(self._alphabet) == len(self._hashids._alphabet + self._hashids._separators + self._hashids._guards)

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
        return (self.__class__, (self._id, self._salt, self._min_length, self._alphabet, self._prefix, None))
