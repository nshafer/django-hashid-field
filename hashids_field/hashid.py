from hashids import Hashids, _is_uint


class Hashid(object):
    def __init__(self, id, salt='', min_length=0, alphabet=Hashids.ALPHABET):
        self.hashids = Hashids(salt=salt, min_length=min_length, alphabet=alphabet)
        self.id = id
        self.hashid = self.set(id)

    def encode(self, id):
        return self.hashids.encode(id)

    def decode(self, hashid):
        id = self.hashids.decode(hashid)
        if len(id) == 1:
            return id[0]
        else:
            return None

    def set(self, id):
        value = self.decode(id)
        if value:
            self.id = value
            self.hashid = id
            return self.hashid
        try:
            id = int(id)
            if not _is_uint(id):
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError("id must be positive integer or valid Hashid value")
        self.id = id
        self.hashid = self.encode(id)
        return self.hashid

    def __repr__(self):
        return "Hashid({}): {}".format(self.id, self.hashid)

    def __str__(self):
        return self.hashid

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id and self.hashid == other.hashid
        return NotImplemented

    def __len__(self):
        return len(self.hashid)
