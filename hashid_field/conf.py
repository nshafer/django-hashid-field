from django.conf import settings


setattr(settings, 'HASHID_FIELD_SALT', getattr(settings, 'HASHID_FIELD_SALT', ""))
