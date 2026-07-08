import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()
from django.utils.translation import gettext_lazy as _
from corsheaders.defaults import default_headers
import firebase_admin
from firebase_admin import credentials
BASE_DIR = Path(__file__).resolve().parent.parent

cred_path = os.path.join(BASE_DIR, "firebase-key.json")
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
else:
    print(f"Warning: Firebase certificate not found at {cred_path}")

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
DATA_UPLOAD_MAX_MEMORY_SIZE = 1048576
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
CORS_ALLOW_HEADERS = list(default_headers) + ['ngrok-skip-browser-warning',]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://localhost:3000',
    'https://*.ngrok-free.dev',
    'http://*.ngrok-free.dev',
]


INSTALLED_APPS = [
    'modeltranslation',
    'unfold',
    'django.forms',
    'channels',
    'corsheaders',
    'rosetta',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'rest_framework_simplejwt',
    'drf_yasg',
    'authentication',
    'subscription',
    'payment',
    'product',
    'order',
    'other',
    'notify',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LANGUAGE_CODE = 'hr'

LANGUAGES = [
    ('hr', _('Croatian')),
    ('en', _('English')),
]

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

if os.getenv("USE_PSQL", "False") == "True":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv("DB_NAME"),
            'USER': os.getenv("DB_USER"),
            'PASSWORD': os.getenv("DB_PASSWORD"),
            'HOST': os.getenv("DB_HOST"),
            'PORT': os.getenv("DB_PORT"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
}


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

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = "authentication.User"
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Zagreb'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static",]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        'rest_framework.filters.OrderingFilter',
        ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': None,
    }


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30)
}


EMAIL_BACKEND = 'config.email_backend.BrevoEmailBackend'
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Varivo")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", os.getenv("DEFAULT_FROM_EMAIL"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_TIMEOUT = 15


CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Type in the *Value* input box below: **Bearer &lt;JWT&gt;**, where JWT is the token'
        }
    },
    'USE_SESSION_AUTH': True,
    'LOGIN_URL': '/api-auth/login/',
    'LOGOUT_URL': '/api-auth/logout/',
}


UNFOLD = {
    "SITE_TITLE": "Varivo Admin",
    "SITE_HEADER": "Varivo Control Center",
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "255 247 237",
            "100": "255 237 213",
            "200": "254 215 170",
            "300": "253 186 116",
            "400": "251 146 60",
            "500": "249 115 22",
            "600": "234 88 12",
            "700": "194 65 12",
            "800": "154 52 18",
            "900": "124 45 18",
            "950": "67 20 7",
        },
    },
    "DASHBOARD_CALLBACK": "config.admin.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Business Overview"),
                "separator": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": _("Core Management"),
                "separator": True,
                "items": [
                    {
                        "title": _("User Base"),
                        "icon": "group",
                        "link": "/admin/authentication/user/",
                    },
                    {
                        "title": _("Order History"),
                        "icon": "shopping_cart",
                        "link": "/admin/order/order/",
                    },
                    {
                        "title": _("Coupons"),
                        "icon": "confirmation_number",
                        "link": "/admin/order/coupon/",
                    },
                ],
            },
            {
                "title": _("Inventory"),
                "separator": True,
                "items": [
                    {
                        "title": _("Food Items"),
                        "icon": "restaurant",
                        "link": "/admin/product/fooditem/",
                    },
                    {
                        "title": _("Daily Menu"),
                        "icon": "menu_book",
                        "link": "/admin/product/menu/",
                    },
                ],
            },
            {
                "title": _("System"),
                "separator": True,
                "items": [
                    {
                        "title": _("Activity Log"),
                        "icon": "history",
                        "link": "/admin/activity-log/",
                    },
                ],
            },
        ],
    },
}

# Firebase Web App Configuration
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")
FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID", "")
FIREBASE_MEASUREMENT_ID = os.getenv("FIREBASE_MEASUREMENT_ID", "")
FIREBASE_VAPID_KEY = os.getenv("FIREBASE_VAPID_KEY", "")
