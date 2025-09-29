from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY","dev-secret")
DEBUG = os.getenv("DEBUG","1") == "1"
ALLOWED_HOSTS = [h for h in os.getenv("ALLOWED_HOSTS","*").split(",") if h]

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'rest_framework','django_filters','drf_spectacular','corsheaders','django_htmx',
    'catalog','orders','users',
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'core.urls'
TEMPLATES = [{
  'BACKEND':'django.template.backends.django.DjangoTemplates',
  'DIRS':[BASE_DIR/'templates'],
  'APP_DIRS':True,
  'OPTIONS':{'context_processors':[
      'django.template.context_processors.debug',
      'django.template.context_processors.request',
      'django.contrib.auth.context_processors.auth',
      'django.contrib.messages.context_processors.messages'
  ]}
}]
WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "parts",        # tên DB bạn tạo
        "USER": "postgres",        # user (hoặc postgres)
        "PASSWORD": "yeuAnhvcl123@",    # mật khẩu
        "HOST": "localhost",
        "PORT": "5432",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
STATICFILES_DIRS = [BASE_DIR/'static']
REST_FRAMEWORK = {
  'DEFAULT_SCHEMA_CLASS':'drf_spectacular.openapi.AutoSchema',
  'DEFAULT_FILTER_BACKENDS':[
      'django_filters.rest_framework.DjangoFilterBackend',
      'rest_framework.filters.SearchFilter',
      'rest_framework.filters.OrderingFilter'
  ],
  'DEFAULT_AUTHENTICATION_CLASSES':[
      'rest_framework.authentication.SessionAuthentication',
      'rest_framework.authentication.BasicAuthentication',
  ],
  'DEFAULT_PERMISSION_CLASSES':[
      'rest_framework.permissions.AllowAny'
  ]
}
SPECTACULAR_SETTINGS = { 'TITLE':'Parts API','VERSION':'1.0.0' }
CORS_ALLOW_ALL_ORIGINS = True

# === Added: media settings for serving product photos in dev ===
MEDIA_URL = "/data/photos/"
MEDIA_ROOT = BASE_DIR / "data" / "photos"
