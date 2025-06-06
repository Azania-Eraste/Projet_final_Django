"""
Django settings for projet_final project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'Authentification.CustomUser'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-hq5*wx=opkt-zh_b+dy0b8s&k5dai-fw-8@g4#-eks$*$hjb2_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django_ckeditor_5',
    'filebrowser', 
    'jazzmin',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'drf_yasg',
    'mathfilters',
    'django_filters',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'blog.apps.BlogConfig',
    'Authentification.apps.AuthentificationConfig',
    'Ecommerce.apps.EcommerceConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'projet_final.urls'

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

WSGI_APPLICATION = 'projet_final.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FILEBROWSER_DIRECTORY = ''  
FILEBROWSER_EXTENSIONS = {
    'Image': ['.jpg', '.jpeg', '.png', '.gif'],
    'Document': ['.pdf', '.docx', '.txt'],
}
FILEBROWSER_VERSIONS_BASEDIR = '_versions'
FILEBROWSER_ADMIN_THUMBNAIL = 'admin_thumbnail'

TINYMCE_DEFAULT_CONFIG = {
    'height': 600,
    'width': 900,
    'menubar': True,
    'plugins': 'advlist autolink lists link image charmap print preview anchor '
               'searchreplace visualblocks code fullscreen '
               'insertdatetime media table paste code help wordcount',
    'toolbar': 'undo redo | formatselect | bold italic backcolor | '
               'alignleft aligncenter alignright alignjustify | '
               'bullist numlist outdent indent | removeformat | help',
    'content_css': '/static/css/custom_tinymce.css',  # Optionnel : personnalisation du style
}

customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': ['heading', '|', 'bold', 'italic', 'link',
                      'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
        }
    },
    'extends': {
        'toolbar': {
            'items': ['heading', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                      'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 
                      'sourceEditing', 'insertImage', 'bulletedList', 'numberedList', 
                      'todoList', '|', 'blockQuote', 'imageUpload', '|',
                      'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 
                      'mediaEmbed', 'removeFormat', 'insertTable'],
            'shouldNotGroupWhenFull': True
        },
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': ['full', 'side', 'alignLeft', 'alignRight', 'alignCenter']
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
            'tableProperties': {'borderColors': customColorPalette, 'backgroundColors': customColorPalette},
            'tableCellProperties': {'borderColors': customColorPalette, 'backgroundColors': customColorPalette}
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        },
        'language': 'fr',
    }
}

# Permission pour l'upload des fichiers
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"  # Possible: "staff", "authenticated", "any"


#auth google
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Configuration du domaine de l'application
SITE_ID = 1
SITE_URL = "http://127.0.0.1:8000/"
SITE_PROTOCOL = ""

# Rediriger après une connexion réussie
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Pour le compte utilisateur
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_EMAIL_VERIFICATION = "optional" # Si tu veux désactiver la vérification par email
ACCOUNT_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True

# Configuration de Google OAuth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'ton-client-id-google'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'ton-client-secret-google'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'VOTRE_CLIENT_ID',
            'secret': 'VOTRE_SECRET_CLIENT',
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}


#Smtp

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Utiliser le serveur SMTP de votre fournisseur
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER =  "kouadioazania@gmail.com"
EMAIL_HOST_PASSWORD = 'oxxz hmvh aqfz qpbo'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER



#REST framework

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
}


# Récupérer les clés API de Stripe depuis les variables d'environnement
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

