"""
Django settings for vidhub project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from .config import Config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = Config.DEBUG

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = Config.SECRET_KEY

ALLOWED_HOSTS = Config.ALLOWED_HOSTS


# Application definition

INSTALLED_APPS = [
	'streamer.apps.StreamerConfig',
	'users.apps.UsersConfig',

	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	'django_rq',
	'video_encoding',
	'maintenance_mode',
]


MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'maintenance_mode.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'vidhub.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'django.template.context_processors.media',
				'maintenance_mode.context_processors.maintenance_mode',
			],
		},
	},
]

WSGI_APPLICATION = 'vidhub.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = Config.DATABASES


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
	os.path.join(BASE_DIR, "static"),
	'/var/www/static/',
]


MEDIA_ROOT= os.path.join(BASE_DIR, 'media/')
MEDIA_URL= "/media/"


RQ_QUEUES = {
	'default': {
		'HOST': 'localhost',
		'PORT': 6379,
		'DB': 0,
		'DEFAULT_TIMEOUT': 3600,
	},
	# 'with-sentinel': {
	#     'SENTINELS': [('localhost', 26736), ('localhost', 26737)],
	#     'MASTER_NAME': 'redismaster',
	#     'DB': 0,
	#     'PASSWORD': 'secret',
	#     'SOCKET_TIMEOUT': None,
	#     'CONNECTION_KWARGS': {
	#         'socket_connect_timeout': 0.3
	#     },
	# },
	# 'high': {
	#     'URL': os.getenv('REDISTOGO_URL', 'redis://localhost:6379/0'), # If you're on Heroku
	#     'DEFAULT_TIMEOUT': 500,
	# },
	# 'low': {
	#     'HOST': 'localhost',
	#     'PORT': 6379,
	#     'DB': 0,
	# }
}

# RQ_EXCEPTION_HANDLERS = ['path.to.my.handler'] # If you need custom exception handlers

VIDEO_ENCODING_FORMATS = {
	'FFmpeg': [
		{
			'name': 'mp4_sd',
			'extension': 'mp4',
			'params': [
				'-codec:v', 'libx264', '-crf', '20', '-preset', 'medium',
				'-b:v', '1000k', '-maxrate', '1000k', '-bufsize', '2000k',
				'-vf', 'scale=-2:480',  # http://superuser.com/a/776254
				'-codec:a', 'aac', '-b:a', '128k', '-strict', '-2',
			],
		},
		{
			'name': 'mp4_hd',
			'extension': 'mp4',
			'params': [
				'-codec:v', 'libx264', '-crf', '20', '-preset', 'medium',
				'-b:v', '3000k', '-maxrate', '3000k', '-bufsize', '6000k',
				'-vf', 'scale=-2:720',
				'-codec:a', 'aac', '-b:a', '128k', '-strict', '-2',
			],
		},
	]
}

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'

MAINTENANCE_MODE = Config.MAINTENANCE_MODE
MAINTENANCE_MODE_TEMPLATE = Config.MAINTENANCE_MODE_TEMPLATE
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = Config.MAINTENANCE_MODE_IGNORE_ADMIN_SITE
MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = Config.MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
)

DOMAIN = Config.DOMAIN

EMAIL_HOST_USER = Config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = Config.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = Config.EMAIL_USE_TLS
EMAIL_HOST = Config.EMAIL_HOST
EMAIL_PORT = Config.EMAIL_PORT

AUTH_USER_MODEL = 'users.CustomUser'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'