from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-62*#4*q8y*ir$e6h!&%ww+51lzl0rh%mo*47--&p$*24e#0*sc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.pythonanywhere.com', 'girlhub.onrender.com']

# Регистрация!!!

ACCOUNT_EMAIL_REQUIRED = True              # Требование email при регистрации
ACCOUNT_EMAIL_VERIFICATION = "none"        # Отключить подтверждение по email
ACCOUNT_USERNAME_REQUIRED = True           # Требование имени пользователя
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False  # Убрать необходимость повтора пароля
ACCOUNT_AUTHENTICATION_METHOD = 'email' # Аутентификация только по имени пользователя

LOGIN_REDIRECT_URL = '/home'  # Путь для перенаправления после успешного входа
ACCOUNT_SIGNUP_REDIRECT_URL = '/home'  # Путь для перенаправления после успешной регистрации
LOGOUT_REDIRECT_URL = '/home'  # Перенаправление на главную страницу после выхода

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

USE_TZ = True
TIME_ZONE = 'UTC' # Чтобы избежать проблем с записью временных меток в БД!

# Application definition
INSTALLED_APPS = [
    # Базовые приложения Django
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',


    # Приложения для allauth
    'allauth',
    'allauth.account',

    # Ваше основное приложение
    'home',
]

SITE_ID = 1

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
)

ROOT_URLCONF = 'GirlHub.urls'

# Specify the context processors as follows:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'home/templates'], # путь к пользовательским шаблонам
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Это нужно для allauth
                'django.contrib.auth.context_processors.auth',  # Требуется для админки
                'django.contrib.messages.context_processors.messages',  # Требуется для админки
            ],
        },
    },
]

WSGI_APPLICATION = 'GirlHub.wsgi.application'

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

AUTHENTICATION_BACKENDS = [
    # Needed to log in by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

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

USE_I18N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Лимиты на обращения пользователей к серверу

ACCOUNT_RATE_LIMITS = {
    # Лимит на запросы на вход в аккаунт
    "login": "10/m",  # До 10 запросов в минуту

    # Лимит на запросы на сброс пароля
    "reset_password": "5/m",  # До 5 запросов в минуту

    # Лимит на подтверждение почты
    "verify_email": "5/m",  # До 5 запросов в минуту

    # Лимит для подтверждения/восстановления входа
    "email_verification": "20/h",  # До 20 запросов в час

    # Лимит на регистрацию
    "signup": "5/m",  # До 3 запросов в минуту
}
