import warnings

from django.conf import settings

setattr(settings, 'HASHID_FIELD_SALT', getattr(settings, 'HASHID_FIELD_SALT', ""))
setattr(settings, 'HASHID_FIELD_ALLOW_INT_LOOKUP', getattr(settings, 'HASHID_FIELD_ALLOW_INT_LOOKUP', False))
setattr(settings, 'HASHID_FIELD_LOOKUP_EXCEPTION', getattr(settings, 'HASHID_FIELD_LOOKUP_EXCEPTION', False))
setattr(settings, 'HASHID_FIELD_ENABLE_HASHID_OBJECT', getattr(settings, 'HASHID_FIELD_ENABLE_HASHID_OBJECT', True))
setattr(settings, 'HASHID_FIELD_ENABLE_DESCRIPTOR', getattr(settings, 'HASHID_FIELD_ENABLE_DESCRIPTOR', True))

