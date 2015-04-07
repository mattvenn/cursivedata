# Django settings for testsite project.

from os import path
import sys
import socket

hostname = socket.gethostname()
# Try and import pycairo or fallback to cairocffi and install as cairo
try:
    import cairo
except ImportError:
    import cairocffi
    cairocffi.install_as_pycairo()

from django.core.urlresolvers import reverse_lazy

PROJECT_ROOT = path.dirname(path.dirname(__file__))
LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = 'localhost'

# debug on dev machines
if hostname == 'vennzaa1.miniserver.com':
    DEBUG = False
else:
    DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Matt Venn', 'matt@mattvenn.net'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cursivedata',
        'USER': 'cursivedata',
        'HOST': 'localhost',
        'PASSWORD': 'cursivedata',
                },
    'sqllite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(PROJECT_ROOT, 'db', 'www.sqlite'),
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Greenwich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

import warnings
warnings.filterwarnings(
        'error', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/polarsite/polargraphenergymonitor/testsite/media/admin/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/media/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'i@))&amp;55xb)_981^88xtxtd6bds+bn_be&amp;3w)uttk*+w*fs+%7v'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'www.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'www.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(PROJECT_ROOT, 'www', 'templates'),
    "cursivedata/templates"
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party libraries
    'tastypie',
    'django_nose',
    'south',

    # Our apps
    'landing',
    'cursivedata',
    )

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
if DEBUG:
    default_logger = {
                        'handlers': ['console','file'],
                        'level': 'DEBUG',
                     }
else:
    default_logger = {
                        'handlers': ['file'],
                        'level': 'INFO',
                     }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] %(process)d %(module)s : %(message)s'
                    },
                },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
        'file': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename': 'log/info.log',
                    'formatter': 'verbose',
        },
    },
    'loggers': {
        'endpoint': default_logger,
        'api': default_logger,
        'graphics': default_logger,
        'data': default_logger,
        'generator': default_logger,
        'views': default_logger,
        'pipeline': default_logger,
    },
}
LOGIN_URL = reverse_lazy('login')
LOGOUT_URL = reverse_lazy('logout')
