"""
    Django settings for SUPPORT_API project.
"""

from datetime import timedelta
from os import environ, path
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = path.join(Path(__file__).resolve().parent.parent.parent, '.env.dev')
load_dotenv(dotenv_path)


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = environ.get('SECRET_KEY')
DEBUG = int(environ.get('DEBUG', default=0))
ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS').split(' ')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_json_api',
    'rest_framework_simplejwt',  # If I wish to use localizations/translations
    'rest_framework.authtoken',  # unnecessary
    'django_filters',  # filters library
    'app_support.apps.AppSupportConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SUPPORT_API.urls'
APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SUPPORT_API.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': environ.get('POSTGRES_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': environ.get('POSTGRES_DB', BASE_DIR / 'db.sqlite3'),
        'USER': environ.get('POSTGRES_USER', 'user'),
        'PASSWORD': environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': environ.get('POSTGRES_PORT', '5432'),
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# no static so far
STATIC_URL = '/static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {  # CFG from rest_framework_json_api DOCs
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',  # because custom permisssion classes are used
    ),
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.TokenAuthentication',  # if DJOSER TOKEN is used
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # this one works w/o downgrade pyjwt

        # if auth via DRF JWT
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication', # need to downgrade pyjwt to 1.7.1

        'rest_framework.authentication.SessionAuthentication',  # optional
        'rest_framework.authentication.BasicAuthentication',  # optional

    ),
    'EXCEPTION_HANDLER': (
        # 'rest_framework_json_api.exceptions.exception_handler', if no custom ex handler
        'app_support.exceptions.custom_exception_handler'  # custom ex handler
    ),
    'DEFAULT_PAGINATION_CLASS':
        # 'rest_framework_json_api.pagination.JsonApiPageNumberPagination',  # default
        'rest_framework_json_api.pagination.PageNumberPagination',  # ('django school' cfg)
    'DEFAULT_PARSER_CLASSES': (
        # 'rest_framework_json_api.parsers.JSONParser',  # optional
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser'  # added for tests (defaul content = multipart/form...)
    ),
    'DEFAULT_RENDERER_CLASSES': (

        'rest_framework_json_api.renderers.JSONRenderer',  # best one
        'rest_framework_json_api.renderers.BrowsableAPIRenderer',  # best one
        # 'rest_framework.renderers.JSONRenderer',  # optional
        # 'rest_framework.renderers.StaticHTMLRenderer',  # optional
    ),
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework_json_api.schemas.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': (
        # 'rest_framework_json_api.filters.QueryParameterValidationFilter',  # optional
        # 'rest_framework_json_api.filters.OrderingFilter',  # optional
        'rest_framework_json_api.django_filters.DjangoFilterBackend',
        # 'rest_framework.filters.SearchFilter',  # optional
    ),
    'SEARCH_PARAM': 'filter[search]',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework_json_api.renderers.JSONRenderer',
        'rest_framework_json_api.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer'
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'vnd.api+json'
}

JWT_AUTH = {  # DRF JWT default settings
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=3000),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,

}

# DJOSER = {  # uncomment if djoser is used
#     # 'SEND_ACTIVATION_EMAIL': True,
#     # 'SEND_CONFIRMATION_EMAIL': True,
#     # 'ACTIVATION_URL': 'auth/activate/{uid}/{token}/',  # этот юрл отправляется пользователю на почту
#     # 'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
#     # 'TOKEN_MODEL': None,  # default = ('rest_framework.authtoken.models.Token')
#     # 'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
#     # 'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
#     # 'ACTIVATION_URL': '#/activate/{uid}/{token}',
#     # 'SERIALIZERS': {
#     #       'user_create': 'app_support.serializers.MyUserCreateSerializer',
#     # },
#     # 'USER_ID_FIELD': (default) User._meta.pk.name,
#     # 'LOGIN_FIELD': (default) User.USERNAME_FIELD,
# }

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=125),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('JWT',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=15),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

AUTH_USER_MODEL = 'app_support.AppUser'  # default User

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_TRANSPORT_OPTION = {'visibility_timeout': 3600}
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

APP_SUPPORT_DEFAULTS = {
    'TICKETS_COLLECTOR_NAME': environ.get('TICKETS_COLLECTOR_USERNAME', 'tcollector'),
}
