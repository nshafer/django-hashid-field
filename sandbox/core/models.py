from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from hashids import Hashids
from hashid_field import HashidAutoField

field = FlatPage._meta.fields[0]
field.__class__ = HashidAutoField
field.salt = settings.HASHID_FIELD_SALT
field.min_length = 7
field.alphabet = Hashids.ALPHABET
field.allow_int_lookup = True

