# -*- coding: utf-8 -*-
import os.path

PROJECT_NAME = 'Car Battle'
SITE_DIR = 'gta'
FACEBOOK_APP_NAME = 'car_battle'
FACEBOOK_INTERNAL = True
IS_FB = False
IS_TW = False

MAINTANCE_MODE = False

# if os.path.abspath(__file__).startswith('/Users/marek/Sites/' + SITE_DIR):
# PROJECT_DIR = '/Users/marek/Sites/' + SITE_DIR
# LOCAL = True
# DEBUG = True
# else:
# PROJECT_DIR = '/home/marek/' + SITE_DIR
# LOCAL = False
# DEBUG = False

LOCAL = True
DEBUG = True
PROJECT_DIR = '/var/www/gta'

TEMPLATE_DEBUG = DEBUG
SQL_DEBUG = DEBUG
INTERNAL_IPS = ['127.0.0.1', '168.168.1.2', '94.78.183.198', '69.63.187.251']

if LOCAL:
    db_user = 'root'
    db_pass = ''
else:
    db_user = 'root'
    db_pass = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'carbattle',
        'USER': db_user,
        'PASSWORD': db_pass,
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'archive': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'archive',
        'USER': db_user,
        'PASSWORD': db_pass,
        'HOST': '',
        'PORT': '',
    },
    # 'stat': {
    # 	'ENGINE': 'django.db.backends.mysql',
    #         'NAME': 'stat',
    #         'USER': db_user,
    #         'PASSWORD': db_pass,
    #         'HOST': '',
    #         'PORT': '',
    # }
}

DATABASE_OPTIONS = {
    'charset': 'utf8',
}

if LOCAL:
    SITE_ROOT_URL = 'http://10.0.0.2:9000/'
    MEDIA_URL = 'http://10.0.0.2:9000/static/gta/'
    BASE_MEDIA_URL = 'http://10.0.0.2:9000/static/base/'
    SITE_URL = SITE_ROOT_URL
else:
    SITE_ROOT_URL = 'http://www.car-battle.com/'
    MEDIA_URL = '/static/gta/'
    BASE_MEDIA_URL = 'http://static.madfb.com/base/'
    SITE_URL = SITE_ROOT_URL

MEDIA_ROOT = '/var/www/gta/static/'
ADMIN_MEDIA_PREFIX = MEDIA_URL + 'admin/'

SECRET_KEY = ''

ADMINS = (
    ('marek', ''),
)
MANAGERS = ADMINS
ADMIN_UIDS = ('1',)  # , '2')

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = False
LANGUAGES = (
    ('en', 'English'),
    # ('pl', 'Polish'),
    # ('de', 'German')
)
LANGUAGE_CODE = 'en-us'

ROOT_URLCONF = SITE_DIR + '.urls'
APPEND_SLASH = True
SEND_BROKEN_LINK_EMAILS = False
SITE_ID = 1

AUTH_PROFILE_MODULE = 'userprofile.userprofile'
# LOGIN_URL = '/accounts/login/'
# LOGOUT_URL = '/accounts/logout/'
# LOGIN_REDIRECT_URL = '/'

ACCOUNT_ACTIVATION_DAYS = 7

EMAIL_USE_TLS = True
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'Car Battle <noreply@car-battle.com>'

DATE_FORMAT = 'Y-m-d'

SESSION_COOKIE_NAME = SITE_DIR + '_cookie'
# SESSION_COOKIE_AGE = 3600 * 24 # 24h
SESSION_COOKIE_AT_BROWSER_CLOSE = False

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

if LOCAL:
    CACHE_BACKEND = 'dummy:///'
    # CACHE_BACKEND = "locmem:///"
    # CACHE_BACKEND = 'db://django_cache?timeout=86400'
    CACHE_TIMEOUT = 60 * 5
    CACHE_PREFIX = "GTA_"
else:
    # CACHE_BACKEND = 'memcached://127.0.0.1:11000/?timeout=86400'
    # CACHE_BACKEND = 'db://django_cache?timeout=86400'
    # CACHE_BACKEND = 'dummy:///'
    CACHE_BACKEND = "locmem:///"
    CACHE_TIMEOUT = 60 * 15
    CACHE_PREFIX = "GTA_"

DEBUG_TOOLBAR_PANELS = (
    # 'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.templates.TemplatesDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    # 'debug_toolbar.panels.signals.SignalDebugPanel',
    # 'debug_toolbar.panels.logger.LoggingPanel',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'facebook.djangofb.FacebookMiddleware',
    # 'facebookconnect.middleware.FacebookConnectMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'common.middleware.engine.EngineMiddleware',
    # 'common.middleware.login_required.LoginRequiredMiddleware',
    # 'common.middleware.fb_connect.fbMiddleware',
    # 'common.middleware.ProfilerMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    # 'django.contrib.flatpages',
    'django.contrib.messages',
    # 'annoying',
    'common',
    # 'facebookconnect',
    # --- Car Battle
    'registration',
    'userprofile',
    # 'achievement',
    'album',
    'auction',
    'battle',
    'encyclopedia',
    'friend',
    'gift',
    'job',
    'main',
    'wishlist',
    'msg',
    'achievement',
    # --- Internal
    # 'intranet',
    # 'debug_toolbar',
)

# AUTHENTICATION_BACKENDS = (
# 	'facebookconnect.models.FacebookBackend',
# 	'django.contrib.auth.backends.ModelBackend',
# )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'common.context_processors.messages',
    'common.context_processors.base',
    'common.helpers.sql_debug.sqldebug',
)

LOGIN_EXEMPT_URLS = (
    r'^$',
    r'^robots.txt$',
    r'^favicon.ico$',
    r'^accounts/',
    r'^intranet/',
    r'^profile/[A-Za-z0-9]{2,20}/$',
    r'^profile/edit/(?P<invite_code>[\w\-_0-9]{16})/(?P<secret_code>[\w\-_0-9]{16})/$',
    r'^encyclopedia/',
    r'^auction/',
    r'^tutorial/',
    r'^leaderboard/',
    r'^friend/invite/.+',
    r'^static/',
    r'^main/payment/process/.+',
    r'^partner.*\.html$',
    r'^auth-.*',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

DUMMY_FACEBOOK_INFO = {
    'uid': 0,
    'name': '(Private)',
    'first_name': '(Private)',
    'pic_square_with_logo': 'http://www.facebook.com/pics/t_silhouette.gif',
    'affiliations': None,
    'status': None,
    'proxied_email': None,
}

FACEBOOK_CACHE_TIMEOUT = 1800
FB_API_KEY = ''

FLICKR_API_KEY = ''
FLICKR_API_SECRET = ''
FLICKR_USER_ID = ''

MY_FACEBOOK_UID = ''
FACEBOOK_APP_NAME = ''
FACEBOOK_API_KEY = ''
FACEBOOK_SECRET_KEY = ''
FACEBOOK_APP_ID = ''
FACEBOOK_APP_URL = ''
FACEBOOK_INTERNAL = True

SRPOINTS_SECRET = {
    'fb': '',
    'www': '',
}

OFFERPAL_SECRET = {
    'fb': '',
}

IM = {
    # 'blip': {'username': 'carbattle', 'password': ''},
    'twitter': {'username': 'carbattle', 'password': ''},
    'jabber_bot': {'username': 'bot@madfb.com', 'password': ''},
}

