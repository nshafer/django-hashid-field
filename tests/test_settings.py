import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "tests",
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
