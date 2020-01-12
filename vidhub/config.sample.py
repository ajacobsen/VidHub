class Config:
	SECRET_KEY = '4p#&7+l#ws*s^rm(o&qh0ph6h3p*n2wdmkmy2i&#q$5jtkm1m5'
	ALLOWED_HOSTS = ['vidhub']
	ROOT_URLCONF = 'vidhub.urls'
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

	MAINTENANCE_MODE = None
	MAINTENANCE_MODE_TEMPLATE = 'streamer/maintenance.html'
	MAINTENANCE_MODE_IGNORE_ADMIN_SITE = False
	MAINTENANCE_MODE_IGNORE_AUTHENTICATED_USER = False
	DEBUG = True

	DOMAIN = 'example.com'

	EMAIL_HOST_USER='noreply@example.com'
	EMAIL_HOST_PASSWORD='TOPSECRET'
	EMAIL_USE_TLS = True
	EMAIL_HOST = 'smtp.example.com'
	EMAIL_PORT = 587