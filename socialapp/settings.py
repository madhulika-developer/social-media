"""
Django settings for socialapp project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key: use environment variable in production, fallback for local dev
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-social-media-app-secret-key-change-in-production'
)

# Debug: set to False in production unless DEBUG=True is explicitly passed
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Allowed Hosts: allow render.com subdomains and local dev hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

# Conditionally use WhiteNoise if available (installed on Render)
try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass

MIDDLEWARE.extend([
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

ROOT_URLCONF = 'socialapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'socialapp.wsgi.application'

# Database
# Uses DATABASE_URL if provided (e.g. Render Postgres), otherwise fallback to local SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

try:
    import dj_database_url
    if 'DATABASE_URL' in os.environ:
        DATABASES['default'] = dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
except ImportError:
    pass

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'feed'
LOGOUT_REDIRECT_URL = 'login'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
