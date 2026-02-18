from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
#  SECURITY SETTINGS
# =========================================================

# ### CHANGE THIS ### to a random string for production security
SECRET_KEY = 'cn=^s*#7!x9)2@v_l4(z-5$q&1+8%k0m3^j6(d#g9!r5$y2@t1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allow all IPs (useful for internal windows servers). 
# You can replace '*' with specific IPs like ['192.168.1.5', 'localhost']
ALLOWED_HOSTS = ['rebootready.co.za', 'www.rebootready.co.za', 'localhost', '127.0.0.1', '[102.218.215.238]']

CSRF_TRUSTED_ORIGINS = [
    'https://rebootready.co.za', 
    'https://www.rebootready.co.za',
    'http://rebootready.co.za',      # Keep http for testing until SSL is active
]


# =========================================================
#  APPLICATION DEFINITION
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party Apps
    'crispy_forms',
    'crispy_bootstrap5',
    'import_export',

    # Custom Apps
    'users.apps.UsersConfig',
    'courses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be listed directly after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# =========================================================
#  DATABASE (PostgreSQL)
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rebootready_db',       # Must match DB name in pgAdmin
        'USER': 'reboot_user',          # Must match User in pgAdmin
        'PASSWORD': 'Mortal@reboot@6678', # ### CHANGE THIS ### to your actual password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# =========================================================
#  PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# =========================================================
#  INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Johannesburg'
USE_I18N = True
USE_TZ = True


# =========================================================
#  STATIC & MEDIA FILES (WhiteNoise Config)
# =========================================================

STATIC_URL = 'static/'
# This is where collectstatic will gather files for WhiteNoise to serve
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [BASE_DIR / "static"]

# Enable WhiteNoise compression and caching support
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files (User Uploads - Profile Pics, Word Docs)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# =========================================================
#  APP CONFIGURATION
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Redirects
LOGIN_REDIRECT_URL = 'lecture_list'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'


# =========================================================
#  EMAIL SETTINGS (SMTP)
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'dillonkevin46@gmail.com' 
# PASTE THE 16-CHAR APP PASSWORD HERE
EMAIL_HOST_PASSWORD = 'aivw udgc krrt sptb'  

DEFAULT_FROM_EMAIL = 'RebootReady LMS <noreply@rebootready.com>'

# ... (existing code) ...

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ... (at the very bottom of the file)

# Increase Limit to 25MB
# Calculation: 25 * 1024 * 1024 = 26,214,400 bytes
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400