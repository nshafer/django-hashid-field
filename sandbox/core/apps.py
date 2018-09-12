from django.apps import AppConfig
from django.conf import settings
from hashids import Hashids

from hashid_field import HashidAutoField


class CoreConfig(AppConfig):
    name = 'core'

