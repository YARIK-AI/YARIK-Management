# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from pathlib import Path
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


try:
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError as e:
    raise RuntimeError("Could not find a SECRET_KEY in environment") from e

# SECRET_KEY = \
#    'fwgwqegwwerohj30954hju3jh0q3rj0gq34h9j3q49jh-3q9j4h-9y4q30-jhq-j-q34j3qj4hgw4erhg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get("DEBUG", default=0)))

GIT_URL = os.environ.get("GIT_URL")

# GIT_URL = "http://gitbucket-int:8080/gitbucket/root/configs/blob/master/"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "https://localhost").split(" ")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.config_management",
    "apps.authentication",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATE_DIR = BASE_DIR / "apps/templates"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.context_processors.cfg_assets_root",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# ldap config
# ldap uri
# AUTH_LDAP_SERVER_URI = "ldap://ldap-srv-svc.default.svc.cluster.local:3893"
AUTH_LDAP_SERVER_URI = os.environ["LDAP_URI"]

# bind parameters
# AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_DN = os.environ.get("LDAP_BIND_DN", default="cn=admin,dc=example,dc=com")
# AUTH_LDAP_BIND_PASSWORD = "admin"
AUTH_LDAP_BIND_PASSWORD = os.environ["LDAP_PSWD"]

# search config "ou=users,dc=example,dc=com"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.environ["LDAP_USER_BASE_DN"], ldap.SCOPE_SUBTREE, "(uid=%(user)s)"
)

AUTH_LDAP_MIRROR_GROUPS = True

# group search config "ou=users,dc=example,dc=com"
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    os.environ["LDAP_GROUP_BASE_DN"],
    ldap.SCOPE_SUBTREE,
    "(objectClass=posixGroup)",
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

"""
#AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=django,ou=groups,dc=example,dc=com"
#AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"
"""

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

"""
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=active,ou=django,ou=groups,dc=example,dc=com",
    "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
    "is_superuser": "cn=superuser,ou=django,ou=groups,dc=example,dc=com",
}"""

AUTH_LDAP_ALWAYS_UPDATE_USER = True

AUTH_LDAP_FIND_GROUP_PERMS = True

AUTH_LDAP_CACHE_TIMEOUT = 1800

# ldap backends
AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
]


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "artifacts": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {"options": "-c search_path=artifacts"},
        "NAME": "postgres",
        "USER": "admin",
        "PASSWORD": "psltest",
        "HOST": "postgres.default.svc.cluster.local",
        "PORT": "3239",
    },
}


DATABASE_ROUTERS = (
    "apps.config_management.dbrouters.ModulesDBRouter",
    "apps.config_management.dbrouters.ComponentsDBRouter",
    "apps.config_management.dbrouters.ApplicationsDBRouter",
    "apps.config_management.dbrouters.InstancesDBRouter",
    "apps.config_management.dbrouters.FilesDBRouter",
    "apps.config_management.dbrouters.ParametersDBRouter",
)


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "static/"

STATICFILES_DIRS = (
    BASE_DIR / "apps/static/",
)

# Assets Management
ASSETS_ROOT = '/static/assets'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 30 * 60


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            'formatter': 'verbose',
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}