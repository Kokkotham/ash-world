import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=''):
    return os.environ.get(name, default)


SECRET_KEY = env('DJANGO_SECRET_KEY', 'local-dev-only-secret-key')
DEBUG = env('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = [host.strip() for host in env('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.common',
    'apps.rules',
    'apps.glossary',
    'apps.importer',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('MYSQL_DATABASE', 'embers_world'),
        'USER': env('MYSQL_USER', 'embers_user'),
        'PASSWORD': env('MYSQL_PASSWORD', 'embers_password'),
        'HOST': env('MYSQL_HOST', '127.0.0.1'),
        'PORT': env('MYSQL_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in env('DJANGO_CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    if origin.strip()
]

SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['规则管理', '术语管理', '认证与权限'],
    'dynamic': False,
    'menus': [
        {
            'name': '规则管理',
            'icon': 'fas fa-book',
            'models': [
                {'name': '规则分类', 'url': 'rules/rulecategory/'},
                {'name': '规则条目', 'url': 'rules/rule/'},
            ],
        },
        {
            'name': '术语管理',
            'icon': 'fas fa-tags',
            'models': [
                {'name': '术语词条', 'url': 'glossary/glossaryterm/'},
            ],
        },
        {
            'name': '认证与权限',
            'icon': 'fas fa-user-shield',
            'models': [
                {'name': '用户', 'url': 'auth/user/'},
                {'name': '用户组', 'url': 'auth/group/'},
            ],
        },
    ],
}
