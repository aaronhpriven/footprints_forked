# flake8: noqa
# Django settings for footprints project.
import distro
import os.path
import sys
import djcelery
from ccnmtlsettings.shared import common

project = 'footprints'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

if 'ubuntu' in distro.linux_distribution()[0].lower():
    if distro.linux_distribution()[1] == '16.04':
        # 15.04 and later need this set, but it breaks
        # on trusty.
        SPATIALITE_LIBRARY_PATH = 'mod_spatialite'
    elif distro.linux_distribution()[1] == '18.04':
        # On Debian testing/buster, I had to do the following:
        # * Install the sqlite3 and libsqlite3-mod-spatialite packages.
        # * Add the following to writlarge/local_settings.py:
        # SPATIALITE_LIBRARY_PATH =
        # '/usr/lib/x86_64-linux-gnu/mod_spatialite.so' I think the
        # django docs might be slightly out of date here, or just not
        # cover all the cases.
        #
        # I've found that Ubuntu 18.04 also works with this full path
        # to the library file, but not 'mod_spatialite'. I'll raise
        # this issue with Django.
        SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'
elif 'debian' in distro.linux_distribution()[0].lower():
        SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'footprints',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '',
        'ATOMIC_REQUESTS': True,
    }
}

if ('test' in sys.argv or 'jenkins' in sys.argv or 'validate' in sys.argv
        or 'check' in sys.argv):
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.spatialite',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
            'ATOMIC_REQUESTS': True,
        }
    }
    CELERY_ALWAYS_EAGER = True
    BROKER_BACKEND = 'memory'
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    }
    MEDIA_ROOT = './'
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )


# This setting enables a simple search backend for the Haystack layer
# The simple backend using very basic matching via the database itself.
# It's not recommended for production use but it will return results.
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 15

PROJECT_APPS = [
    'footprints.main',
    'footprints.batch',
    'viaf',
]

USE_TZ = True

TEMPLATES[0]['OPTIONS']['context_processors'].extend([  # noqa
    'django.template.context_processors.csrf',
    'footprints.main.utils.permissions',
    'footprints.main.views.django_settings',
])

MIDDLEWARE += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    'reversion.middleware.RevisionMiddleware',
]

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'bootstrapform',
    'infranil',
    'django_extensions',
    'haystack',
    'footprints.main',
    'rest_framework',
    'reversion',
    'djcelery',
    'celery_haystack',
    'footprints.batch',
    's3sign',
    'registration',
    'django.contrib.gis'
]

djcelery.setup_loader()
BROKER_URL = "amqp://guest:guest@localhost:5672//footprints"
CELERYD_CONCURRENCY = 2

CONTACT_US_EMAIL = 'footprints@columbia.edu'

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = '/'

ACCOUNT_ACTIVATION_DAYS = 7

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'footprints.main.utils.BrowsableAPIRendererNoForms'
    ),
    'PAGINATE_BY': 15,
    'DATETIME_FORMAT': '%m/%d/%y %I:%M %p'
}

GOOGLE_MAPS_REVERSE_GEOCODE = \
    'https://maps.googleapis.com/maps/api/geocode/json?address={},{}'

AWS_STORAGE_BUCKET_NAME = "ccnmtl-footprints-static-dev"
MEDIA_URL = 'https://%s.s3.amazonaws.com/uploads/' % AWS_STORAGE_BUCKET_NAME
IMPERSONATE_REQUIRE_SUPERUSER = True

WIND_AFFIL_HANDLERS = [
    'djangowind.auth.StaffMapper',
    'djangowind.auth.SuperuserMapper',
]

ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
REGISTRATION_AUTO_LOGIN = False  # Do not automatically log the user in.
