from django.conf import settings


setattr(settings, 'HASHID_FIELD_SALT', getattr(settings, 'HASHID_FIELD_SALT', ""))
setattr(settings, 'HASHID_FIELD_ALLOW_INT', getattr(settings, 'HASHID_FIELD_ALLOW_INT', True))
