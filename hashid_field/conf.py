import warnings

from django.conf import settings

if hasattr(settings, 'HASHID_FIELD_ALLOW_INT'):
    warnings.warn("HASHID_FIELD_ALLOW_INT is deprecated, use HASHID_FIELD_ALLOW_INT_LOOKUP",
                  DeprecationWarning, stacklevel=0)
    if not hasattr(settings, 'HASHID_FIELD_ALLOW_INT_LOOKUP'):
        setattr(settings, 'HASHID_FIELD_ALLOW_INT_LOOKUP', getattr(settings, 'HASHID_FIELD_ALLOW_INT', False))

setattr(settings, 'HASHID_FIELD_SALT', getattr(settings, 'HASHID_FIELD_SALT', ""))
setattr(settings, 'HASHID_FIELD_ALLOW_INT_LOOKUP', getattr(settings, 'HASHID_FIELD_ALLOW_INT_LOOKUP', False))
setattr(settings, 'HASHID_FIELD_LOOKUP_EXCEPTION', getattr(settings, 'HASHID_FIELD_LOOKUP_EXCEPTION', False))

