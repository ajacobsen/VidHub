import os

class Config:
	SECRET_KEY = '4p#&7+l#ws*s^rm(o&qh0ph6h3p*n2wdmkmy2i&#q$5jtkm1m5'
	ALLOWED_HOSTS = ['vidhub']
	ROOT_URLCONF = 'vidhub.urls_dev'

	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'NAME': 'vidhub',
			'USER': 'vidhub',
			'PASSWORD': 'sommer',
			'HOST': '127.0.0.1',
			'PORT': '3306',
		}
	}

	DEBUG = False

	DOMAIN = 'example.com'

	EMAIL_HOST_USER='noreply@example.com'
	EMAIL_HOST_PASSWORD='PASSWORD'
	EMAIL_USE_TLS = True
	EMAIL_HOST = 'smtp.example.com'
	EMAIL_PORT = 587
	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

	LOGGING = {
	    'version': 1,
	    'disable_existing_loggers': False,
	    'handlers': {
	        'console': {
	            'class': 'logging.StreamHandler',
	        },
	    },
	    'loggers': {
	        '': {
	            'handlers': ['console'],
	            'level': 'INFO',
	        },
	    },
	}

	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	STATIC_ROOT = os.path.join(BASE_DIR, '/static/')
	MEDIA_ROOT= os.path.join(BASE_DIR, '/media/')
	