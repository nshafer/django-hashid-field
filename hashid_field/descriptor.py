from hashids import Hashids

from .hashid import Hashid


class HashidDescriptor(object):
    def __init__(self, name, salt='', min_length=0, alphabet=Hashids.ALPHABET):
        self.name = name
        self.salt = salt
        self.min_length = min_length
        self.alphabet = alphabet

    def __get__(self, instance, owner=None):
        if self.name in instance.__dict__:
            return instance.__dict__[self.name]
        else:
            return None

    def __set__(self, instance, value):
        if isinstance(value, Hashid) or value is None:
            instance.__dict__[self.name] = value
        else:
            try:
                existing = instance.__dict__.get(self.name, None)
                if existing:
                    existing.set(value)
                else:
                    instance.__dict__[self.name] = Hashid(value, salt=self.salt, min_length=self.min_length, alphabet=self.alphabet)
            except ValueError:
                instance.__dict__[self.name] = value
