from hashids import Hashids

from .hashid import Hashid


class HashidDescriptor(object):
    def __init__(self, name, salt='', min_length=0, alphabet=Hashids.ALPHABET, hashids=None, prefix=None):
        self.name = name
        self.salt = salt
        self.min_length = min_length
        self.alphabet = alphabet
        self.prefix = prefix
        if hashids is None:
            self._hashids = Hashids(salt=self.salt, min_length=self.min_length, alphabet=self.alphabet)
        else:
            self._hashids = hashids

    def __get__(self, instance, owner=None):
        if instance is not None and self.name in instance.__dict__:
            return instance.__dict__[self.name]
        else:
            return None

    def __set__(self, instance, value):
        if isinstance(value, Hashid) or value is None:
            instance.__dict__[self.name] = value
        else:
            try:
                instance.__dict__[self.name] = Hashid(value, hashids=self._hashids, prefix=self.prefix)
            except ValueError:
                instance.__dict__[self.name] = value
