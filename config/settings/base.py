"""Django base settings for enterprise RAG knowledge base."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.rag',
    'apps.ingestion',
    'apps.knowledge',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'app.db',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── RAG 配置 ──────────────────────────────────────────
RAG_CONFIG = {
    'default_top_k': int(os.environ.get('RAG_DEFAULT_TOP_K', 8)),
    'max_context_chars': int(os.environ.get('RAG_MAX_CONTEXT_CHARS', 12000)),
    'chunk_size': int(os.environ.get('RAG_CHUNK_SIZE', 800)),
    'chunk_overlap': int(os.environ.get('RAG_CHUNK_OVERLAP', 120)),
}

# ── MiniMax 配置 (仅 Chat) ────────────────────────────
MINIMAX_CONFIG = {
    'api_key': os.environ.get('MINIMAX_API_KEY', ''),
    'base_url': os.environ.get('MINIMAX_BASE_URL', 'https://api.minimax.chat'),
    'chat_model': os.environ.get('MINIMAX_CHAT_MODEL', ''),
}

# ── Embedding 配置 (本地 sentence-transformers) ────────
EMBEDDING_CONFIG = {
    'model_name': os.environ.get('EMBEDDING_MODEL', 'BAAI/bge-small-zh-v1.5'),
}

# ── Chroma 配置 ───────────────────────────────────────
CHROMA_CONFIG = {
    'mode': os.environ.get('CHROMA_MODE', 'persistent'),
    'persist_dir': os.environ.get('CHROMA_PERSIST_DIR', str(BASE_DIR / 'data' / 'chroma')),
    'host': os.environ.get('CHROMA_HOST', 'localhost'),
    'port': int(os.environ.get('CHROMA_PORT', 8000)),
}

# ── 存储配置 ──────────────────────────────────────────
STORAGE_DIR = os.environ.get('STORAGE_DIR', str(BASE_DIR / 'data' / 'raw'))

# ── 日志 ───────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
}
